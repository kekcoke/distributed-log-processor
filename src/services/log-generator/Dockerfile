FROM python:3.9-slim

WORKDIR /app

# Copy just the requirements.txt first to leverage Docker cache
COPY src/services/log-generator/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create logs directory
RUN mkdir -p /logs

# Copy application code
COPY src/services/log-generator/ /app/

# Run the application
CMD ["python", "-u", "app.py"]
