# Use a Python base image. It's a good practice to specify a version.
# Use a slim-bullseye image for a smaller footprint.
FROM python:3.11-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install uv, the fast package installer
RUN pip install uv

# Install dependencies from the requirements.txt file using uv
RUN uv sync

# Copy the rest of the application code into the container
COPY . .

# Set the environment variable for Python to not buffer output
# and to not write pyc files to disk, which is good for production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose the port that the Streamlit application will run on
# Streamlit's default port is 8501
EXPOSE 8501

# The command to run your application.
# This starts the Streamlit server and runs your main app.
# The `CMD` is the default command, which can be overridden at runtime.
CMD ["streamlit", "run", "src/app.py"]
