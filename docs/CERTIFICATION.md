# 🎓 Certification Challenge: Thudbot Submission

This document outlines how the Thudbot project meets all 7 required tasks for the AIM Certification Challenge.

---

## ✅ Task 1: Define the Problem and Audience

**Problem:**  
You're playing _The Space Bar_, a quirky, puzzle-rich sci-fi game, and you get stuck. Online resources are scarce, outdated, or full of spoilers. You want a subtle, immersive hint — not a line-by-line walkthrough.

**Audience:**  
Players of _The Space Bar_ and similar games who value immersion and in-character experiences. They prefer organic hints to maintain the game's tone and challenge. Thudbot offers help in the voice of Thud, an original in-game character, preserving narrative and puzzle integrity.

---

## ✅ Task 2: Proposed Solution and Tooling

**Solution:**  
Thudbot is a web-based agentic companion that delivers in-character puzzle hints using a LangChain agent backed by structured hint data and fallback logic. Users interact through a chat-style interface that mirrors talking to an NPC.

**Tooling Stack:**
- **LLM:** OpenAI GPT-4.1-nano
- **Embeddings:** `text-embedding-3-small`
- **Vector DB:** Qdrant (in-memory)
- **Agent Framework:** LangChain `AgentExecutor` with tools
- **UI:** Next.js frontend with FastAPI backend
- **Monitoring:** LangSmith
- **Evaluation:** RAGAS
- **External API:** OpenWeatherMap (for fallback tool)

---

## ✅ Task 3: Data Sources and External APIs

**Hint Data:**  
Custom CSV file with structured hint entries (fields: question_id, category, question, hint_level, hint_text, puzzle_name, character, location, etc.). Derived from public walkthroughs and curated manually.

**External API:**  
OpenWeatherMap used as a fallback "tool" when no hint is found — Thud responds with weather info, humorously framed as a character quirk.

---

## ✅ Task 4: Agentic RAG Implementation

Implemented a LangChain `AgentExecutor` with two tools:
- `hint_lookup`: RAG retriever using multi-query embedding search
- `get_weather`: External API for fallback conversations

Agent is prompt-tuned to sound like Thud and simulate reasoning with limited knowledge.

---

## ✅ Task 5: Golden Dataset and Evaluation

**Golden Set:**  
12 synthetic player-style queries generated via SDG. Stored in structured format with expected answers.

**Platinum Subset:**  
5 representative queries selected via a LangChain-based rewriting prompt, curated for diversity and cost efficiency.

**Evaluation Framework:**  
Used RAGAS to measure:
- Context Recall
- Entity Recall
- Noise Sensitivity

---

## ✅ Task 6: Advanced Retrieval Techniques

**Compared Retrievers:**
- Naive (cosine similarity)
- BM25 (keyword overlap)
- Multi-query (diversified semantic embeddings)

**Rationale:**  
BM25 performs well on short queries. Multi-query improves robustness to vague or underspecified inputs. Chosen based on puzzle language and player phrasing variance.

---

## ✅ Task 7: Evaluation Results and Insights

| Retriever   | Context Recall | Entity Recall | Noise Sensitivity | Latency | Est. Cost |
|-------------|----------------|----------------|-------------------|---------|-----------|
| Naive       | 0.5067         | 0.6440         | 0.0833            | ~2.5s   | ~$0.00025 |
| BM25        | 0.3667         | 0.5690         | 0.0990            | ~1.5s   | ~$0.00021 |
| Multi-query | 0.5067         | 0.7524         | 0.0125            | ~4.5s   | ~$0.00041 |

**Conclusion:**  
Multi-query provided the best retrieval quality with modest latency tradeoffs, and was selected as the production retriever.

---

## 📎 References

- [📘 Design Doc](./DESIGN.md)
- [📄 README](../README.md)
- [📓 Notebook: `00_Thud_construction.ipynb`](../00_Thud_construction.ipynb)
- [🧪 Evaluation Checkpoint](./dev_journey/CHECKPOINT_20250802_2350.md)
- [🧪 Final Build Checkpoint](./dev_journey/CHECKPOINT_20250803_2330.md)
