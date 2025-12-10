# src/__init__.py

# Lazy imports - only import when accessed, not at module load time
# This allows the runtime entry point (__main__.py) to set up sys.path first
def __getattr__(name):
    if name == "get_direct_hint":
        from .agent import get_direct_hint
        return get_direct_hint
    elif name == "initialize_rag_only":
        from .agent import initialize_rag_only
        return initialize_rag_only
    elif name == "app":
        from .api import app
        return app
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = ['get_direct_hint', 'initialize_rag_only', 'app']