import logging
import os
import shutil
import sys

# Suppress specific PIL import warnings
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import environ
from PIL import Image, ImageFile

warnings.filterwarnings("ignore", category=UserWarning, module="PIL")

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

import django

django.setup()

# Allow truncated images to be processed
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Read directory paths from environment variables
INPUT_DIR = Path(env("INPUT_DIR"))
OUTPUT_DIR = Path(env("OUTPUT_DIR"))
ORIGINAL_DIR = Path(env("ORIGINAL_DIR"))
LOG_DIR = Path(env("LOG_DIR"))

print(f"INPUT_DIR: {INPUT_DIR}")
print(f"OUTPUT_DIR: {OUTPUT_DIR}")
print(f"ORIGINAL_DIR: {ORIGINAL_DIR}")
print(f"LOG_DIR: {LOG_DIR}")

# Ensure log directory exists
LOG_DIR.mkdir(parents=True, exist_ok=True)
print(f"Attempted to create LOG_DIR: {LOG_DIR}")
print(f"LOG_DIR exists: {os.path.exists(LOG_DIR)}")
print(f"LOG_DIR is writable: {os.access(LOG_DIR, os.W_OK)}")

# Set up logging using the same configuration as logging_test.py
log_filename = f'image_optimization_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
log_file_path = LOG_DIR / log_filename

try:
    logging.basicConfig(
        filename=str(log_file_path),
        level=logging.DEBUG,  # Adjust log level as needed
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    # Add StreamHandler to also log to console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(console_handler)

    print("Logging configuration completed.")
except Exception as e:
    print(f"Failed to set up logging: {str(e)}")
    sys.exit(1)

# Define logger
logger = logging.getLogger(__name__)

# Guaranteed logging
logger.critical("Script started")

MAX_FILE_SIZE = 500 * 1024  # 500 KB


def is_image_file(file_path):
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except (IOError, SyntaxError):
        logger.info(f"File {file_path} is not a valid image.")
        return False
    except Exception as e:
        logger.error(f"Unexpected error when checking {file_path}: {str(e)}")
        return False


def optimize_image(
    input_path,
    output_dir,
    original_dir,
    max_size=(1200, 1200),
    initial_jpeg_quality=85,
    initial_webp_quality=80,
):
    logger.info(f"Processing file: {input_path}")
    try:
        with Image.open(input_path) as img:
            if img.mode == "RGBA":
                img = img.convert("RGB")

            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size)

            for format, quality in [
                ("JPEG", initial_jpeg_quality),
                ("WEBP", initial_webp_quality),
            ]:
                output_path = output_dir / f"{input_path.stem}.{format.lower()}"
                while True:
                    img.save(output_path, format, quality=quality, optimize=True)
                    if output_path.stat().st_size <= MAX_FILE_SIZE or quality <= 20:
                        break
                    quality -= 5

            original_path = original_dir / input_path.name
            shutil.move(str(input_path), str(original_path))

        logger.info(f"Successfully optimized: {input_path}")
        return True
    except Exception as e:
        logger.error(f"Error optimizing {input_path}: {str(e)}")
        return False


def process_images(input_dir, output_dir, original_dir):
    input_dir, output_dir, original_dir = map(
        Path, [input_dir, output_dir, original_dir]
    )

    all_files = list(input_dir.iterdir())
    image_files = [f for f in all_files if is_image_file(f)]
    logger.info(f"Found {len(image_files)} image files to process")

    successful_count = 0
    failed_count = 0
    failed_files = []

    with ThreadPoolExecutor() as executor:
        future_to_file = {
            executor.submit(optimize_image, f, output_dir, original_dir): f
            for f in image_files
        }
        for future in as_completed(future_to_file):
            file = future_to_file[future]
            try:
                if future.result():
                    successful_count += 1
                else:
                    failed_count += 1
                    failed_files.append(file.name)
            except Exception as exc:
                logger.error(f"{file} generated an exception: {exc}")
                failed_count += 1
                failed_files.append(file.name)

    return successful_count, failed_count, failed_files


def main():
    for dir_path in [INPUT_DIR, OUTPUT_DIR, ORIGINAL_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)

    logger.info("Starting image optimization process")
    logger.info(f"Input directory: {INPUT_DIR}")
    logger.info(f"Output directory: {OUTPUT_DIR}")
    logger.info(f"Original directory: {ORIGINAL_DIR}")
    logger.info(f"Log file: {log_file_path}")

    successful, failed, failed_files = process_images(
        INPUT_DIR, OUTPUT_DIR, ORIGINAL_DIR
    )

    summary = f"Summary: Successfully processed {successful} files, "
    summary += f"Failed to process {failed} files"
    logger.info(summary)
    if failed_files:
        logger.info(f"Failed files: {failed_files}")

    logger.info("Image optimization process completed")

    # Guaranteed logging
    logger.critical("Script ended")

    # Ensure all log messages are written to file before reading
    logging.shutdown()

    # Print the last few lines of the log file
    try:
        print("\nLast few lines of the log file:")
        with open(log_file_path, "r") as log_file:
            lines = log_file.readlines()
            for line in lines[-5:]:
                print(line.strip())
    except FileNotFoundError as e:
        print(f"Error: {e} - Log file might not have been written or flushed properly.")


if __name__ == "__main__":
    main()
