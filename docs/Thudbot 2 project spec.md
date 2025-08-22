Gemini 8/17/25
### **Final Project Specification: ZeldaBot**

This document serves as a consolidated plan for the _The Space Bar_ final project, outlining a clear path for the initial Demo Day deadline and a set of stretch goals for future development. This document is the single source of truth for all development.

---

### **1. Project Goal**

The primary objective is to enhance the existing RAG pipeline to create an intelligent, character-driven hint system for _The Space Bar_. The "Thud" character will be replaced by "Zelda," a smart but irreverent secretary. The core enhancements are **conversational memory**, **progressive hint escalation**, and robust error handling to prevent ungrounded responses. The project will leverage the LangGraph framework for a clear, modular, and debuggable architecture.

---

### **2. LangGraph Architecture & State Management**

The system will operate as a stateful LangGraph. This architecture is designed to be extensible, with the core flow being simple for the initial prototype and a more complex, robust version as a stretch goal.

#### **Initial Plan (Demo Day Prototype)**

The graph will use a simplified flow, prioritizing a working, clean prototype for the deadline. This approach incorporates the TA's suggestion to remove the retry loop for clarity, but includes the progressive hint escalation feature.

- **User Input** enters the system.
    
- A **Router Node** first checks if the user's current query is a repeat of the `last_question_id` stored in the state.
    
- **If it's a new query**, the router updates the `last_question_id`, resets the `hint_level` to 1, and proceeds to the **Find Hint Node Agent**.
    
- **If it's a repeat query**, it routes to a **Hint Escalation** path. This path immediately increments the `state['hint_level']` and proceeds to the **Find Hint Node Agent**.
    
- The **Find Hint Node Agent** performs multi-query retrieval from the Qdrant vector store, using the current `hint_level` to retrieve a progressively more explicit hint.
    
- The retrieved hint is passed to a **Verify Correctness Node Agent**, which acts as a fact-checker to prevent hallucinations.
    
- If the hint is correct, it is sent to a **Maintain Character Node Agent**, where an LLM rewrites it in Zelda's voice.
    
- The final hint is formatted by a **Format Output** node and sent directly to the user.
    
- If the hint is incorrect, the graph routes directly to a **Generate Error Message Node**. This node will provide a final, canned error message to the user, prompting them to rephrase their query. (in future state, there will be a retry loop here)
    

LangGraph State:

The graph's state will be a central object passed between nodes to manage necessary context. For the initial plan, this includes:

- `chat_history`: A list of messages for conversational awareness and context.
    
- `last_question_id`: A unique identifier for the last question asked, used to track repeated queries.
    
- `hint_level`: An integer that increases on repeated questions to signal the `Find Hint Node` to retrieve a less subtle hint.
    

---

### **3. Data Specification**

The project will use the `Thudbot_Hint_Data_1.csv` file, which requires cleaning to improve RAG performance and reduce hallucination risk.

- **Clean Blanks**: Replace blank values in `planet`, `location`, and `puzzle_name` with a key like `"General"` or `"Meta"`.
    
- **Consolidate Columns**: Fill the `speaker` column with `"Zelda"` for all hints. The `tone` column should be filled with relevant values (e.g., `"Irreverent"`) to guide the "Maintain Character" node.
    
- **RAGAS Evaluation**: To combat hallucinations, RAGAS will be used to measure the `faithfulness` of the pipeline. A manual, on-demand test script will be created to run evaluations before the final demo.
    

---

### **4. Technical Stack**

- **Orchestration**: LangGraph
    
- **LLM**: GPT-4-turbo via OpenAI API
    
- **Embedding Model**: `text-embedding-3-small` (OpenAI)
    
- **Vector Database**: Qdrant (in-memory for the prototype)
    
- **Observability**: LangSmith
    

---

### **5. Character Persona Prompting**

The "Maintain Character" node will be driven by a clear prompt for the LLM. The prompt should combine a short, descriptive summary of Zelda with 3-5 concrete dialogue examples from the game to provide a clear and consistent voice. This approach avoids the need for using sensitive, private design documents.

---

### **6. Initial Plan vs. Stretch Goals**

| Feature                    | Initial Plan (Demo Day MVP version)                         | Stretch Goals (Post-Demo)                                                                                                                        |
| -------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| **LangGraph Architecture** | Simplified flow; no retry loop for bad hints.               | **Full Loop**: A more robust LangGraph with a retry counter and a loopback to try and find a better hint before giving up on a failed retrieval. |
| **Error Handling**         | A single, canned message for all hint retrieval failures.   | Optional: The system attempts to re-query with a more permissive prompt before delivering a final failure message.                               |
| **Hint Escalation**        | Based on user re-queries and the `hint_level` in the state. | Based on user re-queries.                                                                                                                        |
| **Testing**                | Manual, on-demand RAGAS evaluation script.                  | (Future) Automated RAGAS evaluations integrated into a full CI/CD pipeline.                                                                      |
| **Multi-Character**        | futre only                                                  | Build out a multi-character agent crew with a router node to direct the user to the correct agent (e.g., Fleebix).                               |
| **Data Privacy**           | Uses only public data; a public LLM.                        | Use a self-hosted LLM (e.g., Phi-2 via Ollama) to incorporate sensitive, private game design documents into the RAG pipeline.                    |

---

### State Management

The graph's state will be a central object (e.g., a dictionary or `TypedDict`) that is passed between nodes. This will manage all necessary context:

- **`chat_history`**: A list of messages for conversational awareness and context.
    
- **`retries`**: An integer to track the number of failed hint attempts for the current query. This will be incremented in the `Generate Error Message` node.
    
- **`hint_level`**: An integer that increases on repeated questions to signal the `Find Hint Node` to retrieve a less subtle hint.

### State management example

from typing import TypedDict, List
from langchain_core.messages import BaseMessage

class LangGraphState(TypedDict):
    """
    Represents the state of our LangGraph.

    Attributes:
        chat_history: A list of messages that represents the conversation history.
        retries: An integer to track the number of failed hint attempts.
        hint_level: An integer to track the current hint level (1 for subtle, 2 for moderate, etc.).
        last_question_id: A unique identifier for the last question asked.
    """
    chat_history: List[BaseMessage]
    retries: int
    hint_level: int
    last_question_id: str

---

### How Nodes Interact with the State

Each node in your LangGraph will receive the `state` as an input and can modify it. This is how you implement memory, logic, and control flow.

1. **Router Node:**
    
    - **Logic**: Your `Router Node` will read `state["chat_history"]` and `state["last_question_id"]` to check for repeated questions or signals like "still stuck".
        
    - **Action**: If the user repeats the question, it will increment `state["hint_level"]` to trigger the next level of hint escalation. If it's a new question, it will reset the hint level to 1 and update the `last_question_id`.
        
2. **Find Hint Node (Tool):**
    
    - **Logic**: This node will use the value of `state["hint_level"]` to filter the search in your Qdrant vector store. You can add a metadata filter to the retrieval call that only returns documents with the matching `hint_level`.
        
3. **Generate Error Message Node:**
    
    - **Logic**: As we discussed, this node is where your retry logic lives. It will read `state["retries"]`.
        
    - **Action**: It will increment the retry counter (`state["retries"] += 1`). If the counter is below your set limit, it will return a signal to loop back to the `Router Node`. If the limit is reached, it will return a different signal to end the conversation.
        

By using this `LangGraphState` object, you can seamlessly pass all the necessary information between nodes, allowing your agent to "remember" the conversation's context and make informed decisions at each step. This approach aligns perfectly with your original plan to track the last question and hint level to enable progressive hints.

--- 

Generate Error Message: 


- **`Generate Error Message` Conditional Edge:** By having a conditional edge here, the node can check the retry counter and make a local decision.
    
    - **If `retries < limit`**: The node returns a signal (e.g., `"retry"`) that directs the graph to the `Find Hint Node Agent`. This is a clean way to loop back to the start of the RAG process without going all the way to the top-level router. The `Find Hint Node Agent` would need to check the state to see that it's a retry and should, therefore, get a different hint.
        
    - **If `retries == limit`**: The node returns a signal (e.g., `"end"`) that directs the graph to a final `Respond to User` node, where the canned error message is displayed.
        

This is a perfectly consistent design. If the `Format Output` node is the clean exit for a successful run, the `Generate Error Message` node becomes the clean exit for a failed run.

**MVP solution:** effectively make the retry limit 1; and have the generate error message node go directly back to the user to ask for more information
### Recommended Approach

Instead of a generic "I can't help with that," the message should feel like Zelda's final, slightly exasperated response.

1. **Acknowledge the effort:** Start by acknowledging the attempts that have been made.
    
2. **Maintain character:** The response should be in Zelda's voice. A touch of irreverence or a snappy, dismissive tone can work well.
    
3. **Provide an alternative:** Offer a suggestion for what the user can do next, such as "try rephrasing your question" or "ask a different question." This prevents the conversation from ending abruptly.
    

**Example Messages:**

- "Look, I’ve given it the old college try, but I’m just not getting a read on this puzzle. Maybe try asking in a completely different way? It's your brain, boss."
    
- "My database is coming up empty, and my magic 8-ball says 'Reply Hazy, Try Again Later.' I'm stumped. Let's move on to the next topic."


--- 

### Explanation of futre character Extensibility

This structure is highly extensible. The core pattern remains the same, but the system now has a new entry point that makes a routing decision based on the user's intent.

- **Character Router Node**: This is a new **agentic** node that uses an LLM to determine which character the user is addressing. It will need access to the conversation history to understand context. For example, a query like "Zelda, what's a hint for this puzzle?" would route to the Zelda sub-graph, while "Hey Fleebix, what do you think?" would go to the Fleebix sub-graph.
    
- **Character Sub-Graphs**: Each character's logic is self-contained within a dedicated sub-graph. This means that Zelda's personality, hints, and tools are completely separate from Fleebix's. This modularity is a huge benefit:
    
    - **Independent Development**: You can work on each character's behavior and knowledge base without affecting the others.
        
    - **Scalability**: Adding a new character is as simple as creating a new sub-graph and adding a new edge from the `Character Router` to it.
        
    - **Customization**: Each sub-graph can have a unique set of tools, allowing a future character to, for example, access a different knowledge base or even a different type of external API.

Yes, you could absolutely "wrap" each subgraph as an agent. This is a powerful and very common pattern in LangGraph. This concept is often referred to as Agent-to-Agent (A2A) communication or creating a "crew" of agents.

### How it Works

Instead of having a flat graph with many nodes, you would define each character's entire sub-graph (e.g., the `Find Hint` -> `Verify` -> `Maintain Character` flow) as a single, callable agent.

The top-level `Character Router` would then act as a meta-agent or orchestrator. Its job is not to call specific tools, but rather to decide which **character agent** to "delegate" the task to.

Your LangGraph would then look something like this:

### Benefits of this Approach

- **Clean Abstraction**: Each character's logic is fully encapsulated. You don't need to know the internal workings of the "Zelda Agent" when you're working on the `Character Router`. You just need to know how to call it.
    
- **Encapsulation and Modularity**: This is the core benefit. You can independently develop and test the `Zelda Agent` without affecting the `Fleebix Agent` or the `Character Router`.
    
- **Scalability**: Adding a new character (`Bob Agent`) is a simple matter of creating a new sub-graph and adding a routing decision for it. You aren't adding a lot of complexity to the main graph.
    
- **Easier Reasoning**: The `Character Router` agent's job becomes much simpler. Its prompt is focused purely on identifying the right agent based on the user's input, rather than deciding on a specific tool call.



- Query successful
    

That image is a much better representation of the LangGraph flow, as it correctly shows the loopback from `Generate Error Message` directly to the `Router Node` at the top of the graph.

To add a loop/counter on the "Generate Error Message" node, it would be handled **within the node itself**. This is a logical check that happens _before_ the node returns to the `Router`.

---

### How the Retry Counter Works

The counter for the loop is managed as part of the LangGraph's state. When a user's query leads to an error state, the `Generate Error Message` node would perform a few actions:

1. **Read State:** Check the current retry count from the graph's state object.
    
2. **Conditional Logic:**
    
    - If the retry count is **below a set limit** (e.g., 3), the node would:
        
        - Increment the counter.
            
        - Generate a friendly error message for the user.
            
        - Return a value that tells the graph to route back to the `Router Node`.
            
    - If the retry count has **reached the limit**, the node would:
        
        - Generate a final, definitive failure message (e.g., "I'm sorry, I can't help with that puzzle right now.")
            
        - Return a value that directs the graph to an `end` state, preventing it from looping forever.
            

This counter is an internal mechanism of the node, not a separate conditional edge on the diagram. It's a way of programmatically controlling the `No` path of the conditional edge coming from "Is the hint correct?" to prevent an infinite loop.

--- 
RAGAS eval (stretch goal)

RAGAS is powerful for one-off evaluations, but its real value comes from a repeatable, automated process. You want to avoid manually running tests every time you make a change to your code, your prompts, or your data. The goal is to set up a system that continuously evaluates your RAG pipeline to ensure new changes don't introduce regressions like more hallucinations.

### The Solution

You can automate RAGAS evaluations with a simple script that runs on every new commit to your project. This script would:

1. **Generate a Test Dataset**: Create a small, representative test dataset of questions and ground truth answers. This is the most crucial part. The dataset should cover a range of your puzzles and hint levels.
    
2. **Run the RAG Pipeline**: Use your new LangGraph code to process the questions from the test dataset. The script would record the generated answers and the retrieved contexts for each question.
    
3. **Run RAGAS**: Pass the generated answers, retrieved contexts, and ground truth answers to the RAGAS evaluation suite.
    
4. **Publish Results**: The script saves the RAGAS faithfulness score and any other metrics to a file or a simple dashboard.
    
5. **Set a Quality Gate**: Implement a quality gate that fails the build if the RAGAS faithfulness score drops below a certain threshold (e.g., 0.95).
    

Your project already has a `check_and_commit.sh` script, which is the perfect place to integrate this. You would add a step to the script that runs your RAGAS evaluation after your unit tests pass, preventing a commit if the faithfulness score is too low.

This automated process ensures that every change you make to the pipeline is a step forward, not a step back.

It seems like you're feeling a bit overwhelmed by the idea of setting up a full CI/CD pipeline, and you're wondering if it's something you can skip for your upcoming demo day.

You're absolutely right that a full, automated CI/CD pipeline is a significant project in itself, and it's a great "stretch goal" for after your deadline. The core value for your mid-term project is demonstrating the key concepts you've learned. You can get most of the benefits of RAGAS evaluation without building a full pipeline.

### The "Good Enough" Plan for Demo Day

For your demo day deadline, you can use a manual, but repeatable, process. The goal is to be able to run an evaluation on-demand and have a clear number to show that your changes have improved the system.

1. **Create a dedicated test script:** Write a Python script, separate from your main application, that is specifically for RAGAS evaluation. This script will:
    
    - Load your test dataset.
        
    - Run your RAG pipeline over the test dataset.
        
    - Generate and save the RAGAS faithfulness score.
        
2. **Manually run the script:** Before your demo, or whenever you make a significant change, run this script from your terminal. This gives you a performance score you can cite in your presentation.
    
3. **Prepare a test set:** As we discussed, a small, high-quality test set is crucial. It should contain questions that are known to cause hallucinations in your current system. This allows you to specifically show how your new `Verify Correctness` node fixes the problem.
    

This approach gives you the necessary evidence of your project's performance without the complexity of a full, automated pipeline. You can discuss the full CI/CD pipeline in your presentation as a planned future enhancement.

### Note about agents and tools

Of the nodes in the LangGraph, the following are agents because they use a large language model (LLM) for reasoning:

Find Hint Node Agent: While it uses a tool (the vector store retriever), it's considered an agent because it uses an LLM to generate the query or queries for retrieval.

Verify Correctness Node Agent: This node's entire purpose is to use an LLM to reason about the validity and relevance of the retrieved text.

Maintain Character Node Agent: This node relies on an LLM to perform a core reasoning task: rewriting the text to fit a specific persona.

The other nodes are not agents because their functionality is based on pre-defined, non-LLM logic:

Router Node: A simple conditional check based on a rule (is it a hint request?).

Generate Error Message Node: Uses simple conditional logic and a counter, not an LLM.

Format Output Node: A simple chain that formats a string.

Respond Directly and Respond to User: These are final output nodes, not agents.