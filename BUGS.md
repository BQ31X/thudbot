# 🐛 Known Issues & Bug Tracker

*Last Updated: August 5, 2025*

## 🚨 Demo Blockers (Avoid for Certification Video)

### Agent Clarification Failures
**Issue:** When agent needs clarification from user, it has no interactive mechanism  
**Impact:** Leads to wrong tool selection or 500 errors  
**Trigger:** Ambiguous questions like "How do I get the token?" (no specific context)  
**Workaround:** Use specific questions with clear context  
**Status:** Known limitation of current agent framework  

**Examples to avoid:**
- ❌ "How do I get the token?" → triggers clarification loop
- ❌ "What's the weather?" → missing location parameter
- ❌ "Help me with the game" → too vague

---

## 🔧 Post-Certification Improvements

### Weather Tool Error Handling
**Issue:** `get_weather()` tool doesn't handle missing/invalid locations gracefully  
**Impact:** Agent loops until iteration limit when no city specified  
**Priority:** Medium  
**Solution:** Add default location or better validation  

### Agent Tool Selection Refinement  
**Issue:** Agent sometimes chooses wrong tool for borderline questions  
**Impact:** User gets weather when expecting game help, or vice versa  
**Priority:** Low  
**Solution:** Improve tool descriptions and prompts  

### UI Error State Improvements
**Issue:** Frontend shows generic "An error occurred" for all backend failures  
**Impact:** Poor user experience during debugging  
**Priority:** Low  
**Solution:** Parse specific error types and show helpful messages  

### Environment Setup Complexity
**Issue:** `uv sync` doesn't reliably install all dependencies  
**Impact:** Requires manual `uv pip install fastapi uvicorn` workaround  
**Priority:** Low (dev environment only)  
**Solution:** Investigate pyproject.toml vs requirements.txt conflicts  

---

## ✅ Fixed Issues

### Tool Registration Bug *(Fixed: 2025-08-05 09:00)*
**Issue:** Agent only saw `hint_lookup` tool, not `get_weather`  
**Cause:** Missing `get_weather` in tools list initialization  
**Fix:** Added to `tools = [hint_lookup, get_weather]` in agent.py  
**Verification:** Weather queries now correctly route to weather API  

### UI Auto-Scroll *(Fixed: 2025-08-05 09:30)*
**Issue:** Chat responses appeared "below the fold" requiring manual scroll  
**Impact:** Poor demo experience, users couldn't see responses  
**Fix:** Added useRef + useEffect for smooth auto-scroll to latest message  
**Verification:** UI now auto-scrolls on new messages and loading states  

### Import Path Resolution *(Fixed: 2025-08-05 09:15)*
**Issue:** `ImportError: attempted relative import with no known parent package`  
**Cause:** Running script directly vs as module affects import resolution  
**Fix:** Ensured proper virtual environment activation sequence  
**Verification:** Backend starts cleanly with `uv run python src/api.py`  

### Sample Question Updates *(Fixed: 2025-08-05 09:45)*
**Issue:** UI sample questions included problematic examples  
**Fix:** Updated to demo-safe questions:
- "How do I get the token from the cup?" (proven working)
- "How do I use the voice printer" (specific game mechanic)  
- "What's the weather in Boston?" (location specified)
**Verification:** All sample questions work reliably  

---

## 🧪 Testing Notes

### Reliable Test Questions
✅ **Game hints:**
- "How do I get the token from the cup?"
- "How do I use the voice printer?"
- "What should I do at the bar?"

✅ **Weather queries:**
- "What's the weather in Boston?"
- "How's the weather in Bermuda?"

### Known Problematic Patterns
❌ **Vague game questions:** "Help me" / "I'm stuck" / "What do I do?"  
❌ **Location-less weather:** "What's the weather?" / "Is it nice out?"  
❌ **Ambiguous tokens:** "How do I get the token?" (which token?)  

---

## 📋 Development Practices

### Bug Triage Process
1. **Demo Blocker:** Avoid in certification video
2. **High Priority:** Fix before public deployment  
3. **Medium Priority:** Address in next development cycle
4. **Low Priority:** Technical debt / nice-to-have improvements

### Issue Resolution
- **Document trigger conditions** for reproducible bugs
- **Include workarounds** for known limitations  
- **Track verification steps** for confirmed fixes
- **Maintain testing examples** for regression prevention

---

## 🎯 Demo Day Preparation

**Pre-Recording Checklist:**
- [ ] Test all sample questions work correctly
- [ ] Verify auto-scroll behavior  
- [ ] Confirm both tools (hint_lookup + get_weather) are accessible
- [ ] Practice specific, unambiguous questions only
- [ ] Have backup questions ready if one fails

**Safe Demo Script:**
1. Show game hint: "How do I get the token from the cup?"
2. Show weather tool: "What's the weather in Boston?" 
3. Show another game hint: "How do I use the voice printer?"
4. Demonstrate UI auto-scroll and responsiveness

---

*This bug tracker demonstrates systematic issue management and professional development practices for the Thudbot certification project.*