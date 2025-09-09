from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
import os
from dotenv import load_dotenv
from thudbot_core.app import run_hint_request, clear_session
from slowapi.errors import RateLimitExceeded
from thudbot_core.rate_limiter import limiter, IP_RATE_LIMIT, GLOBAL_RATE_LIMIT

# Load environment variables
load_dotenv()

app = FastAPI()

# Add rate limiter to app
app.state.limiter = limiter

# Custom rate limit exceeded handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    response = JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded. Please wait before making another request. (Limit: {exc.detail})"}
    )
    return response


# app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
# Environment-based CORS configuration
env = os.getenv("ENV", "dev")  # defaults to "dev" 
if env == "dev":
    # Development: allow localhost
    allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
else:
    # Production: use explicit allowlist
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "https://boffo.games").split(",")

app.add_middleware(
    CORSMiddleware, 
    allow_origins=allowed_origins,
    allow_methods=["POST"],  # Only allow POST (more restrictive)
    allow_headers=["*"]
)

class ChatRequest(BaseModel):
    user_message: str
    session_id: str = "default"  # Session ID for chat history persistence
    
    @field_validator('user_message')
    @classmethod
    def validate_user_message(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        
        if len(v) > 5000:
            raise ValueError("Message too long. Please keep your message under 5000 characters")
        
        return v.strip()

class ClearSessionRequest(BaseModel):
    session_id: str = "default"

@app.post("/api/chat")
@limiter.limit(IP_RATE_LIMIT)
@limiter.limit(GLOBAL_RATE_LIMIT, key_func=lambda request: "global")
async def chat_with_thud(request: Request, chat_user_data: ChatRequest):
    try:
        # Use API key from .env only - no environment pollution
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise HTTPException(status_code=503, detail="Chat service unavailable: Missing API key configuration.")
        
        # Use the new LangGraph implementation with session support
        response = run_hint_request(chat_user_data.user_message, chat_user_data.session_id)
        return {"response": response, "session_id": chat_user_data.session_id}
    except HTTPException:
        # Re-raise HTTPExceptions unchanged (these are intentional API responses)
        raise
    except Exception as e:
        # Log the full error for debugging (you can see this in server logs)
        print(f"🚨 API Error in chat endpoint: {type(e).__name__}: {str(e)}")
        
        # Return user-friendly message without exposing internals
        raise HTTPException(
            status_code=500, 
            detail="I'm experiencing technical difficulties. Please try again."
        )

@app.post("/api/clear-session")
async def clear_chat_session(request: ClearSessionRequest):
    """Clear a specific session's chat history and reset hint levels"""
    try:
        cleared = clear_session(request.session_id)
        if cleared:
            return {"message": f"Session {request.session_id} cleared successfully"}
        else:
            return {"message": f"Session {request.session_id} not found (may already be empty)"}
    except Exception as e:
        # Log the full error for debugging (you can see this in server logs)
        print(f"🚨 API Error in clear-session endpoint: {type(e).__name__}: {str(e)}")
        
        # Return user-friendly message without exposing internals
        raise HTTPException(
            status_code=500, 
            detail="Unable to clear session. Please try again."
        )
# This module is not intended to be run directly.
# Use `python -m thudbot_core` instead.

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
