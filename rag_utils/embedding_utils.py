# Inside rag_utils, creating embedding_utils.py as a minimal shared embedding helper.
# Do NOT import anything from apps.backend or thudbot_core.
# Use only the OpenAI embeddings client.

# This file should contain:

# - get_embedding_function(model_name: str)
# - embed_text(text: str, model_name: str)
# - embed_batch(texts: List[str], model_name: str)
