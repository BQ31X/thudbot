# apps/backend/tests/conftest.py

# This file is automatically discovered and run by pytest.
# It is used to define global test setup code or fixtures.
# In this case, we use it to load environment variables from .env.
import os

# from thudbot_core.config import load_env  # Import robust .env loader
if os.getenv("CI") != "true":
    from thudbot_core.config import load_env
    load_env(verbose=True)
else:
    print("🧪 CI detected — skipping load_env() in conftest.py")

# Automatically load .env before any tests are executed.
# This allows test files to use environment variables without repeating boilerplate.
