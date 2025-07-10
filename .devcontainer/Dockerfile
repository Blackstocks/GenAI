# Use official Python Dev Container base image
FROM mcr.microsoft.com/devcontainers/python:3.12

# Prevent Python from writing .pyc files
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Optional: install project dependencies using Poetry (if pyproject.toml is present)
# COPY pyproject.toml poetry.lock ./
# RUN poetry install --no-root

# Install Node.js and npm (LTS version)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

