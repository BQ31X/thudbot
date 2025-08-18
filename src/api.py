from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from app import run_hint_request

# Load environment variables
load_dotenv()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class ChatRequest(BaseModel):
    user_message: str
    api_key: str = ""  # Optional - will fall back to .env if empty

@app.post("/api/chat")
async def chat_with_thud(request: ChatRequest):
    try:
        # Use API key from request OR fall back to .env
        api_key = request.api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise HTTPException(status_code=400, detail="OpenAI API key required (provide in request or set OPENAI_API_KEY in .env)")
        
        # Set the API key in environment for the LangGraph to use
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
        
        # Use the new LangGraph implementation
        response = run_hint_request(request.user_message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
