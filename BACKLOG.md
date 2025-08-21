# Thudbot 2 - Development Backlog

## Post-Demo Day Improvements

### 🔧 Technical Debt & Architecture



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

#### 4. Frontend Polish & Enhancement
- **Priority**: Low
- **Status**: Pending
- **Description**: Additional UI/UX improvements for the PDA interface
- **Details**: 
  - Add subtle animations (loading states, message transitions)
  - Implement keyboard shortcuts (Enter to send, Escape to clear)
  - Add sound effects for authentic retro experience
  - Mobile responsiveness testing and optimization
  - Accessibility improvements (screen reader support, keyboard navigation)
- **Files**: `src/app/page.tsx`, CSS/styling files
- **Benefit**: Enhanced user experience, broader accessibility, professional polish

#### 5. PDA Interface Expansion
- **Priority**: Low  
- **Status**: Pending
- **Description**: Make other PDA buttons functional for enhanced immersion
- **Details**: 
  - MAP button: Show game world map or current location
  - STASH button: Display inventory or collected items
  - ZOOM button: Adjust chat text size
  - SYSTEM button: Settings/preferences panel
- **Files**: `src/app/page.tsx`, new component files
- **Benefit**: More interactive PDA experience, additional functionality

#### 4. Add State Context for Follow-up Questions
- **Priority**: Medium  
- **Status**: Pending
- **Description**: Enable conversational follow-ups and hint escalation
- **Details**: Support "tell me more", "I'm still stuck", context-aware responses
- **Files**: `src/state.py`, `src/langgraph_flow.py`
- **Benefit**: Better user experience, natural conversations

### 📊 Evaluation & Debugging

#### 5. Dataset Constraint Validation Testing
- **Priority**: Medium
- **Status**: Pending
- **Description**: Implement comprehensive testing for dataset metadata field constraints
- **Details**: 
  - Test `response_must_mention` and `response_must_not_mention` field compliance
  - Validate hint level progression logic within puzzle groups
  - Check content quality metrics (length, specificity, coherence)
  - Verify categorical data consistency and completeness
  - Test edge cases in dataset structure and content
- **Files**: `src/test_dataset_validation.py`, `data/Thudbot_Hint_Data_1.csv`
- **Benefit**: Ensure dataset integrity before implementing progressive hints, catch constraint violations early

#### 6. Evaluate MMR (Maximal Marginal Relevance) for Retrieval Diversity
- **Priority**: Medium
- **Status**: Pending
- **Description**: Test MMR to reduce retrieval bias and improve context diversity
- **Details**: 
  - **Code Change**: In `src/agent.py` line ~100, update retriever:
    ```python
    naive_retriever = vectorstore.as_retriever(
        search_type="mmr",  # Add this
        search_kwargs={"k": 10, "lambda_mult": 0.5}  # Balance relevance vs diversity
    )
    ```
  - **Evaluation Needed**: A/B test against current system using RAGAS framework
  - **Metrics**: Context precision/recall, answer relevance, faithfulness
  - **Risk**: May reduce precision for specific questions while improving vague query handling
- **Benefit**: Address potential whac-a-mole effects from repetitive retrieval patterns

#### 7. Implement Full RAGAS Evaluation
- **Priority**: Low
- **Status**: Pending
- **Description**: Set up comprehensive RAG evaluation with RAGAS framework
- **Details**: Evaluate retrieval relevance, answer faithfulness, context precision/recall
- **Benefit**: Data-driven insights into RAG performance, systematic improvement

### 🛠️ Process & Tooling

#### 8. Create GitHub Issue Tracker
- **Priority**: Low
- **Status**: Pending  
- **Description**: Migrate backlog from markdown to GitHub Issues for better project management
- **Details**: Create issues for each backlog item, set up labels, milestones
- **Benefit**: Better tracking, collaboration, integration with PRs

---

## Completed Items ✅

### PDA Interface Visual Overhaul
- ✅ **Retro Sci-Fi Design** - Complete visual transformation to authentic Space Bar PDA aesthetic
- ✅ **Responsive Layout** - PDA interface scales properly across different screen sizes  
- ✅ **Terminal-Style Chat** - Green monospace text with proper contrast and readability
- ✅ **Clean Input Integration** - Input field and SEND button blend seamlessly with PDA buttons
- ✅ **Status Display** - Small screen shows helpful chat examples and instructions
- ✅ **Image Optimization** - Custom PDA graphics with hidden button areas for clean overlay

### Intent-Based Router System
- ✅ **LLM-based intent classification** - Replace keyword matching with natural language understanding
- ✅ **Character guardrails** - Ensure Zelda stays as Space Bar PDA, not Legend of Zelda princess  
- ✅ **Comprehensive testing** - All scenarios covered (game vs off-topic, guardrails)
- ✅ **Enhanced LangSmith tracing** - Clear input/output visibility for debugging
- ✅ **Canned responses** - Efficient off-topic handling without extra LLM calls

### Technical Architecture Improvements
- ✅ **Complete AgentExecutor → LangGraph Migration** - Removed all vestigial AgentExecutor code for clean LangGraph architecture
- ✅ **RAG Pipeline Diagnostic Logging** - Added comprehensive logging for retrieval and generation steps



### Cache Security Enhancement
- ✅ **SHA-256 Encoder** - Upgraded cached embeddings from SHA-1 to SHA-256 for collision resistance
---

## Notes

- **Demo Day Target**: August 25, 2025
- **Code Freeze Target**: August 21, 2025
- **Current State**: Production ready with smart routing and character integrity
- **Architecture**: LangGraph-based flow with temporary AgentExecutor bridge
- **Focus**: Prioritize user-facing features over technical debt until post-demo

---

*Last Updated: Aug 20, 2025*
