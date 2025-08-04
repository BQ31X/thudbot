from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from .agent import get_thud_agent

# Load environment variables
load_dotenv()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class ChatRequest(BaseModel):
    user_message: str
    api_key: str

@app.post("/api/chat")
async def chat_with_thud(request: ChatRequest):
    try:
        # Set OpenAI API key from request
        os.environ['OPENAI_API_KEY'] = request.api_key
        
        # Get the Thudbot agent and run
        thud_agent = get_thud_agent()
        response = thud_agent.run(request.user_message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
