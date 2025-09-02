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
    
    1. Follow the [Setup & Installation](#-setup--installation) steps below
        
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

### Prerequisites

- Python 3.12+
- Node.js 18+

### 1. Environment Setup

```bash
# 📦 Clone the repo (check latest stable branch)
git clone https://github.com/BQ31X/thudbot.git
cd thudbot


# Create Python virtual environment  
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
uv sync

# Install Node.js dependencies
npm install
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Add your OpenAI API key to .env
OPENAI_API_KEY=your_api_key_here
```

### 3. Run the Application

**Terminal 1 - Backend:**
```bash
source .venv/bin/activate
uv run python src/api.py
```

**Terminal 2 - Frontend:**  
```bash
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
thudbot/
├── src/                     # Core application code
│   ├── *_node.py           # LangGraph workflow nodes
│   ├── api.py              # FastAPI backend server
│   ├── langgraph_flow.py   # Main workflow orchestration
│   ├── state.py            # Shared state management
│   └── app/                # Next.js frontend
├── tests/                  # Test suite
│   ├── regression/         # Regression testing
│   └── node_specific/      # Component-specific tests
├── data/                   # CSV hint database
├── docs/                   # Project documentation
├── public/                 # Static assets (PDA interface)
├── pyproject.toml          # Python dependencies & config
└── package.json            # Node.js dependencies
```


> ⚠️ **Note:** Test organization is currently being refactored. Some test files are temporarily located in `src/` and will be consolidated into the `tests/` directory structure.


## 🚨 Troubleshooting Tips

- Make sure `.env` is properly configured with a valid OpenAI key.
- Restart both frontend and backend if switching API keys or files.
- Logs appear in the terminal where you run `src/api.py`.


## 📄 License

 _This project is [copyrighted](COPYRIGHT) and all rights are reserved. Leo DaCosta 2025_ 