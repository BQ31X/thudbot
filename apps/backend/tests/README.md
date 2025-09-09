# Thudbot Test Suite Guide

## 🎯 Quick Start (You'll Want This Tomorrow)

### **Primary Regression Testing (Recommended)**
```bash
# Run the simple, no-interpretation regression test
python tests/regression/run_regression.py

# Results automatically saved to:
# - tests/regression/results/regression_YYYYMMDD_HHMMSS.csv (raw data)
# - tests/regression/results/regression_YYYYMMDD_HHMMSS.md (human readable)
# - tests/regression/results/latest_regression.csv (symlink to newest)
```

### **Custom Test Questions**
```bash
# Edit test questions
nano tests/regression/test_questions.csv

# Quick 3-question test
python -c "
from tests.regression.run_regression import RawCollector
collector = RawCollector('tests/regression/test_quick.csv')
collector.run_collection()
"
```

## 📊 Understanding Results

### **CSV Columns**
- **question**: Your test query
- **expected_router**: What you expected (GAME_RELATED/OFF_TOPIC)
- **router**: What actually happened
- **hint**: Raw hint text (when game-related)
- **verify**: VERIFIED/INSUFFICIENT_CONTEXT/HALLUCINATED/TOO_SPECIFIC
- **final**: Complete final response
- **timestamp**: For correlating with LangSmith traces

### **Key Patterns**
- ✅ **VERIFIED + "🎯 Hint"** = Working correctly
- ⚠️ **INSUFFICIENT_CONTEXT** = Asking for clarification (often good UX)
- ❌ **HALLUCINATED** = Potential verification calibration issue
- ✅ **OFF_TOPIC + canned response** = Router working correctly

## 📋 Test Files

### **Current Test Infrastructure**
```
tests/
├── regression/                    # ⭐ PRIMARY - Simple raw data collection
│   ├── run_regression.py         # Main regression runner
│   ├── test_questions.csv        # 15 test questions
│   ├── test_quick.csv            # 3 quick questions
│   └── results/                  # Auto-generated results
├── run_all_tests.py              # 🚨 DEPRECATED - Complex interpretation logic
└── test_functions.py             # Unit tests
```

### **Adding New Test Questions**
Edit `tests/regression/test_questions.csv`:
```csv
question,expected_router,notes
"Your new question here",GAME_RELATED,"Description of what you're testing"
```

## 🔍 Debugging Workflow

### **For Verification Issues (like "Who is Zelda?")**
1. **Run focused test**: Add question to `test_quick.csv`
2. **Run multiple times**: Look for inconsistent verify results
3. **Check LangSmith**: Use timestamp to correlate with traces
4. **Fix verification**: Modify `src/verify_correctness_node.py`
5. **Validate fix**: Re-run regression test

### **For Router Issues**
1. **Check router column**: Should match expected_router
2. **Look at final response**: OFF_TOPIC should have canned responses
3. **Test edge cases**: Add borderline questions to test set

## ⚠️ Important Notes

- **No interpretation**: This test suite just collects raw data - YOU decide what's good/bad
- **Run from project root**: Always `python tests/regression/run_regression.py`
- **LangSmith correlation**: Use timestamps to find traces for deep debugging
- **Consistency testing**: Run same question multiple times to check for LLM non-determinism

## 🚀 Advanced Usage

### **Programmatic Testing**
```python
from tests.regression.run_regression import RawCollector

# Custom CSV file
collector = RawCollector('my_custom_tests.csv')
collector.run_collection()

# Results are in collector.results list
```

### **Verification Calibration Testing**
```bash
# Create a file with just "Who is Zelda?" repeated 10 times
# Run to check consistency - should get >95% same verification result
```

---
*Created: 2025-08-20 | Thread: Test infrastructure overhaul*
