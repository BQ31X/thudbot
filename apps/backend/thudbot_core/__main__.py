import uvicorn
from thudbot_core.config import load_env

if __name__ == "__main__":
    load_env()  # Load .env variables before starting
    uvicorn.run("thudbot_core.api:app", host="0.0.0.0", port=8000, reload=True)
