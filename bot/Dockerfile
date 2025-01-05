# Use Python 3.10 slim image as the base
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Copy the current directory content to the container
COPY . /app

# Install system dependencies for psycopg2 and other libraries (if needed in the future)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Ensure the bot script is executable
RUN chmod +x bot.py

# Run the bot script
CMD ["python", "bot.py"]
