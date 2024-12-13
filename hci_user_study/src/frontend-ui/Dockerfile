# Use the official Python image
FROM python:3.12-slim-bookworm

# Set environment variables
ENV PYENV_SHELL=/bin/bash

# Install dependencies
RUN set -ex; \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends build-essential && \
    pip install --no-cache-dir --upgrade pip && \
    pip install pipenv streamlit && \
    mkdir -p /app

WORKDIR /app

# Copy source files
COPY . /app

# Install dependencies with pipenv
RUN pipenv install

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit app
CMD ["pipenv", "run", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
