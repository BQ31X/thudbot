# Thudbot 2 - Development Backlog

## Post-Demo Day Improvements

### 🔧 Technical Debt & Architecture

#### 1. Complete AgentExecutor → LangGraph Migration
- **Priority**: Low
- **Status**: Pending
- **Description**: Remove vestigial AgentExecutor from `find_hint_node` for cleaner architecture
- **Details**: Currently using hybrid approach - LangGraph nodes calling old AgentExecutor chain
- **Files**: `src/agent.py`, `src/langgraph_flow.py`
- **Benefit**: Cleaner code, faster execution, full LangGraph architecture

#### 2. Externalize LLM Model References  
- **Priority**: Low
- **Status**: Pending
- **Description**: Make LLM models configurable instead of hardcoded
- **Details**: Currently hardcoded `gpt-4o-mini` in multiple places
- **Files**: `src/langgraph_flow.py`, configuration files
- **Benefit**: Easy model swapping, cost optimization, testing flexibility

### 🚀 Feature Enhancements

#### 3. Dynamic Status Display in PDA Small Screen
- **Priority**: Low
- **Status**: Pending
- **Description**: Replace static instructions with real-time status information in PDA small screen
- **Details**: Show live activity like "Zelda: Online", "Processing...", message counts, timestamps, connection status
- **Files**: `src/app/page.tsx`
- **Benefit**: More authentic PDA feel, real-time feedback, dynamic interface

#### 4. Add State Context for Follow-up Questions
- **Priority**: Medium  
- **Status**: Pending
- **Description**: Enable conversational follow-ups and hint escalation
- **Details**: Support "tell me more", "I'm still stuck", context-aware responses
- **Files**: `src/state.py`, `src/langgraph_flow.py`
- **Benefit**: Better user experience, natural conversations

### 📊 Evaluation & Debugging

#### 4. Add RAG Pipeline Diagnostic Logging
- **Priority**: Medium
- **Status**: Pending
- **Description**: Add intermediate logging to identify retrieval vs generation issues
- **Details**: Log retrieved documents, context quality, and response generation steps
- **Files**: `src/agent.py` (hint_lookup function)
- **Benefit**: Quick debugging without full RAGAS evaluation, identify pipeline bottlenecks

#### 5. Implement Full RAGAS Evaluation
- **Priority**: Low
- **Status**: Pending
- **Description**: Set up comprehensive RAG evaluation with RAGAS framework
- **Details**: Evaluate retrieval relevance, answer faithfulness, context precision/recall
- **Benefit**: Data-driven insights into RAG performance, systematic improvement

### 🛠️ Process & Tooling

#### 6. Create GitHub Issue Tracker
- **Priority**: Low
- **Status**: Pending  
- **Description**: Migrate backlog from markdown to GitHub Issues for better project management
- **Details**: Create issues for each backlog item, set up labels, milestones
- **Benefit**: Better tracking, collaboration, integration with PRs

---

## Completed Items ✅

### Intent-Based Router System
- ✅ **LLM-based intent classification** - Replace keyword matching with natural language understanding
- ✅ **Character guardrails** - Ensure Zelda stays as Space Bar PDA, not Legend of Zelda princess  
- ✅ **Comprehensive testing** - All scenarios covered (game vs off-topic, guardrails)
- ✅ **Enhanced LangSmith tracing** - Clear input/output visibility for debugging
- ✅ **Canned responses** - Efficient off-topic handling without extra LLM calls

---

## Notes

- **Demo Day Target**: August 25, 2025
- **Current State**: Production ready with smart routing and character integrity
- **Architecture**: LangGraph-based flow with temporary AgentExecutor bridge
- **Focus**: Prioritize user-facing features over technical debt until post-demo

---

*Last Updated: January 18, 2025*
