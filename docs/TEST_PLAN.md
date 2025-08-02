# Thudbot Testing Plan
# Test Plan: Thudbot Certification Challenge

## 1. Foundational Testing

This section of the test plan outlines the initial testing framework established on the `main` branch. The purpose of these tests is to ensure that the project's core infrastructure is functional before a new feature branch is created.

### 1.1 Fast Unit Tests

- **Objective:** To quickly verify that core, non-RAG-specific functions and dependencies are working as expected.
    
- **Tooling:** `pytest` is used to discover and run tests.
    
- **Location:** All fast unit tests are located in the `tests/` directory.
    
- **Current State:** A placeholder test in `tests/test_functions.py` has been created to validate that the `pytest` framework is set up correctly. This test will be expanded as new, testable components are added.
    

### 1.2 Automated Checks with `check_and_commit.sh`

- **Objective:** To automate the execution of fast tests and prevent commits to the repository if any tests fail.
    
- **Tooling:** A `bash` script named `check_and_commit.sh` is used as a pre-commit hook.
    
- **Workflow:** This script runs `uv run pytest` to execute all fast tests. If the tests pass, it proceeds with the `git commit`. If they fail, the commit is aborted.
    

## 2. Future Testing

As the project progresses, this test plan will be updated with more comprehensive testing strategies, including:

- **Component-specific unit tests** for the RAG pipeline components (e.g., data loading, vector store setup).
    
- **Integration tests** to verify that the different components of the RAG pipeline (retrieval, generation) work together correctly.
    
- **Ragas Evaluation** to measure and track the performance of the RAG pipeline using metrics like faithfulness and context precision.
    
- **UI Tests** for the Streamlit application interface.