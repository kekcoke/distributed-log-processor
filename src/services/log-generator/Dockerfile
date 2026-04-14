FROM python:3.9-slim

WORKDIR /app

# Copy just the requirements.txt first to leverage Docker cache
COPY src/services/log-generator/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create logs directory for collector
RUN mkdir -p /app/logs

# Copy application code
COPY src/services/log-generator/ /app/

# Run the application using the entrypoint script
CMD ["python", "-u", "entrypoint.py"]
