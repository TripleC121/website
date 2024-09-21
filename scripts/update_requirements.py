import json
import os
import subprocess
from datetime import datetime

# Adjust paths for running from scripts directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Ensure logs directory exists
os.makedirs(LOGS_DIR, exist_ok=True)


def get_outdated_packages():
    result = subprocess.run(
        ["pip", "list", "--outdated", "--format=json"], capture_output=True, text=True
    )
    return json.loads(result.stdout)


def update_requirements(filename):
    filepath = os.path.join(BASE_DIR, filename)
    with open(filepath, "r") as f:
        old_requirements = f.readlines()

    outdated = get_outdated_packages()
    outdated_dict = {pkg["name"]: pkg["latest_version"] for pkg in outdated}

    updated_requirements = []
    changes = []
    for req in old_requirements:
        package = req.split("==")[0].strip()
        old_version = req.split("==")[1].strip() if "==" in req else "Not specified"
        if package in outdated_dict:
            new_version = outdated_dict[package]
            updated_requirements.append(f"{package}=={new_version}\n")
            changes.append(f"{package}: {old_version} -> {new_version}")
        else:
            updated_requirements.append(req)

    # Write updated requirements
    with open(filepath, "w") as f:
        f.writelines(updated_requirements)

    # Create backup of old requirements in logs directory
    backup_filename = os.path.join(
        LOGS_DIR,
        f"{os.path.basename(filename)}.{datetime.now().strftime('%Y%m%d%H%M%S')}.bak",
    )
    with open(backup_filename, "w") as f:
        f.writelines(old_requirements)

    print(f"Updated {filename}")
    return changes


def log_changes(changes, filename):
    log_filepath = os.path.join(LOGS_DIR, f"{filename}.log")
    log_entry = f"\n--- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n"
    log_entry += "\n".join(changes)
    log_entry += "\n"

    with open(log_filepath, "a") as f:
        f.write(log_entry)


# Update both requirements files
dev_changes = update_requirements("requirements-dev.txt")
prod_changes = update_requirements("requirements-prod.txt")

# Log changes
log_changes(dev_changes, "requirements-dev")
log_changes(prod_changes, "requirements-prod")

print(
    "Requirements files updated successfully. Check logs directory for change details."
)
