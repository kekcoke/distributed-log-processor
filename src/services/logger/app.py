import os
import time
from datetime import datetime
import logHandler
from http.server import HTTPServer
import threading

from config import logger, LOG_DIR, LOG_FILE, LOG_LEVEL_CONSOLE, LOG_LEVEL_FILE

def run_web_server():
    """Run the web interface on port 8080."""
    server = HTTPServer(("0.0.0.0", 8080), logHandler.LogHandler)
    logger.info("Web interface started on http://0.0.0.0:8080")
    server.serve_forever()


def main():
    """Main logger service with web interface."""
    print("Starting distributed logger service...")
    logger.info("Logger service starting...")
    logger.info(f"Log level (console): {LOG_LEVEL_CONSOLE}")
    logger.info(f"Log level (file): {LOG_LEVEL_FILE}")
    logger.info(f"Log file: {LOG_FILE}")

    # Start web server in background thread
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()

    # Main logging loop
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info("Logger service is running. This will be part of our distributed system!")
        time.sleep(5)

if __name__ == "__main__":
    main()