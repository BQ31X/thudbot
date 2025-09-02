# 🧠 Thudbot System Overview

## Architecture Summary

- **Frontend**: Next.js + Tailwind
- **Backend**: FastAPI + LangGraph
- **LLM**: OpenAI GPT-4 Turbo (future: self-hosted)
- **Vector Store**: Qdrant
- **Orchestration**: LangGraph state machine
- **Observability**: LangSmith

## Design Philosophy

- Diegetic hinting via in-universe character (Zelda)
- Progressive hint escalation 
- Clean separation of routing, retrieval, and character voice

## 🔄 LangGraph Flow Summary

- **Router Node:** Classifies intent, manages escalation logic
- **Find Hint Node:** Performs metadata-aware vector search
- **Verify Correctness Node:** Ensures retrieved content is grounded
- **Maintain Character Node:** Rewrites responses in Zelda's voice
- **Output Node:** Formats and returns the final message

All nodes interact via a shared LangGraph state object that includes `chat_history`, `last_question_id`, `hint_level`, and `retries`.

## 🔍 Data Strategy

- **Custom CSV Dataset:** Structured hints with fields like `puzzle_name`, `hint_level`, `speaker`, `tone`
- **Chunking:** One row per embedded document
- **Hint Escalation Logic:** Based on query repetition or similarity
## Planned Enhancements

- Voice input / output
- Multi-character support
- Self-hosted LLM pipeline

---
_Last updated: [2-Sept-2025]_