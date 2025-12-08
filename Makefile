# === Config ===

# Your Linode login info
LINODE_USER = bq
LINODE_HOST = 45.33.65.116

# Remote path on Linode where compose file is deployed (file-only, no repo)
REMOTE_DIR = ~/thudbot

# Path to compose file relative to this Makefile (Mac/local path)
COMPOSE_FILE = infra/compose.prod.yml

# Just the filename (for remote use)
COMPOSE_FILENAME = compose.prod.yml

# Docker stack name (on Linode)
STACK_NAME = thudbot-prod

# Path to local Qdrant collection
QDRANT_LOCAL = apps/backend/qdrant_db

# Staging path on Linode (temporary, before copying to Docker volume)
QDRANT_STAGING = ~/qdrant_db

# === Targets ===

# Declare non-file targets (prevents filename collision issues)
.PHONY: help deploy-prod deploy-all push-compose ssh-deploy logs logs-frontend remove
.PHONY: deploy-qdrant push-qdrant update-qdrant restart-backend

# 📖 Show available commands
help:
	@echo "Available commands:"
	@echo "  make deploy-prod     - Deploy code changes (compose + images)"
	@echo "  make deploy-qdrant   - Deploy Qdrant collection updates"
	@echo "  make deploy-all      - Deploy both code and data"
	@echo "  make logs            - View backend logs"
	@echo "  make logs-frontend   - View frontend logs"
	@echo "  make remove          - Remove the stack"
	@echo ""
	@echo "Individual Qdrant steps:"
	@echo "  make push-qdrant     - Transfer collection to Linode"
	@echo "  make update-qdrant   - Update Docker volume"
	@echo "  make restart-backend - Restart backend service"

# 🟢 Full deployment pipeline: scp + ssh deploy
deploy-prod: push-compose ssh-deploy

# 🚀 Full deployment: code + data (use when both changed)
deploy-all: deploy-prod deploy-qdrant
	@echo ""
	@echo "🎉 Full deployment complete!"
	@echo "📋 Monitor with: make logs"

# 📤 Push updated compose file to Linode
push-compose:
	scp $(COMPOSE_FILE) $(LINODE_USER)@$(LINODE_HOST):$(REMOTE_DIR)/

# 🚀 SSH into Linode and redeploy the stack
ssh-deploy:
	ssh $(LINODE_USER)@$(LINODE_HOST) 'cd $(REMOTE_DIR) && docker stack deploy -c $(COMPOSE_FILENAME) $(STACK_NAME)'

# 📄 Show backend logs
logs:
	ssh $(LINODE_USER)@$(LINODE_HOST) 'docker service logs $(STACK_NAME)_backend --tail=50'

# 📄 Show frontend logs
logs-frontend:
	ssh $(LINODE_USER)@$(LINODE_HOST) 'docker service logs $(STACK_NAME)_frontend --tail=50'

# === Qdrant Collection Management ===

# 🗄️  Deploy Qdrant collection to production
deploy-qdrant: push-qdrant update-qdrant restart-backend

# 📤 Transfer Qdrant collection to Linode
push-qdrant:
	@echo "📤 Transferring Qdrant collection to Linode..."
	scp -r $(QDRANT_LOCAL) $(LINODE_USER)@$(LINODE_HOST):$(QDRANT_STAGING)
	@echo "✅ Transfer complete"

# 🔄 Update Qdrant volume and cleanup
update-qdrant:
	@echo "🔄 Updating Qdrant Docker volume..."
	ssh $(LINODE_USER)@$(LINODE_HOST) '\
		docker run --rm \
			-v qdrant_data:/dst \
			-v $(QDRANT_STAGING):/src \
			busybox cp -r /src/. /dst/ && \
		rm -rf $(QDRANT_STAGING) \
	'
	@echo "✅ Volume updated and staging files cleaned"

# 🔄 Restart backend to load new collection
restart-backend:
	@echo "🔄 Restarting backend service..."
	ssh $(LINODE_USER)@$(LINODE_HOST) 'docker service update --force $(STACK_NAME)_backend'
	@echo "✅ Backend restarting..."
	@echo ""
	@echo "📋 Monitor with: make logs"

# ❌ Tear down the running stack
remove:
	@echo "⚠️  WARNING: This will remove the PRODUCTION stack ($(STACK_NAME))"
	@echo "Press Ctrl-C to abort..."
	@sleep 5
	ssh $(LINODE_USER)@$(LINODE_HOST) 'docker stack rm $(STACK_NAME)'
