# Use Python 3.10 slim image as the base
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Copy the application files
COPY . /app

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run the Streamlit dashboard
CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.enableXsrfProtection=false"]
