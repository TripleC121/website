import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import environ

# Add the project root directory to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

# Initialize environ and read .env.dev file
env = environ.Env()
env_file = os.path.join(project_root, ".env.dev")
print(f"Reading environment variables from: {env_file}")
environ.Env.read_env(env_file)

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chesley_web.settings.development")

# Read directory paths from environment variables
INPUT_DIR = env("INPUT_DIR", default=None)
OUTPUT_DIR = env("OUTPUT_DIR", default=None)
ORIGINAL_DIR = env("ORIGINAL_DIR", default=None)
LOG_DIR = env("LOG_DIR", default=None)

print(f"INPUT_DIR: {INPUT_DIR}")
print(f"OUTPUT_DIR: {OUTPUT_DIR}")
print(f"ORIGINAL_DIR: {ORIGINAL_DIR}")
print(f"LOG_DIR: {LOG_DIR}")

# Attempt to create log directory if it doesn't exist
if LOG_DIR:
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
    print(f"Attempted to create LOG_DIR: {LOG_DIR}")
    print(f"LOG_DIR exists: {os.path.exists(LOG_DIR)}")
    print(f"LOG_DIR is writable: {os.access(LOG_DIR, os.W_OK)}")

# Set up logging
log_filename = f'debug_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
log_file_path = (
    Path(LOG_DIR) / log_filename if LOG_DIR else Path(project_root) / "debug.log"
)

print(f"Attempting to set up logging to: {log_file_path}")

try:
    logging.basicConfig(
        filename=str(log_file_path),
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    print("Logging configuration completed.")
    logging.info("Logging initialized")
except Exception as e:
    print(f"Failed to set up logging: {str(e)}")

print(f"Log file created: {os.path.exists(log_file_path)}")
if os.path.exists(log_file_path):
    print(f"Log file size: {os.path.getsize(log_file_path)} bytes")
    print("Last 5 lines of the log file:")
    with open(log_file_path, "r") as log_file:
        lines = log_file.readlines()
        for line in lines[-5:]:
            print(line.strip())

# Test logging
logging.debug("This is a debug message")
logging.info("This is an info message")
logging.warning("This is a warning message")
logging.error("This is an error message")

print("Script execution completed.")
