# 🍺 Thudbot - The Space Bar AI Assistant

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue.svg" alt="Python 3.12+"/>
  <img src="https://img.shields.io/badge/FastAPI-0.109.2-green.svg" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Next.js-14+-black.svg" alt="Next.js"/>
  <img src="https://img.shields.io/badge/LangChain-🦜-yellow.svg" alt="LangChain"/>
</p>

An intelligent AI assistant for **The Space Bar** adventure game that provides contextual hints and weather information through a clean web interface.

## 🚀 Project Overview

Thudbot converts a Jupyter notebook-based game assistant into a production-ready web application. Players can ask questions about The Space Bar adventure game and receive contextual hints from a RAG-powered knowledge base, with weather information as a fallback for non-game questions.

**Built from notebook to web app in record time!** 🚀

## ✨ Features

- **🎮 Game Hint System**: RAG-powered hints for The Space Bar adventure game puzzles
- **🌤️ Weather Integration**: Real-time weather information as fallback responses  
- **🤖 LangChain Agent**: Intelligent tool selection between hint lookup and weather
- **🌐 Web Interface**: Clean Next.js frontend for easy interaction
- **⚡ FastAPI Backend**: High-performance Python API server
- **🧪 Comprehensive Testing**: Robust test suite with pytest

## ⚡ Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- OpenAI API Key

### 1. Environment Setup

```bash
# Clone the repository
git clone <your-repo-url>
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
→ "The bus token is in a cup nearby; make sure Thud has it before you hop on the bus."
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
## 📄 License

This project is copyrighted and all rights are reserved. Boffo Games 2025_  - see the [COPYRIGHT](COPYRIGHT) file for details.

## 🚀 Built With

**From Jupyter notebook to production web app!** This project demonstrates:
- Converting research code to production systems
- Rapid prototyping with modern AI tools  
- Full-stack development with Python + TypeScript
- Clean architecture patterns for AI applications

## 📄 License

 _This project is copyrighted and all rights are reserved. Boffo Games 2025_ 