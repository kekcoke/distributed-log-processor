#!/usr/bin/env python3
"""Entrypoint for log-generator container."""
import os
from config import config
from log_generator import LogGenerator


def main():
    # Override output file to use shared volume path
    output_file = os.environ.get("OUTPUT_FILE", "/app/logs/app.log")
    config["OUTPUT_FILE"] = output_file

    generator = LogGenerator(config)
    generator.run()


if __name__ == "__main__":
    main()
