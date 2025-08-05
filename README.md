# 🍺 Thudbot - The Space Bar AI Assistant

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue.svg" alt="Python 3.12+"/>
  <img src="https://img.shields.io/badge/FastAPI-0.109.2-green.svg" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Next.js-14+-black.svg" alt="Next.js"/>
  <img src="https://img.shields.io/badge/LangChain-🦜-yellow.svg" alt="LangChain"/>
</p>

An intelligent AI assistant for **The Space Bar** adventure game that provides contextual hints and weather information through a clean web interface.

## 🚀 Project Overview

Thudbot was prototyped via a Jupyter notebook, then converted to this production-ready web application. Players can ask questions about The Space Bar adventure game and receive contextual hints from a RAG-powered knowledge base, with weather information as a fallback for non-game questions.

**Built from notebook to web app in record time!** 🚀 (Claude likes to brag about this part)

## 🎬 Demo Video

**[Watch the 5-Minute Live Demo](https://www.loom.com/share/bd971bccf3ca4b8094c5ed47c03451c3)**

*See Thudbot in action: agentic tool selection, character-driven responses, and real-time problem solving for The Space Bar game puzzles.*

## ✨ Features

- **🎮 Game Hint System**: RAG-powered hints for The Space Bar adventure game puzzles
- **🌤️ Weather Integration**: Real-time weather information as fallback responses  (to meet api requirement)
- **🤖 LangChain Agent**: Intelligent tool selection between hint lookup and weather
- **🌐 Web Interface**: Clean Next.js frontend for easy interaction
- **⚡ FastAPI Backend**: High-performance Python API server
- **🧪 Comprehensive Testing**: Robust test suite with pytest

## ⚡ Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- OpenAI API Key
- OpenWeather API Key (optional)

### 1. Environment Setup

```bash
# 📦 Clone the correct feature branch **(not main!)**
git clone --branch feat/thudbot-cc https://github.com/BQ31X/thudbot.git
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
Frontend (Next.js) → Backend (FastAPI) → Agent (LangChain) → Tools (Hints/Weather)
```

**Built with:**
- **Backend**: FastAPI + LangChain + OpenAI GPT-4
- **Frontend**: Next.js + React + Tailwind CSS  
- **Data**: CSV hint database + Qdrant vector store
- **Tools**: Weather API + RAG hint lookup

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

**Get general game help
```
"When is the shuttle to Karas 4?"
→ "The shuttle to Karkas 4 departs at 22:50."
```

**Get weather information:**
```  
"What's the weather in Boston?"
→ "It's currently clear sky, around 69°F in Boston."
```

## 📖 Project Structure

```
thudbot/
├── src/
│   ├── agent.py          # LangChain agent & RAG logic
│   ├── api.py            # FastAPI backend server
│   └── app/              # Next.js frontend
├── data/                 # CSV hint database
├── tests/                # Comprehensive test suite
├── requirements.txt      # Python dependencies
└── package.json          # Node.js dependencies
```

## 🚀 Built With

**From Jupyter notebook to production web app!** This project demonstrates:
- Converting research code to production systems
- Rapid prototyping with modern AI tools  
- Full-stack development with Python + TypeScript
- Clean architecture patterns for AI applications

## 📝 Graders Note

**For certification evaluators:** See [CERTIFICATION.md](docs/CERTIFICATION.md) for detailed mapping of this project to all 7 required certification tasks, including evaluation results and technical implementation details.

## 📄 License

 _This project is [copyrighted](COPYRIGHT) and all rights are reserved. Leo DaCosta 2025_ 