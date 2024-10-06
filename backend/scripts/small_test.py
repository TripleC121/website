import os
from pathlib import Path

LOG_DIR = Path("/home/critter/projects/website/backend/logs")
test_file = LOG_DIR / "test_file.txt"

try:
    with open(test_file, "w") as f:
        f.write("Test content")
    print(f"Successfully created and wrote to {test_file}")
except Exception as e:
    print(f"Failed to create or write to {test_file}: {str(e)}")

print(f"File exists: {os.path.exists(test_file)}")
if os.path.exists(test_file):
    print(f"File size: {os.path.getsize(test_file)} bytes")
    with open(test_file, "r") as f:
        print(f"File content: {f.read()}")
