# Thudbot 2 - Development Backlog

## Post-Demo Day Improvements

### 🎯 Progressive Hints Enhancements

#### 1. ✅ Semantic Question Matching for Progressive Hints - COMPLETED
- **Priority**: Medium
- **Status**: ✅ Completed (2025-08-21)
- **Description**: Enhanced progressive hints to escalate on semantically similar questions using keyword matching
- **Implementation**: 
  - ✅ Keyword-based matching with 2+ word overlap threshold
  - ✅ Session persistence for last_question_keywords
  - ✅ Vague escalation logic fixed to reuse previous question
  - ✅ Fallback to exact string matching
- **Result**: Question variants now properly escalate (e.g., "How do I open locker?" → "Why can't I open locker?" = Level 2)

#### 2. Regression Test Verbosity Toggle
- **Priority**: Low
- **Status**: Pending
- **Description**: Add command-line verbosity control to regression test for flexible debugging
- **Current**: Fixed medium verbosity showing search query mismatches
- **Requested**: Toggle between quiet/medium/verbose modes
- **Implementation**: Add argparse with --verbose/-v flag options
- **Options**:
  - `--quiet`: Only final summary
  - `--medium`: Current behavior (search query + basic info)
  - `--verbose`: Full debug output capture
- **Files**: `tests/regression/run_regression.py`
- **Effort**: 15-20 minutes
- **Benefit**: Flexible debugging without code changes

#### 3. Lower LLM Temperature for Demo Consistency
- **Priority**: Medium-High (Pre-Demo)
- **Status**: Pending
- **Description**: Reduce temperature from default 0.7 to 0.1-0.3 for more deterministic responses
- **Root Cause**: Temperature 0.7 adds 30% randomness to verification, character maintenance, and classification
- **Evidence**: "Who is Zelda?" inconsistency likely caused by verification randomness at temp=0.7
- **Target Temperature**: 0.1 for verification, 0.2 for character maintenance (preserve some personality)
- **Files to Update**:
  - `src/verify_correctness_node.py`: `ChatOpenAI(model="gpt-4o-mini", temperature=0.1)`
  - `src/maintain_character_node.py`: `ChatOpenAI(model="gpt-4o-mini", temperature=0.2)`
  - `src/generate_error_message_node.py`: `ChatOpenAI(model="gpt-4o-mini", temperature=0.1)`
  - `src/langgraph_flow.py`: `ChatOpenAI(model="gpt-4.1-nano", temperature=0.1)` (router)
- **Testing**: Re-run "Who is Zelda?" 10 times to verify consistency improvement
- **Effort**: 5-10 minutes
- **Risk**: Very low (easily reversible)
- **Benefit**: Reliable demo behavior, consistent verification results

#### 4. Enhanced Progressive Hints Architecture (Future Refinement)
- **Priority**: Low (Post-Demo)
- **Status**: Design phase
- **Description**: Refactor progressive hints for better separation of concerns and configurability
- **Current Issues**:
  - Router mutates user_input (violates single responsibility)
  - Hard-coded 2+ keyword threshold
  - Mixed classification and query transformation logic
- **Enhanced Architecture**:
  ```
  QueryNormalizer → SimilarityMatcher → EscalationManager → SearchQueryBuilder
  ```
- **Components**:
  - **QueryNormalizer**: Extract keywords, handle stop words
  - **SimilarityMatcher**: Configurable thresholds (keyword count, percentage, semantic)
  - **EscalationManager**: Pure escalation logic, no state mutation
  - **SearchQueryBuilder**: Construct search queries for downstream nodes
- **Configuration Options**:
  - Similarity thresholds (keyword count, percentage)
  - Stop word lists per domain
  - Escalation strategies (linear, exponential, topic-specific)
- **Benefits**:
  - Testable components, better maintainability
  - Configurable without code changes
  - Support for multiple similarity algorithms
  - Clean separation of concerns
- **Effort**: 2-3 hours
- **Alternative**: Consider semantic similarity with local embeddings (sentence-transformers)

**Implementation Plan:**
1. **Create keyword extraction function** in `src/langgraph_flow.py`:
   ```python
   def extract_question_keywords(user_input: str) -> set:
       # Extract key game entities from normalized text
       # Use domain vocabulary from CSV data
   ```

2. **Enhance router logic** in `src/router_node.py`:
   - Replace exact string matching with keyword overlap detection
   - Use 50%+ keyword overlap threshold for escalation
   - Store `last_question_keywords` in state instead of `last_question_id`

3. **Update state management** in `src/state.py`:
   - Add `last_question_keywords` field to LangGraphState

4. **Game entity vocabulary** (extracted from existing CSV):
   - token, bus token, locker, vestibule, zelda, quantelope, lodge
   - residue printer, box, plane, door, hyperdrive, treasure, money

5. **Expected improvements**:
   - "How do I open a locker?" + "Why can't I open locker?" → Proper L1→L2 escalation
   - "How do I find token?" + "Where is the bus token?" → Proper L1→L2 escalation
   - Maintains reset behavior for genuinely different topics

6. **Testing**: Use existing manual test scenarios that showed reset behavior
7. **Fallback**: Keep exact string matching as backup for edge cases

### 🔧 Technical Debt & Architecture

#### 1. LLM Model Optimization Testing
- **Priority**: Low-Medium
- **Status**: Pending
- **Description**: Test nano vs mini model performance on remaining LLM nodes for cost/speed optimization
- **Background**: Router node successfully converted from mini to nano (30% faster, 100% accurate, cost savings)
- **Remaining Nodes to Test**:
  - Verification node (`src/verify_correctness_node.py`) - Currently mini
  - Character maintenance node (`src/maintain_character_node.py`) - Currently mini
  - Note: MultiQuery already uses nano
- **Approach**: Use `tests/test_router_only.py` as template for node-specific testing
- **Success Criteria**: Maintain accuracy while reducing costs
- **Future Context**: May become obsolete if migrating to local SLMs
- **Files**: `src/verify_correctness_node.py`, `src/maintain_character_node.py`
- **Benefit**: Further cost reduction and speed improvements on 2/4 remaining mini calls

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

#### 5. Verification System Calibration - "Who is Zelda" Inconsistency
- **Priority**: Medium-High
- **Status**: Pending
- **Description**: Fix inconsistent verification results for character/meta questions like "Who is Zelda?"
- **Problem**: Question retrieves correct chunk (TSB-007) but verification randomly fails ~33% of time with "HALLUCINATED" verdict
- **Root Cause**: Verification prompt too strict for character questions; LLM non-determinism in borderline cases
- **Approach**: 
  1. Enhance verification prompt to handle character/meta questions explicitly
  2. Add secondary verification check for cases with good context but HALLUCINATED verdict
  3. Consider question type classification pre-verification
- **Files**: `src/verify_correctness_node.py`, verification prompts
- **Testing**: Use `tests/regression/run_regression.py` to validate consistency improvements
- **Success Criteria**: "Who is Zelda" should have >95% consistent verification results
- **Benefit**: Reliable system behavior, better user experience for character questions

**Starter Prompt for Future Thread:**
```
I need to fix the verification system calibration issue where "Who is Zelda?" gets inconsistent verification results (passes ~67% of time, fails with HALLUCINATED ~33% of time). The question correctly retrieves chunk TSB-007 but verification is inconsistent. 

Current symptoms:
- Question: "Who is Zelda?" 
- Retrieval: Working correctly (gets TSB-007)
- Verification: Inconsistent VERIFIED vs HALLUCINATED
- Pattern: Character/meta questions affected

I have a regression tester at tests/regression/run_regression.py ready for validation. Please examine src/verify_correctness_node.py and suggest systematic fixes (not one-offs) to improve verification consistency for character questions.
```

#### 6. Dataset Constraint Validation Testing
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

#### 9 Future Enhancement: Topic-Specific Hint Level Tracking

**Current Behavior:** Single hint level counter that resets when user asks about a different topic.
- User: "How do I find the token?" → level 1
- User: "How do I open the locker?" → level 1 (new topic, counter resets)
- User: "I'm still stuck" → level 2 (about locker)
- User: "How do I find the token?" → level 1 (back to token, counter resets)

### **Enhancement:** Track hint levels per semantic topic to maintain escalation history across topic switches.
- Would require: Question normalization (LLM), per-topic hint tracking, vague prompt topic resolution
- Estimated effort: 3-4 hours
- Value: Handles edge cases where users switch between topics and return to previous questions
- Priority: Low (current approach works for 90% of conversations)


#### Data Cleanup: Fix Duplicate question_ids
- **Issue:** question_id column has duplicates (TSB-026 appears 3x, should be TSB-026a, TSB-026b, TSB-026c)
- **Impact:** Low - puzzle_id grouping works correctly for progressive hints
- **Priority:** Post-demo cleanup
- **Effort:** 30 minutes to regenerate unique IDs and validate
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
