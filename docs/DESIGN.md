7/31/25
### AI Makerspace assignment: Certification challenge
Not necessary, but recommended to use it as a stepping-stone to demo day/final project.

1. Due Tuesday August 5 (currently Thursday 7/31)
2. Can be a locally hosted prototype, but 
3. must demonstrate knowledge of these elements:
	1. RAG
	2. Agentic behavior
	3. SDG (e.g. Ragas)
	4. Instrumentation (e.g. LangSmith)
	5. Eval (e.g. Ragas)
	6. Memory / session state

## Task 1: Defining your Problem and Audience


---
## ✅ Problem Statement

Imagine you are playing _The Space Bar_, the cult-classic sci-fi adventure game from Boffo Games. You've been interrogating bizarre alien suspects for hours, and now you’re stuck on a puzzle that makes sense only if you understand how a Sraffan thinks after four Margaritas. Frustrated, you alt-tab to the internet… only to find scattered walkthroughs, spoiler-heavy guides, or dead links.



## ✅ Audience

The audience for this application includes fans of _The Space Bar_ and similar puzzle-rich games. These players appreciate immersive storytelling, quirky characters, and solving challenges organically. They don’t want to break immersion or read line-by-line walkthroughs with spoilers. They want subtle, diegetic clues, i.e., in-character clues that feel like they belong _inside_ the game world. My application brings that experience to life, by having Thud (a well-known in-game character) offer hints in his original voice, keeping the magic, and the challenge, of the game intact.

---
## Task 2: Propose a Solution
### ✅ Proposed Solution

Thudbot is a web-based character agent who will live at boffo.games and provide immersive in-universe puzzle hints for _The Space Bar_, speaking in the distinctive character style of Thud, one of the first characters you meet in game. Instead of breaking immersion with walkthroughs, players can chat directly with Thud, who responds using a mix of structured hint data and humorous improvisation. When a player types a question, Thudbot first checks a structured database of known puzzle hints and responds in his signature style. If he’s stumped, Thud may consult his gruff colleague Fleebix (simulated via fallback logic*). The result is an immersive, interactive hint system that feels like part of the game itself.

The experience is designed to feel like talking to an NPC from within the game. Over time, this foundation can scale to support other characters, games, or even serve as a demo for AI-powered NPCs in retro or indie titles.

* Fallback logic means Thud remains the only visible agent, but if no matching hint is found, the system switches to a different prompt template and responds as if Fleebix provided the answer. This simulates an agent handoff without requiring a second active agent or complex routing.

---



### ✅ **Agentic Reasoning Usage**

- **Primary agent**: Thud, with personality and limited knowledge.
    
- **Agentic behavior**: Thud tries to answer directly; if stumped, he "consults" Fleebix (simulated agent handoff).
    
- **Optional expansion**: Fleebix can be modeled as a separate agent with different tone and logic, using LangGraph to route user queries based on detected confusion.


--- 

### ✅ **Task 3: Dealing with the Data**

#### 1. **Describe all of your data sources and external APIs, and describe what you’ll use them for.**

- **Data Source #1: Public walkthroughs and fan-written hint content**  
    I will scrape or extract hints and puzzle-solving advice from online sources such as fan forums, archived game FAQs, and community wikis related to _The Space Bar_. These are safe to use, as they are already publicly posted. This data will be chunked, embedded, and used as the knowledge base for RAG-style retrieval when players ask Thudbot for help.
    I plan to structure this data into a custom CSV file containing **discrete hint entries**, each tagged with metadata fields such as:

	- Puzzle or location
	- Hint level (e.g., subtle, moderate, full solution)
	- Optional source citation or fallback comments
    
This format enables easier chunking, embedding, and retrieval based on player intent and desired hint granularity.
    
- **Data Source #2: Original game design documents (private)**  
    I have access to the internal design docs from the original game development process. These contain valuable insight for hint generation, Thud’s character voice, and potential future expansion. However, I will **not include them** in the prototype or RAG system for the certification challenge due to IP sensitivity and privacy concerns. Long-term, I plan to incorporate this material by self-hosting a small language model such as **Phi-2 via Ollama**. Because Thud’s task is narrow in scope (and Thud himself is intentionally simple-minded), a small local model should be sufficient.
    
- **External APIs:**  
    I plan to use the **OpenAI API (GPT-4-turbo and text-embedding-3-small)** for generation and retrieval. I may later replace these with self-hosted models for privacy or cost reasons.
    

---

### 🌐 **External API Usage (Planned)**

Initially, all hint data will be pre-collected manually. I plan to integrate a general-purpose search tool — likely **Firecrawl.dev** or **Tavily** — to allow Thud to “look things up” when he cannot find a suitable hint in the vector store. While most responses will come from the curated hint database, this tool will attempt to fetch obscure online content dynamically. This behavior will be framed in-universe as Thud “checking with Fleebix,” preserving narrative immersion while satisfying the certification requirement for external API usage.

However, I’ve identified a significant risk: there is **very limited publicly available hint data** for _The Space Bar_, and early tests confirm that general-purpose search tools are unlikely to return useful results.

To address this, I have two fallback strategies:

1. **Seed a Public Knowledge Source:**  
    I may publish a small, curated set of puzzle hints (e.g., on GitHub or boffo.games) and structure Firecrawl or Tavily queries to reliably retrieve these known pages.
    
2. **Use a Mock External Endpoint:**  
    Alternatively, I may implement a lightweight external API (e.g., via Glitch or webhook.site) that returns JSON-formatted responses in Fleebix’s voice. This would simulate a real external lookup, while giving me full control over the content and tone.
    

> _Firecrawl.dev_ combines real-time search with optional scraping and returns markdown-formatted page content. It appears well suited for retrieving niche gameplay content — provided the data is publicly available and discoverable.

#### 2. **Describe the default chunking strategy that you will use. Why did you make this decision?**

### 🔍 Embedding & Chunking Strategy (Design Plan)

To support semantic search over puzzle hint data, I initially considered chunking freeform walkthrough text into short Q&A-style blocks or ~100–200 word passages. This would have aligned with how players typically request help — by referencing specific puzzles, locations, or characters (e.g., “How do I get past the security guard?”). I explored approaches like manual segmentation or LangChain’s `RecursiveCharacterTextSplitter` to divide text along natural language boundaries.

However, I quickly realized that license-safe, unstructured walkthrough content was limited for this game. As a result, I decided to pivot to a **structured data approach** using a custom CSV file. Each row in the file will represent a single hint, along with associated metadata fields such as `game_section`, `puzzle_name`, and `hint_level`.

This will allow me to chunk the data semantically — one row per embedding — and use the `hint_text` field as the document content. I plan to embed each document using OpenAI’s `text-embedding-3-small` model and store them in a **Qdrant vectorstore**. Metadata fields will be preserved for later use in filtering and evaluation.

This design supports:

- High-precision retrieval with metadata-aware filtering (e.g., retrieve only hints from a specific scene)
    
- Controlled escalation of hint levels (similar to UHS-style hint reveal)
    
- Reuse of familiar LangChain components, including `CSVLoader` and `Qdrant.from_documents`, based on prior AIM homework patterns
    

Overall, this strategy provides clean separation between content, structure, and logic, while keeping the retrieval pipeline lightweight and explainable.

#### 3. **[Optional] Will you need specific data for any other part of your application? If so, explain.**

Eventually, I want to use the internal design documents to fine-tune the personality or logic of Fleebix, or to seed synthetic data generation (SDG) for under-documented puzzles. For the certification challenge, however, I will avoid using this material and focus on publicly available data only.

---
### ✅ **Task 4: Retrieval-Augmented Generation (RAG) Strategy**

This project uses a **RAG-based approach** for hint delivery. As described in [Task 3](#task-3-dealing-with-the-data),  hint content is stored in a structured CSV file with metadata fields such as location, puzzle, and hint level. This content is embedded using **OpenAI’s `text-embedding-3-small`** model and stored in a **Qdrant** vector database.

At runtime, Thud attempts to answer player queries by calling a dedicated **LangChain `Tool`** (`"hint_lookup"`), which performs a similarity search over the embedded hint data. This approach mirrors the tool-wrapping strategy used in AIM Homeworks 5 and 6, where RAG is invoked as part of an agentic reasoning loop.

If retrieval fails or the result confidence is low, the system may optionally route the query to a secondary tool (e.g., Fleebix) or simulate a fallback API response.

### 🔁 **Hint Escalation Strategy (Progressive Reveal)**

Thudbot will support a **progressive hinting system**, following a well-established pattern from classic interactive fiction — most notably the Invisiclues format popularized by Infocom.

In this approach:

- The first response to a puzzle-related question returns a **Level 1 hint** — subtle, suggestive, and in-character.
    
- If the player **repeats the question** or follows up with signals like _"more?"_, _"still stuck"_, or rephrasings of the same issue, Thud will respond with the **next level of hint**, progressively becoming more explicit.

Sample logic:

```if new_query == last_query:
    next_hint_level += 1
```
    
- The system will track the **last question ID** and the **last hint level shown**, enabling controlled 


This method allows Thud to remain immersive while giving players just enough help — unless they explicitly ask for more. It also lays the foundation for future expansion, such as more nuanced escalation based on query confidence, character tone, or game state.

---

### ✅ **Task 5: Creating a Golden Test Data Set**

To support evaluation of Thudbot’s retrieval and generation behavior, I will construct a **synthetic “golden” test dataset** aligned with key puzzles and likely player queries from _The Space Bar_. This test set will serve as a baseline for scoring responses using **RAGAS**.

Each test entry will include:
- A **player-style query** (e.g., "How do I get on the bus?")
- A **ground truth reference answer** that represents an ideal hint (e.g., “Thud needs to get the token from the cup.”)
- Optional metadata: e.g. puzzle/location tag, hint level.

The initial golden set will contain ~10–15 Q&A pairs that cover:
- Early-game puzzles
- Ambiguous or multi-step hints
- Known difficult moments (based on Raven’s walkthrough and memory of gameplay)

This test set will be stored as a structured `.csv` or `.jsonl`, ready for:

- Scoring with **RAGAS metrics** (context precision, faithfulness, answer relevance)
- Manual spot checks to ensure tone and character alignment
    

If time permits, I may generate variants of some queries to test retrieval robustness against phrasing changes.

This evaluation scaffold will be reused in Task 7 when comparing baseline RAG vs improved versions.

---

### ✅ **Task 6: Focused Retriever Comparison — Naive vs BM25, Multi-query**

I will compare  **two advanced retrieval methods** to a baseline "naive" retriever, to demonstrate how retrieval quality impacts generation in the Thudbot application.

#### 🔍 **Methods to Compare**

1. **Naive (Dense Vector Search via OpenAI Embeddings + Qdrant)**  
    This is the baseline method used in early prototyping. It supports fuzzy semantic matching but can struggle with short, phrase-based queries and ambiguous terminology.
    
2. **BM25 (Keyword-Based Retrieval)**  
    BM25 ranks results based on exact term overlap and term frequency. It is likely to perform better in this domain because:
    
    - My data consists of short, sentence-level hints, often with specific terminology (e.g., _scanner_, _guard_, _morgue cart_).
        
    - Player queries are often sparse and literal (“How do I get into the bar?”), making keyword overlap valuable.
        
    - The hints are chunked into discrete Q&A rows — well suited for token-matching strategies like BM25.
3. **Multi-query**
	This method generates several semantically varied versions of the user query, retrieves documents for each, and merges the results.

    It is especially well suited to this data set because:

    - Users are likely to use multiple ways of describing the same puzzle.
    - Player input may be vague, overly specific, or use synonyms. Multi-query reduces reliance on a single embedding interpretation.
    - This method compensates for sparse or ambiguous queries by increasing semantic coverage, which is useful when queries contain just 2–3 words.

#### 🧪 **Hypothesis**

> BM25 will provide more accurate, contextually grounded retrieval for Thudbot’s hint data — especially for short, literal player queries — and should outperform naive dense retrieval in both faithfulness and context precision, with only a minor latency tradeoff.
> 
> Multi-query retrieval is expected to perform best overall, as it compensates for ambiguous or underspecified player input by expanding the query space, increasing the likelihood of retrieving a relevant hint even when the original phrasing doesn’t match exactly.

I will use RAGAS and a small golden query set to validate this hypothesis, along with Langsmith to check latency.

These methods will be evaluated  (see Task 7 below) using the golden dataset and RAGAS scoring, to validate the expected gains in precision and relevance.

****

### ✅  Task 7: Assessing Performance

#### Monitoring /Observability with LangSmith 

I plan to use LangSmith tracing to monitor and validate Thudbot’s early behavior.  I will enable trace logging to capture:

- **Prompt/response pairs** for debugging and refinement
- **Latency** metrics to track system responsiveness
- **Token counts and cost** to monitor efficiency

This will allow me to verify that prompts are working as intended and that the system is performing within acceptable bounds.

#### RAG Evaluation with RAGAS

I will begin with a **baseline RAG system** using:
- Standard OpenAI `text-embedding-3-small` embeddings
- Basic cosine similarity search via Qdrant
- Flat chunking strategy (one row per structured hint)

To assess the impact of improved retrieval techniques, I will compare the baseline Naive retriever against BM25  and multi-query retrievers using a shared golden test set of player queries and expected hint outputs.

### 🧪 **Evaluation Method**

- Retrieved documents will be evaluated using **RAGAS**, focusing on **retrieval quality metrics**:
    - **Context Recall** – how often the retrieved passage overlaps with the correct answer context
    - **Noise Sensitivity** – how much irrelevant information is returned
    - **Latency (optional)** – for awareness, but not a priority for this prototype

This evaluation will focus on **retrieval quality metrics**, since the retriever is the variable under test.

### 📊 **Expected Output**

A side-by-side comparison table will summarize performance:

| Retriever   | Context Recall | Entity Recall  | Noise Sensitivity | Latency (s)    |
| ----------- | -------------- | -------------- | ----------------- | -------------- |
| Naive       | _(baseline)_   | (baseline)     | _(baseline)_      | _(measured)_   |
| BM25        | _(expected ↑)_ | _(expected ↑)_ | _(expected ↓)_    | _(expected ↑)_ |
| Multi-query | _(expected ↑)_ | _(expected ↑)_ | (minimal change)  | _(expected ↑)_ |
#### Notes:

- **Context Recall**: BM25 and Multi-query are expected to retrieve more relevant segments due to keyword density or diversified phrasing.
- **Entity Recall**: BM25 better for factual/named items (e.g., object names); Multi-query even more so.
- **Noise Sensitivity**: Naive dense retrieval can over-rely on embeddings and retrieve unrelated content; keyword-based and multi-query methods tend to reduce this.
- **Latency**: Multi-query methods call the retriever multiple times, so higher latency is expected.
--- 

## Appendix A

### ✅ Final Submission Checklist

- [ ] **GitHub Repository** (public or shared link)  
  - [ ] Includes a 5-minute (or shorter) **Loom video** showing a live demo of the app and describing the use case  
  - [ ] Contains a **written design document** that addresses all deliverables and answers all required questions  
  - [ ] Includes **all relevant code** (for prototype, evaluation, etc.)


