# 🍺 Thudbot - The Space Bar AI Assistant

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue.svg" alt="Python 3.12+"/>
  <img src="https://img.shields.io/badge/FastAPI-0.109.2-green.svg" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Next.js-14+-black.svg" alt="Next.js"/>
  <img src="https://img.shields.io/badge/LangChain-🦜-yellow.svg" alt="LangChain"/>
</p>

# Welcome to THUDBOT

An intelligent AI assistant for **The Space Bar** adventure game that provides contextual hints and weather information through a clean web interface.

New here? Check out the Quick Start

## Quick Start

1. 🎬 **[Watch the Loom video](https://www.loom.com/share/bd971bccf3ca4b8094c5ed47c03451c3)** to get oriented to Thudbot
    
2. 📄 **Read [`CERTIFICATION.md`](docs/CERTIFICATION.md)** to understand how Thudbot meets the certification challenge
    
3. 🧪 **Try out Thudbot locally**
    
    1. Follow the [Setup & Installation](#-setup--installation) steps below
        
    2. Try these [Example Queries](#-testing-guide-for-graders) to test hinting and tool use
        
4. 🛠 **Learn how Thudbot was built**
    
    1. Review the [RAG evaluation in `00_Thud_construction.ipynb`](00_Thud_construction.ipynb)
        
    2. Explore the [prototype notebook](01_Thud_construction.ipynb) and final [`src/agent.py`](src/agent.py) code for the `AgentExecutor` with tools
        
5. 🔍 **Want to dig deeper?**
    
    1. Include your LangChain API key in the UI to activate LangSmith Tracing
        
    2. Read [`DESIGN.md`](docs/DESIGN.md) and [`ARCHITECTURE.md`](docs/ARCHITECTURE.md) for construction details
    
    3. Follow the [development journey here](docs/dev_journey/)
        
    4. See the full [test plan](docs/TEST_PLAN.md) for engineering-level detail

## 🚀 Project Overview

Thudbot was prototyped via a Jupyter notebook, then converted to this production-ready web application. Players can ask questions about The Space Bar adventure game and receive contextual hints from a RAG-powered knowledge base, with weather information as a fallback for non-game questions.

**Built from notebook to web app in record time!** 🚀 (Claude likes to brag about this part)

## 🎬 Demo Video

**[Watch the 5-Minute Live Demo](https://www.loom.com/share/bd971bccf3ca4b8094c5ed47c03451c3)**

*See Thudbot in action: agentic tool selection, character-driven responses, and real-time problem solving for The Space Bar game puzzles.*

## 🧪 Testing Guide for Graders

**Not familiar with "The Space Bar" game? No problem!** Here are ready-to-test examples:

### **Game Hint Examples** (Tests RAG system)
```
Q: "Where can I find the bus token?"
Expected: Thud should tell you to look in the cup

Q: "How do I empathy telepathy?"
Expected: Guidance for this unique game mechanic

Q: "How do I use the lockers in the vestibule?"
Expected: Instructions to look for an available locker

Q: "When does the shuttle to Karkas 4 leave?"
Expected: Specific time (22:50) with character commentary about checking monitors
```

### **Weather Tool Examples** (Tests external API)
```
Q: "What's the weather in Boston?"
Expected: Real-time weather data with temperature

Q: "How's the weather in New York?"
Expected: Current weather conditions for any city
```

### **Character Voice Examples**
Thud responds as a friendly, simple-minded bar patron with phrases like "Oh, hello there!" and "Hope that helps!" Watch for:
- ✅ **In-character responses** with game-specific knowledge
- ✅ **Intelligent tool selection** (game questions → hints, weather questions → weather API)
- ✅ **Graceful error handling** (no technical errors shown to users)

## ✨ Features

- **🎮 Game Hint System**: RAG-powered hints for The Space Bar adventure game puzzles
- **🌤️ Weather Integration**: Real-time weather information as external API demonstration
- **🤖 LangChain Agent**: Intelligent tool selection between hint lookup and weather
- **🛡️ Robust Error Handling**: Graceful LLM parsing error recovery, no technical errors shown to users
- **🌐 Web Interface**: Clean Next.js frontend with custom Thud icon branding
- **⚡ FastAPI Backend**: High-performance Python API server
- **🧪 Comprehensive Testing**: Robust test suite with pytest

## ⚡ Setup & Installation

### Prerequisites

- Python 3.12+
- Node.js 18+
- OpenAI API Key
- OpenWeather API Key (optional)

### 1. Environment Setup

```bash
# 📦 Clone the repository
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

**Note:** This is a locally-hosted prototype for certification evaluation. No production deployment is currently configured.

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

**Get general game help:**
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

## 🚨 Troubleshooting

### **Performance Notes**

- **🔑 Recommended:** Set OpenAI API key in `.env` file for optimal performance
- **🌤️ Optional:** Add OpenWeather API key for weather functionality  
- **⚡ Debug output:** Available in backend terminal during development

### **Known Issues & Future Enhancements**

**Thud Personality Limitations:**
- **Current State:** Thud responds reliably but with simplified personality
- **Design Intent:** Thud should fall back to weather chat when confused by non-game questions
- **Technical Challenge:** Complex fallback logic previously caused agent loops and iteration limits
- **Resolution:** Prioritized stability over personality for certification deadline

**Conversation Memory Limitations:**
- **No Context Retention:** Each question is treated independently with no memory of previous interactions
- **Pronoun Problems:** Questions like "What does it do?" fail because "it" has no referent from prior context
- **Impact:** Users must provide full context in each message rather than building on previous exchanges
- **Workaround:** Always use specific nouns instead of pronouns (e.g., "What does the voice printer do?" not "What does it do?")

**Planned Improvements:**
- **Enhanced Character Voice:** More Thud-specific speech patterns ("Thud would lose his tail if it wasn't attached")
- **Intelligent Weather Fallback:** Weather tool activation when RAG confidence is low
- **Session Memory:** Track conversation context to handle pronouns and follow-up questions naturally
- **Progressive Hint System:** Remember what hints were already given and escalate appropriately
- **Error Recovery:** More creative responses when external APIs fail
- **Production Deployment:** Cloud hosting configuration (Dockerfile requires updates for FastAPI + Next.js stack)

**Development Notes:**
- Agent behavior is primarily driven by the `THUD_TEMPLATE` prompt (~80% of personality)
- AgentExecutor handles tool routing (~15% of behavior) 
- Tool-specific logic provides minimal behavioral impact (~5%)
- Future personality enhancements should focus on prompt engineering and RAG confidence scoring

## 📝 Graders Note

**For certification evaluators:** See [CERTIFICATION.md](docs/CERTIFICATION.md) for detailed mapping of this project to all 7 required certification tasks, including evaluation results and technical implementation details.

## 📄 License

 _This project is [copyrighted](COPYRIGHT) and all rights are reserved. Leo DaCosta 2025_ 