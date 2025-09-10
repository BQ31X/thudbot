# apps/backend/tests/conftest.py

# This file is automatically discovered and run by pytest.
# It is used to define global test setup code or fixtures.
# In this case, we use it to load environment variables from .env.

from thudbot_core.config import load_env  # Import robust .env loader

# Automatically load .env before any tests are executed.
# This allows test files to use environment variables without repeating boilerplate.
load_env(verbose=True)
