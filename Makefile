# === Config ===
# -----------------------------------------------------------------------------
# Global image build policy
# -----------------------------------------------------------------------------
REGISTRY        ?= bq31
BUILD_DATE_UTC  ?= $(shell date -u +%Y-%m-%d)
VERSION_SUFFIX  ?= $(BUILD_DATE_UTC)

# =============================================================================
# Service image names
# =============================================================================
BACKEND_IMAGE   ?= $(REGISTRY)/thudbot-backend
RETRIEVAL_IMAGE ?= $(REGISTRY)/thudbot-retrieval
FRONTEND_IMAGE  ?= $(REGISTRY)/thudbot-frontend

# =============================================================================
# Service version labels
# =============================================================================
BACKEND_VERSION   ?= backend-$(VERSION_SUFFIX)
RETRIEVAL_VERSION ?= retrieval-api-$(VERSION_SUFFIX)
FRONTEND_VERSION  ?= frontend-$(VERSION_SUFFIX)

# =============================================================================
# Deployment / infrastructure configuration
# =============================================================================
# NOTE:
# - App node uses Docker Swarm (stateful, secrets, long-lived services)
# - Retrieval node uses docker compose (stateless, compute-focused)

# App node (primary, secrets, swarm leader)
APP_LINODE_USER ?= bq
APP_LINODE_HOST ?= 45.33.65.116

# Retrieval node (Qdrant + retrieval API + local embeddings)
RETRIEVAL_LINODE_USER ?= bq
RETRIEVAL_LINODE_HOST ?= 45.79.143.75

# -----------------------------------------------------------------------------
# App node compose configuration (Swarm)
# -----------------------------------------------------------------------------
REMOTE_DIR ?= ~/thudbot
COMPOSE_FILE ?= infra/compose.prod.app.yml
COMPOSE_FILENAME ?= compose.prod.app.yml
STACK_NAME ?= thudbot-prod

# -----------------------------------------------------------------------------
# Retrieval node compose configuration (docker compose)
# -----------------------------------------------------------------------------
RETRIEVAL_REMOTE_DIR ?= ~/thudbot
RETRIEVAL_COMPOSE_FILE ?= infra/compose.prod.retrieval.yml
RETRIEVAL_COMPOSE_FILENAME ?= compose.prod.retrieval.yml

# These are now obsolete with the new retrieval node and will be removed in the near future
# Path to local Qdrant collection
# QDRANT_LOCAL = apps/backend/qdrant_db

# Staging path on Linode (temporary, before copying to Docker volume)
# QDRANT_STAGING = ~/qdrant_db

# === Targets ===

# Declare non-file targets (prevents filename collision issues)
.PHONY: \
	help \
	build-all build-backend build-frontend build-retrieval inspect-images \
	deploy-prod deploy-all push-compose ssh-deploy \
	deploy-retrieval push-compose-retrieval ssh-deploy-retrieval \
	logs logs-frontend logs-retrieval logs-qdrant \
	version version-frontend version-backend version-retrieval \
	restart-backend restart-retrieval restart-retrieval-stack stop-retrieval \
	remove
	
# 📖 Show available commands
help:
	@echo "Build commands:"
	@echo "  make build-backend    - Build and push backend image"
	@echo "  make build-frontend   - Build and push frontend image"
	@echo "  make build-retrieval  - Build and push retrieval image"
	@echo "  make build-all        - Build and push all images"
	@echo "  make inspect-images   - Verify multi-arch images"
	@echo ""
	@echo "Deploy commands (two-node architecture):"
	@echo "  make deploy-prod      - Deploy app node (backend + frontend + redis)"
	@echo "  make deploy-retrieval - Apply retrieval compose (recreate retrieval; qdrant unchanged)"
	@echo "  make deploy-all       - Deploy both nodes (retrieval first, then app)"
	@echo ""
	@echo "Monitoring - App node:"
	@echo "  make logs             - View backend logs (app node)"
	@echo "  make logs-frontend    - View frontend logs (app node)"
	@echo ""
	@echo "Monitoring - Retrieval node:"
	@echo "  make logs-retrieval   - View retrieval service logs"
	@echo "  make logs-qdrant      - View qdrant logs"
	@echo ""
	@echo "Version checks:"
	@echo "  make version           - Check all service versions in production"
	@echo "  make version-frontend  - Check frontend version"
	@echo "  make version-backend   - Check backend version"
	@echo "  make version-retrieval - Check retrieval version"
	@echo ""
	@echo "Operations:"
	@echo "  make restart-backend          - Restart backend service (app node)"
	@echo "  make restart-retrieval        - Restart retrieval service only"
	@echo "  make restart-retrieval-stack  - Restart qdrant + retrieval (after data promotion)"
	@echo "  make stop-retrieval           - Stop retrieval stack"
	@echo ""
	@echo "Destructive:"
	@echo "  make remove                   - Remove app stack (swarm)"

# NOTE: Internal targets (push-compose, ssh-deploy, push-compose-retrieval, 
# ssh-deploy-retrieval) are intentionally hidden from help - they are
# implementation details called by the high-level deploy targets above.

# === Docker Image Build Targets ===

# 🏗️  Build and push all images
build-all: build-backend build-frontend build-retrieval

# 🐍 Build and push backend image
build-backend:
	@echo "🏗️  Building and pushing backend image (multi-arch)..."
	docker buildx build --platform linux/amd64,linux/arm64 \
		-t $(BACKEND_IMAGE):latest \
		-t $(BACKEND_IMAGE):$(BACKEND_VERSION) \
		--push \
		apps/backend/
	@echo "✅ Backend image pushed to Docker Hub"

# ⚛️  Build and push frontend image
build-frontend:
	@echo "🏗️  Building and pushing frontend image (multi-arch)..."
	docker buildx build --platform linux/amd64,linux/arm64 \
		-t $(FRONTEND_IMAGE):latest \
		-t $(FRONTEND_IMAGE):$(FRONTEND_VERSION) \
		--push \
		apps/frontend/
	@echo "✅ Frontend image pushed to Docker Hub"

build-retrieval:
	@echo "🏗️  Building and pushing retrieval image (multi-arch)..."
	docker buildx build --platform linux/amd64,linux/arm64 \
		-t $(RETRIEVAL_IMAGE):latest \
		-t $(RETRIEVAL_IMAGE):$(RETRIEVAL_VERSION) \
		-f apps/retrieval/Dockerfile \
		--push \
		.
	@echo "✅ Retrieval image pushed to Docker Hub"

# 🔍 Verify multi-arch images
inspect-images:
	@echo "🔍 Backend image:"
	@docker buildx imagetools inspect $(BACKEND_IMAGE):latest
	@echo ""
	@echo "🔍 Frontend image:"
	@docker buildx imagetools inspect $(FRONTEND_IMAGE):latest
	@echo ""
	@echo "🔍 Retrieval image:"
	@docker buildx imagetools inspect $(RETRIEVAL_IMAGE):latest

# === Deployment Targets ===

# 🟢 Full deployment pipeline: scp + ssh deploy
# 🟢 App-node deployment pipeline (compose + swarm redeploy; backend + frontend + redis on app node)
deploy-prod: push-compose ssh-deploy

# 🚀 Full deployment: both nodes (app + retrieval)
deploy-all: deploy-retrieval deploy-prod
	@echo ""
	@echo "🎉 Full deployment complete!"
	@echo "📋 Monitor with: make logs (app) or make logs-retrieval (retrieval)"

# 📤 Push updated compose file to app node
push-compose:
	scp $(COMPOSE_FILE) $(APP_LINODE_USER)@$(APP_LINODE_HOST):$(REMOTE_DIR)/

# 🚀 SSH into app node and redeploy the stack
ssh-deploy:
	ssh $(APP_LINODE_USER)@$(APP_LINODE_HOST) 'cd $(REMOTE_DIR) && docker stack deploy -c $(COMPOSE_FILENAME) $(STACK_NAME)'

# 📄 Show backend logs
logs:
	ssh $(APP_LINODE_USER)@$(APP_LINODE_HOST) 'docker service logs $(STACK_NAME)_backend --tail=50'

# 📄 Show frontend logs
logs-frontend:
	ssh $(APP_LINODE_USER)@$(APP_LINODE_HOST) 'docker service logs $(STACK_NAME)_frontend --tail=50'

# 🔍 Check service versions
version-frontend:
	@echo "Frontend version:"
	@ssh $(APP_LINODE_USER)@$(APP_LINODE_HOST) \
	  "docker ps --filter 'name=thudbot-prod_frontend' --format '{{.Names}}' | head -n 1 | \
	   xargs -I{} docker exec {} wget -qO- http://localhost:3000/api/version"
	@echo

version-backend:
	@echo "Backend version:"
	@ssh $(APP_LINODE_USER)@$(APP_LINODE_HOST) \
	  "docker ps --filter 'name=thudbot-prod_backend' --format '{{.Names}}' | head -n 1 | \
	   xargs -I{} docker exec {} python -c \"import urllib.request; print(urllib.request.urlopen('http://localhost:8000/version').read().decode())\""
	@echo

version-retrieval:
	@echo "Retrieval version:"
	@curl -s http://$(RETRIEVAL_LINODE_HOST):8001/version
	@echo

version: version-frontend version-backend version-retrieval

# === Retrieval Node Deployment ===

# 🟢 Deploy retrieval node (compose qdrant + retrieval service, no swarm)
deploy-retrieval: push-compose-retrieval ssh-deploy-retrieval
	@echo ""
	@echo "✅ Retrieval node deployed!"
	@echo "📋 Monitor with: make logs-retrieval"

# 📤 Push compose file to retrieval node
push-compose-retrieval:
	@echo "📤 Pushing $(RETRIEVAL_COMPOSE_FILENAME) to retrieval node..."
	scp $(RETRIEVAL_COMPOSE_FILE) $(RETRIEVAL_LINODE_USER)@$(RETRIEVAL_LINODE_HOST):$(RETRIEVAL_REMOTE_DIR)/

# 🚀 Deploy retrieval stack via docker compose
ssh-deploy-retrieval:
	@echo "🚀 Deploying retrieval stack..."
	ssh $(RETRIEVAL_LINODE_USER)@$(RETRIEVAL_LINODE_HOST) '\
		cd $(RETRIEVAL_REMOTE_DIR) && \
		docker compose -f $(RETRIEVAL_COMPOSE_FILENAME) pull && \
		docker compose -f $(RETRIEVAL_COMPOSE_FILENAME) up -d --force-recreate'

# 📄 Show retrieval service logs (on retrieval node)
logs-retrieval:
	ssh $(RETRIEVAL_LINODE_USER)@$(RETRIEVAL_LINODE_HOST) 'docker compose -f $(RETRIEVAL_REMOTE_DIR)/$(RETRIEVAL_COMPOSE_FILENAME) logs retrieval --tail=50 -f'

# 📄 Show qdrant logs (on retrieval node)
logs-qdrant:
	ssh $(RETRIEVAL_LINODE_USER)@$(RETRIEVAL_LINODE_HOST) 'docker compose -f $(RETRIEVAL_REMOTE_DIR)/$(RETRIEVAL_COMPOSE_FILENAME) logs qdrant --tail=50 -f'

# 🔄 Restart retrieval service only
restart-retrieval:
	@echo "🔄 Restarting retrieval service..."
	ssh $(RETRIEVAL_LINODE_USER)@$(RETRIEVAL_LINODE_HOST) '\
		cd $(RETRIEVAL_REMOTE_DIR) && \
		docker compose -f $(RETRIEVAL_COMPOSE_FILENAME) restart retrieval'

# 🔄 Restart both Qdrant and retrieval (required after collection promotion)
restart-retrieval-stack:
	@echo "🔄 Restarting Qdrant and retrieval (required after collection promotion)..."
	ssh $(RETRIEVAL_LINODE_USER)@$(RETRIEVAL_LINODE_HOST) '\
		cd $(RETRIEVAL_REMOTE_DIR) && \
		docker compose -f $(RETRIEVAL_COMPOSE_FILENAME) restart qdrant retrieval'

# ❌ Stop retrieval stack
stop-retrieval:
	@echo "⚠️  Stopping retrieval stack..."
	ssh $(RETRIEVAL_LINODE_USER)@$(RETRIEVAL_LINODE_HOST) 'docker compose -f $(RETRIEVAL_REMOTE_DIR)/$(RETRIEVAL_COMPOSE_FILENAME) down'


# === Qdrant Collection Management ===

# These are now obsolete with the new retrieval node and will be removed in the near future
# # 🗄️  Deploy Qdrant collection to production
# deploy-qdrant: push-qdrant update-qdrant restart-backend

# # 📤 Transfer Qdrant collection to retrieval node
# push-qdrant:
# 	@echo "📤 Transferring Qdrant collection to retrieval node..."
# 	scp -r $(QDRANT_LOCAL) $(RETRIEVAL_LINODE_USER)@$(RETRIEVAL_LINODE_HOST):$(QDRANT_STAGING)
# 	@echo "✅ Transfer complete"

# # 🔄 Update Qdrant volume and cleanup
# update-qdrant:
# 	@echo "🔄 Updating Qdrant Docker volume on retrieval node..."
# 	ssh $(RETRIEVAL_LINODE_USER)@$(RETRIEVAL_LINODE_HOST) '\
# 		docker run --rm \
# 			-v qdrant_data:/dst \
# 			-v $(QDRANT_STAGING):/src \
# 			busybox cp -r /src/. /dst/ && \
# 		rm -rf $(QDRANT_STAGING) \
# 	'
# 	@echo "✅ Volume updated and staging files cleaned"




# === App Node Operations ===

restart-backend:
	@echo "🔄 Restarting backend service on app node..."
	ssh $(APP_LINODE_USER)@$(APP_LINODE_HOST) \
	  'docker service update --force $(STACK_NAME)_backend'
	@echo "✅ Backend restarting..."
	@echo ""
	@echo "📋 Monitor with: make logs"

# === App Stack Destructive Operations ===

remove:
	@echo "⚠️  WARNING: This will remove the PRODUCTION stack ($(STACK_NAME)) on app node"
	@echo "Press Ctrl-C to abort..."
	@sleep 5
	ssh $(APP_LINODE_USER)@$(APP_LINODE_HOST) \
	  'docker stack rm $(STACK_NAME)'
