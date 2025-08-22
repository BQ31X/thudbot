### AI Makerspace assignment: DemoDay


1. Due Tuesday August 26 (currently Sunday 8/17)
2. Needs to be publicly hosted

### Noteworthy changes from V1 (certification challenge (cc) version)
Shift from Thud to Zelda as main character
Conversion to LangGraph
Separation of roles across multiple nodes / agents

Deprecate: Weather function; any reference to web searching

## Task 1: Defining your Problem and Audience


---
## ✅ Problem Statement

Imagine you are playing _The Space Bar_, the cult-classic sci-fi adventure game from Boffo Games. You've been interrogating bizarre alien suspects for hours, and now you’re stuck on a puzzle that makes sense only if you understand how a Sraffan thinks after four Margaritas. Frustrated, you alt-tab to the internet… only to find scattered walkthroughs, spoiler-heavy guides, or dead links.



## ✅ Audience

The audience for this application includes fans of _The Space Bar_ and similar puzzle-rich games. These players appreciate immersive storytelling, quirky characters, and solving challenges organically. They don’t want to break immersion or read line-by-line walkthroughs with spoilers. They want subtle, diegetic clues, i.e., in-character clues that feel like they belong _inside_ the game world. My application brings that experience to life, by having Zelda (a well-known in-game character) offer hints in their original voice, keeping the magic, and the challenge, of the game intact.

---
## Task 2: Propose a Solution
### ✅ Proposed Solution

Thudbot is a web-based character agent who will live at boffo.games and provide immersive in-universe puzzle hints for _The Space Bar_, speaking in the distinctive character style of Zelda. In the game, Zelda is the persona that inhabits the player characters "Personal Digigal Assistant (PDA), and one of the first non-player characters you meet in game. Instead of breaking immersion with walkthroughs, players can chat directly with Zelda, who responds using a mix of structured hint data and in-character commentary. When a player types a question, Thudbot first checks a structured database of known puzzle hints and responds in her signature style. If he’s stumped, Thud may consult his gruff colleague Fleebix (simulated via fallback logic*). The result is an immersive, interactive hint system that feels like part of the game itself.

The experience is designed to feel like talking to an NPC from within the game. Over time, this foundation can scale to support other characters, games, or even serve as a demo for AI-powered NPCs in retro or indie titles.



---



### ✅ **Agentic Reasoning Usage**

- **Primary agent**: Zelda, with personality and limited knowledge.
    
- **Future expansion**: Additional agents to represent other game characters.


--- 

### ✅ **Task 3: Dealing with the Data**

#### 1. **Describe all of your data sources and external APIs, and describe what you’ll use them for.**

- **Data Source #1: Public walkthroughs and fan-written hint content**  
    Play through the game to generate questions and answers. This data will be chunked, embedded, and used as the knowledge base for RAG-style retrieval when players ask Thudbot for help.
    The data has been structured into a custom CSV file containing **discrete hint entries**, each tagged with metadata fields such as:

	- Puzzle or location
	- Hint level (e.g., subtle, moderate, full solution)
	
    
This format enables easier chunking, embedding, and retrieval based on player intent and desired hint granularity.
    
- **Data Source #2: Original game design documents (private)**  
    I have access to the internal design docs from the original game development process. These contain valuable insight for hint generation, and character personalities, for potential future expansion. However, I will **not include them** in the prototype or RAG system for the certification challenge due to IP sensitivity and privacy concerns. Long-term, I plan to incorporate this material by self-hosting a small language model such as **Phi-2 via Ollama**. Because the retrieval task is narrow in scope a small local model should be sufficient.
    
- **External APIs:**  
    I plan to use the **OpenAI API (GPT-4-turbo and text-embedding-3-small)** for generation and retrieval. I may later replace these with self-hosted models for privacy or cost reasons.
    

---



#### 2. **Describe the default chunking strategy that you will use. Why did you make this decision?**

### 🔍 Embedding & Chunking Strategy (Design Plan)

To support semantic search over puzzle hint data, I initially considered chunking freeform walkthrough text into short Q&A-style blocks or ~100–200 word passages. This would have aligned with how players typically request help — by referencing specific puzzles, locations, or characters (e.g., “How do I get past the security guard?”). I explored approaches like manual segmentation or LangChain’s `RecursiveCharacterTextSplitter` to divide text along natural language boundaries.

However, I quickly realized that license-safe, unstructured walkthrough content was limited for this game. As a result, I decided to pivot to a **structured data approach** using a custom CSV file. Each row in the file will represent a single hint, along with associated metadata fields such as `game_section`, `puzzle_name`, and `hint_level`.

This will allow me to chunk the data semantically — one row per embedding — and use the `hint_text` field as the document content. I plan to embed each document using OpenAI’s `text-embedding-3-small` model and store them in a **Qdrant vectorstore**. Metadata fields will be preserved for later use in filtering and evaluation.

This design supports:

- High-precision retrieval with metadata-aware filtering (e.g., retrieve only hints from a specific scene)
- Controlled escalation of hint levels
- Reuse of familiar LangChain components, including `CSVLoader` and `Qdrant.from_documents`, based on prior AIM homework patterns

Overall, this strategy provides clean separation between content, structure, and logic, while keeping the retrieval pipeline lightweight and explainable.

#### 3. **[Future] Will you need specific data for any other part of your application? If so, explain.**

Eventually, I want to use the internal design documents to fine-tune the personality or logic of Fleebix, or to seed synthetic data generation (SDG) for under-documented puzzles. For the certification challenge, however, I will avoid using this material and focus on publicly available data only.

---
### ✅ **Task 4: Retrieval-Augmented Generation (RAG) Strategy**

This project uses a **RAG-based approach** for hint delivery. As described in [Task 3](#task-3-dealing-with-the-data),  hint content is stored in a structured CSV file with metadata fields such as location, puzzle, and hint level. This content is embedded using **OpenAI’s `text-embedding-3-small`** model and stored in a **Qdrant** vector database.


**UPDATE THIS SECTION**
At runtime, Thudbot attempts to answer player queries by calling a dedicated **LangChain `Tool`** (`"hint_lookup"`), which performs a similarity search over the embedded hint data. This approach mirrors the tool-wrapping strategy used in AIM Homeworks 5 and 6, where RAG is invoked as part of an agentic reasoning loop.



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


This method allows Thudbot to remain immersive while giving players just enough help — unless they explicitly ask for more. It also lays the foundation for future expansion, such as more nuanced escalation based on query confidence, character tone, or game state.