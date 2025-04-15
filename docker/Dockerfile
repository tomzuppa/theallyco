# 🐍 Base image with Python pre-installed
FROM python:3.12-slim

# 🧱 Set environment variables to prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 📁 Set the working directory inside the container
WORKDIR /app

# 🔁 Copy only requirements first for dependency caching
COPY requirements/base.txt requirements/base.txt
COPY requirements/prod.txt requirements/prod.txt

# ⬇️ Install system dependencies (for psycopg2, Pillow, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && pip install --upgrade pip

# 📦 Install Python dependencies
RUN pip install -r requirements/prod.txt

# 📁 Copy the rest of the project into the container
COPY . .

# 🛠️ Make entrypoint.sh executable
RUN chmod +x docker/entrypoint.sh

# 🔄 Run the entrypoint script by default
ENTRYPOINT ["/app/docker/entrypoint.sh"]
