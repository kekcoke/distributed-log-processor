import random
import time
import sys
import os
from datetime import datetime

# Add parent directory to path for shared config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'logger'))
from config import logger

# Log event types for simulation
LOG_EVENTS = [
    ("INFO", "User login successful"),
    ("INFO", "User logout completed"),
    ("DEBUG", "Processing request from client"),
    ("DEBUG", "Cache hit for resource"),
    ("WARNING", "High memory usage detected: {}%"),
    ("WARNING", "Slow query detected: {}ms"),
    ("ERROR", "Connection timeout to database"),
    ("ERROR", "Failed to process message"),
    ("INFO", "Batch job started: {} records"),
    ("DEBUG", "API response received in {}ms"),
]

SERVICES = ["auth-service", "api-gateway", "worker", "scheduler", "cache"]
ENDPOINTS = ["/api/users", "/api/data", "/health", "/api/jobs", "/metrics"]


def generate_random_log():
    """Generate a random log event."""
    level, message = random.choice(LOG_EVENTS)

    # Fill in template placeholders
    if "{}" in message:
        if "%" in message:
            value = random.randint(70, 95)
            message = message.format(value)
        elif "ms" in message:
            value = random.randint(50, 500)
            message = message.format(value)
        else:
            value = random.randint(10, 1000)
            message = message.format(value)

    # Add context
    service = random.choice(SERVICES)
    endpoint = random.choice(ENDPOINTS)

    log_message = f"[{service}] {message} | endpoint={endpoint}"
    return level, log_message


def main():
    """Generate random log events."""
    print("Starting log generator service...")
    logger.info("Log generator service starting...")

    # Adjust log rate via environment variable
    interval = float(os.environ.get("LOG_INTERVAL", 2))

    logger.info(f"Log generation interval: {interval} seconds")
    logger.info("Generating random log events...")

    while True:
        level, message = generate_random_log()

        if level == "DEBUG":
            logger.debug(message)
        elif level == "INFO":
            logger.info(message)
        elif level == "WARNING":
            logger.warning(message)
        elif level == "ERROR":
            logger.error(message)

        time.sleep(interval)


if __name__ == "__main__":
    main()
