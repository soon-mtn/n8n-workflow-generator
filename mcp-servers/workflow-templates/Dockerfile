FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Initialize workflow database if not exists
RUN python api_server.py --init-db

# Expose API port
EXPOSE 8000

# Run API server
CMD ["python", "api_server.py", "--host", "0.0.0.0", "--port", "8000"]