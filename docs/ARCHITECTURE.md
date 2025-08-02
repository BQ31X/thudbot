# THUDBOT System Architecture & Tech Stack

## 🧰 ** Proposed Tech Stack for Certification Challenge**

### 1. **LLM**

- **GPT-4-turbo via OpenAI API** — Primary language model used for all generation, including in-character responses from Thud.
    
- _(Stretch Goal: Use Ollama + Phi-2 locally to support private hint data and reduce API dependence.)_
    

### 2. **Embedding Model**

- **text-embedding-3-small (OpenAI)** — Used to embed individual hint entries from a structured CSV. Chosen for simplicity, cost-efficiency, and tight OpenAI integration.
    

### 3. **RAG Data Source**

- **Curated CSV Dataset** — Custom-authored or paraphrased hint content stored in structured format with metadata (`game_section`, `puzzle_name`, `hint_level`, etc.). Designed for clean chunking and precise filtering.
    

### 4. **Vector Database**

- **Qdrant (local)** — Stores embedded hint chunks with full metadata support. Enables similarity-based retrieval plus filtering by section or hint level.
- Embedded data will be stored in-memory for development simplicity. This avoids persistence complexity while still enabling local retrieval for RAG.
    

### 5. **Orchestration**

- **LangChain + Agent with Tool-Based RAG** — Wraps RAG as a LangChain `Tool` named `"hint_lookup"`, following the Homework 5/6 pattern to support agent-based tool invocation.
    
- _(Stretch Goal: Use LangGraph for richer agent flow, e.g. Thud → Fleebix → Thud.)_
    

### 6. **Tool Integration**

- To satisfy the Certification Challenge requirement for agentic tool usage, I plan to follow the pattern introduced in Homeworks 5 and 6. I will define my RAG retrieval pipeline as a callable LangChain `Tool` named `"hint_lookup"`, which the agent can invoke to access structured, metadata-rich hints stored in a vector database. This approach allows RAG to function as an explicit tool in the agent's reasoning flow, meeting the certification’s tool-use requirement without requiring external APIs. If time permits, I may add a second tool (e.g., `"consult_fleebix"`) that simulates a fallback agent response for flavor and behavioral variety.

- **hint_lookup (RAG as Tool)** — Structured retrieval from vector store, implemented as a LangChain Tool
- **Firecrawl.dev or Tavily** — Integrated as a fallback tool if RAG retrieval fails, simulating a "Thud checks the Archive" behavior.
- _(Optional)_: **Mock Fleebix API (JSON)** — Stretch goal; used to simulate secondary external lookup with fixed responses.
- _(Alternative fallback: simulated Fleebix function returning scripted responses. Satisfies AIM’s agent/tool usage requirement.)_
    

### 7. **Monitoring & Instrumentation**

- **LangSmith** — Tracks prompt/response traces, assists with debugging and RAG evaluation. Required for certification.

### 8. **Evaluation**

- **RAGAS** — Used to evaluate hint accuracy, faithfulness, and context relevance using a small synthetic test set.
    
- _(Includes multiple hint levels per puzzle to allow fine-grained relevance scoring.)_
    

### 9. **User Interface**

- **Streamlit (preferred) or Flask (fallback)** — Lightweight UI with:
    
    - Text input
        
    - Chat-style Thud response field
        
    - Optional “explain this answer” trace/debug toggle
        
- _(Stretch Goal: Stylized version with Space Bar–inspired UI elements.)_
    

### 10. **Session History (Stretch Goal)**

- _(Stretch Goal)_ Implement lightweight session tracking using local file logs, or Streamlit session state to allow Thud to remember previous queries and avoid repeating hint levels unnecessarily.
    

### 11. **Hosting**

- **Localhost prototype for certification** — No deployment required.
    
- _(Future: VPS-hosted version using Docker for reproducibility. Planned setup includes Python 3.11, Ubuntu 22.04, and Let’s Encrypt SSL if public.)_
    

---

## 🔍 Summary Rationale

This stack is designed to:

- Deliver high-fidelity, in-character responses from a fictional NPC
- Use structured, safe-to-use hint data in a controlled, traceable RAG pipeline
- Demonstrate agentic reasoning via tool fallback behavior
- Allow easy debugging, evaluation, and submission (via LangSmith + RAGAS)
- Be modular enough to support future hosting, multi-agent expansion, and visual polish
---
## Appendix A: Converting a Jupyter Notebook to a Python Script


https://g.co/gemini/share/6fc814e5c293

--- 
## Appendix B: Key Architectural Decisions
Additional Tech stack considerations

To finalize the tech stack for this Thudbot project, I considered other recent projects that I have some familiarity with, and could leverage. I used Claude and Gemini to evaluate the three below tech stacks as possibilities for this project.

Criteria considered:
Which will be likely to offer least technical resistance; e.g. env conflicts, setup issues?
Which will be quickest to build and test, for certification challenge? (only ~4 days available)
Which will offer best options for observability and evaluation?
Which will be most extensible to public hosted version, for AIM demo day?
Which will be most scalable to future use of Thudbot (including self-hosting at my boffo.games website and integration of SLM model)
Is there a hybrid approach?

*Also note: 

2 & 3 were largely "vibe coded" by Claude Sonnet; 1 is the one for which I best understand the code. However, 1 is 'notebook' based, which may be a limitation.

I do need a distinct chat-bot style front-end, which I am allowed/expected to 'vibe-code'.

#### 1. 🔧 This is the tech stack used for a HW #9, to evaluate and compare different retrieval methods (as summarized by ChatGPT)

- **LangChain** – For building and chaining together retrieval and evaluation components
- **Ragas** – To compute retrieval-specific evaluation metrics (e.g., context recall, noise sensitivity)
- **LangSmith** – (Partially used) For tracing, latency, and cost monitoring
- **OpenAI** – LLMs for generation and evaluation (`gpt-4.1-mini`, etc.)
- **Anthropic** – Claude models used when OpenAI rate-limited
- **Cohere** – Used for reranking in Contextual Compression 
- **Python** – Primary language, with standard libs like `uuid`, `os`, and `time` 
- **Jupyter Notebooks** – For code execution and documentation 

---
#### 2. This is the tech stack used for recent Google Hackathon submission (as summarized by Claude)


## **Pandemonium/SpyGame Tech Stack Summary**

### **Core Framework & AI**
- **Agent Framework**: Google ADK (Agent Development Kit) v1.5.0
- **AI Model**: Gemini 2.0 Flash for natural language reasoning
- **Architecture Pattern**: Multi-agent system (Game Master, Spymaster, Operative)

### **Development Environment**
- **Language**: Python 3.10
- **Package Management**: Conda + pip
- **Environment**: `environment.yml` specification
- **Alternative**: Dockerfile for containerized deployment

### **Multi-Agent Communication**
- **Patterns**: Agent-as-Tool, Shared Session State, Workflow Agents
- **State Management**: Centralized session dictionary
- **Tool Exposure**: Function-based inter-agent communication

### **Development & Testing**
- **Testing Framework**: pytest + custom game simulation scripts
- **Code Quality**: black (formatting), flake8 (linting)
- **Version Control**: Git/GitHub with structured branching
- **CI/CD**: Automated testing scripts (`TEST.sh`, `check_and_commit.sh`)

### **Prompt Engineering Focus**
- **Strategy**: External prompt files with environment-based switching
- **Variants**: Production, debug, enhanced modes
- **Testing**: Custom scenario generation tools (`spymaster_tester.py`)

### **Documentation & Structure**
- **Docs**: Comprehensive markdown (ARCHITECTURE.md, EXPLANATION.md)
- **Development Tracking**: Journal logs, screenshot documentation
- **Code Organization**: Modular `src/` structure with clear separation

### **Key Strengths**
- **Rapid prototyping** with ADK framework
- **Professional documentation** standards
- **Sophisticated prompt engineering** capabilities
- **Multi-agent coordination** patterns
- **Competition-ready** structure (IEEE submission format)


#### 3. This is the tech stack used for pdf based end to end rag application, aka Homework 3, (as summarized by Claude)

Project Type: Full-stack LLM-powered chat application with streaming responses

### Frontend Stack

- Framework: Next.js 14.2.30 (React 18.2.0)

- Language: TypeScript 5.3.3

- Styling: Tailwind CSS 3.4.1 + PostCSS + Autoprefixer

- HTTP Client: Axios 1.6.7

- Development: ESLint, Next.js App Router, React Strict Mode

### Backend Stack

- Framework: FastAPI 0.109.2

- Language: Python

- Server: Uvicorn 0.27.1 (ASGI server)

- Data Validation: Pydantic 2.6.1

- AI Integration: OpenAI API 1.12.0

- Features: Streaming responses, CORS enabled, async/await pattern

### Deployment & Infrastructure

- Platform: Vercel

- Architecture: Serverless functions

- Frontend Deployment: @vercel/next

- Backend Deployment: @vercel/python

- API Routing: Proxy setup from frontend to backend

### Key Features & Capabilities

- Real-time streaming chat responses

- OpenAI GPT model integration (configurable model selection)

- Cross-origin resource sharing (CORS) enabled

- Full TypeScript support

- Responsive design with Tailwind CSS

- Development/production environment separation

- API key authentication (user-provided)

### Development Experience

- Hot reload in development

- TypeScript for type safety

- Modern React patterns (functional components, hooks)

- RESTful API design

- Modular component architecture

- Utility-first CSS with Tailwind

This stack is particularly well-suited for AI-powered applications, real-time chat interfaces, and rapid prototyping with modern web technologies. It offers excellent developer experience while maintaining production-ready performance and scalability through Vercel's serverless architecture.
