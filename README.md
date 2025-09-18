# 🍺 Thudbot - The Space Bar AI Assistant

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue.svg" alt="Python 3.12+"/>
  <img src="https://img.shields.io/badge/FastAPI-0.109.2-green.svg" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Next.js-14+-black.svg" alt="Next.js"/>
  <img src="https://img.shields.io/badge/LangGraph-🧭-indigo.svg" alt="LangGraph"/>

</p>

An intelligent AI assistant for **The Space Bar** adventure game that provides contextual hints.

## Quick Start

1. 🎬 **Watch the video** to get oriented to Thudbot
    
2. 🧪 **Try out Thudbot locally**
    
    1. Follow the [Quick Start](#-quick-start) steps below
        
    2. Try these [Example Questions](#-testing-thudbot) 
        
## 🚀 Project Overview

**Thudbot** is an AI-powered player companion for _The Space Bar_, a cult-classic adventure game from legendary game designer Steve Meretzky.

It provides contextual, spoiler-sensitive hints through an immersive, in-universe interface: the player’s Personal Digital Assistant (PDA), Zelda.

Designed as a standalone web tool, Thudbot keeps you grounded in the game world—even when you need help solving its trickiest puzzles.

Built with LangGraph, FastAPI, and Next.js, Thudbot is a stepping stone toward fully agentic NPCs for the Boffo Games universe.

## 🎬 Demo Video

**[Watch the 2min Demo Video](https://www.loom.com/share/e528242bce8a4b86be393f35b7d45e10)**

*See Thudbot in action*

## 🧪 Testing Thudbot

**Not familiar with "The Space Bar" game? No problem!** Here are ready-to-test examples:

### **Game Hint Examples** (Tests RAG system)
```
Q: "Where is the bus token?"
Expected: Thud explains it's in a cup, with character-specific advice

Q: "How do I get the token from the cup?" 
Expected: Step-by-step hint about asking Thud for help or looking carefully

Q: "When does the shuttle to Karkas 4 leave?"
Expected: Specific time (22:50) with character commentary about checking monitors
```




## ✨ Features

- **🎮 Game Hint System**: RAG-powered hints for The Space Bar adventure game puzzles
- **🛡️ Robust Error Handling**: Graceful error recovery
- **🌐 Web Interface**: Next.js frontend
- **⚡ FastAPI Backend**: High-performance Python API server
- **🧪 Comprehensive Testing**: Robust test suite

## ⚡ Quick Start

### 🐳 **Fastest Way: Docker Compose**

```bash
# Clone the repo
git clone https://github.com/BQ31X/thudbot.git
cd thudbot

# Add your API keys to .env (copy from .env.example)
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# Start everything with Docker
cd infra
docker compose up --build

# ✨ Thudbot backend now at: http://localhost:8000
```

### 📦 **Traditional Setup**

### Prerequisites

- Python 3.13+
- Node.js 20+

### 1. Environment Setup

```bash
# 📦 Clone the repo
git clone https://github.com/BQ31X/thudbot.git
cd thudbot


# Install Python dependencies (backend)
cd apps/backend
uv sync

# Install Node.js dependencies (frontend)
cd ../frontend
npm install
```

### 2. Configuration

```bash
# Return to project root and copy environment template
cd ../..
cp .env.example .env

# Edit .env and add your API keys:
# OPENAI_API_KEY=your_api_key_here
# LANGCHAIN_API_KEY=your_langchain_key_here  # Optional: for LangSmith tracing
```

### 3. Run the Application

**Terminal 1 - Backend:**
```bash
cd apps/backend
uv run python -m thudbot_core
```

**Terminal 2 - Frontend:**  
```bash
cd apps/frontend
npm run dev
```

**Access:** Open `http://localhost:3000` in your browser!

## 🏗️ Architecture

```
Frontend (Next.js) → Backend (FastAPI) → Agent (LangGraph)
```

**Built with:**
- **Backend**: FastAPI + LangChain + OpenAI GPT-4
- **Frontend**: Next.js + React + Tailwind CSS  
- **Data**: CSV hint database + Qdrant vector store

## 📊 RAG Evaluation & Performance

**Data-driven retriever selection** using comprehensive evaluation:

- **📓 Full evaluation in:** `00_Thud_construction.ipynb`
- **🧪 Framework:** RAGAS metrics (context recall, entity recall, noise sensitivity)
- **📋 Golden dataset:** 12 synthetically generated test queries  
- **🥇 Platinum dataset:**  Selected subset of 5 queries, produced by applying a LangChain-based rewriting prompt to the golden dataset, followed by manual selection for evaluation focus and cost control
- **⚖️ Compared retrievers:** Naive, BM25, Multi-query
- **🎯 Result:** Multi-query retrieval selected based on superior performance

**Key findings:**
- Multi-query retrieval significantly improved context precision
- Enhanced handling of ambiguous game terminology  
- Better retrieval of relevant hints for complex puzzles

*See notebook for detailed metrics, comparison tables, and methodology.*

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
uv run pytest

# Run tests with the commit script
./check_and_commit.sh "your commit message"
```

**Test coverage includes:**
- Data validation (CSV exists & structure)
- Module imports (all components load)
- File organization (required files present)
- Basic functionality verification
## 🎮 Usage Examples

**Ask about game puzzles:**
```
"How do I get the token from the cup?"
→ "The bus token is in the cup; make sure Thud has it before you hop on the bus."
```

**Get general game help**
```
"When is the shuttle to Karkas 4?"
→ "The shuttle to Karkas 4 departs at 22:50."
```


## 📖 Project Structure

```
thudbot2/
├── apps/
│   ├── backend/            # Python FastAPI backend
│   │   ├── thudbot_core/   # Core application code
│   │   │   ├── *_node.py   # LangGraph workflow nodes
│   │   │   ├── api.py      # FastAPI backend server
│   │   │   ├── langgraph_flow.py # Main workflow orchestration
│   │   │   └── state.py    # Shared state management
│   │   ├── data/           # CSV hint database
│   │   ├── tests/          # Backend test suite
│   │   ├── pyproject.toml  # Python dependencies & config
│   │   └── Dockerfile      # Backend container image
│   └── frontend/           # Next.js frontend
│       ├── app/            # Next.js app directory
│       ├── public/         # Static assets (PDA interface)
│       └── package.json    # Node.js dependencies
├── infra/
│   ├── compose.yml         # Docker Compose (default)
│   └── compose.prod.yml    # Production Docker Compose
├── docs/                   # Project documentation
├── notebooks/              # Jupyter notebooks used for prototype development
├── .env                    # Environment variables (not in git)
├── README.md               # This file
└── check_and_commit.sh     # Test runner and commit script
```


## 🚨 Troubleshooting Tips

- Make sure `.env` is properly configured with a valid OpenAI key.
- Restart both frontend and backend if switching API keys or files.
- Backend logs appear in the terminal where you run `uv run python -m thudbot_core`.
- For Docker Compose issues, try `docker compose down` then `docker compose up --build`.


## 📄 License

 _This project is [copyrighted](COPYRIGHT) and all rights are reserved. Leo DaCosta 2025_ 