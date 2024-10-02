import logging
import os
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import environ
from PIL import Image, ImageFile

# Add the project root directory to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chesley_web.settings.development")

import django

django.setup()

from django.conf import settings

# Initialize environ
env = environ.Env()

# Read .env.dev file
environ.Env.read_env(os.path.join(project_root, ".env.dev"))

# Allow truncated images to be processed
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Read directory paths from environment variables
INPUT_DIR = Path(env("INPUT_DIR"))
OUTPUT_DIR = Path(env("OUTPUT_DIR"))
ORIGINAL_DIR = Path(env("ORIGINAL_DIR"))
LOG_DIR = Path(env("LOG_DIR"))

# Set up logging
LOG_DIR.mkdir(parents=True, exist_ok=True)

log_filename = f'image_optimization_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    filename=str(LOG_DIR / log_filename),
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Add a stream handler to print logs to console as well
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logging.getLogger("").addHandler(console_handler)

print(f"Log file will be written to: {LOG_DIR / log_filename}")

MAX_FILE_SIZE = 500 * 1024  # 500 KB
MAX_OPTIMIZATION_ATTEMPTS = 5


def is_image_file(file_path):
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except (IOError, SyntaxError) as e:
        logging.warning(f"File {file_path} is not a valid image: {str(e)}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error when checking {file_path}: {str(e)}")
        return False


def optimize_image(
    input_path,
    output_dir,
    original_dir,
    max_size=(1200, 1200),
    initial_jpeg_quality=85,
    initial_webp_quality=80,
    max_file_size=500 * 1024,  # 500 KB
):
    logging.info(f"Processing file: {input_path}")
    try:
        with Image.open(input_path) as img:
            logging.debug(
                f"Opened image: {input_path}, Mode: {img.mode}, Size: {img.size}"
            )

            # Convert to RGB if image is in RGBA mode
            if img.mode == "RGBA":
                img = img.convert("RGB")
                logging.debug(f"Converted {input_path} from RGBA to RGB")

            # Resize image if it's larger than max_size
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size)
                logging.debug(f"Resized {input_path} to {img.size}")

            # Save as JPEG
            jpeg_path = output_dir / f"{input_path.stem}.jpg"
            jpeg_quality = initial_jpeg_quality
            while True:
                img.save(jpeg_path, "JPEG", quality=jpeg_quality, optimize=True)
                if jpeg_path.stat().st_size <= max_file_size or jpeg_quality <= 20:
                    break
                jpeg_quality -= 5
            logging.debug(f"Saved JPEG: {jpeg_path} with quality {jpeg_quality}")

            # Save as WebP
            webp_path = output_dir / f"{input_path.stem}.webp"
            webp_quality = initial_webp_quality
            while True:
                img.save(webp_path, "WEBP", quality=webp_quality)
                if webp_path.stat().st_size <= max_file_size or webp_quality <= 20:
                    break
                webp_quality -= 5
            logging.debug(f"Saved WebP: {webp_path} with quality {webp_quality}")

            # Move original file
            original_path = original_dir / input_path.name
            shutil.move(str(input_path), str(original_path))
            logging.info(f"Moved original file to: {original_path}")

        logging.info(f"Successfully optimized: {input_path}")
        return True
    except Exception as e:
        logging.error(f"Error optimizing {input_path}: {str(e)}")
        return False


def process_images(input_dir, output_dir, original_dir):
    input_dir, output_dir, original_dir = (
        Path(input_dir),
        Path(output_dir),
        Path(original_dir),
    )

    logging.debug(f"Absolute input directory path: {input_dir.resolve()}")
    logging.debug(f"Absolute output directory path: {output_dir.resolve()}")
    logging.debug(f"Absolute original directory path: {original_dir.resolve()}")

    all_files = list(input_dir.iterdir())
    logging.debug(f"All files in input directory: {all_files}")

    image_files = [f for f in all_files if is_image_file(f)]
    logging.info(f"Found {len(image_files)} image files to process")
    logging.info(f"Image files found: {[f.name for f in image_files]}")

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
                logging.error(f"{file} generated an exception: {exc}")
                failed_count += 1
                failed_files.append(file.name)

    logging.info(f"Failed files: {failed_files}")
    return successful_count, failed_count, failed_files


if __name__ == "__main__":
    print(f"Input directory: {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Original directory: {ORIGINAL_DIR}")
    print(f"Log directory: {LOG_DIR}")

    logging.info(f"Input directory: {INPUT_DIR}")
    logging.info(f"Output directory: {OUTPUT_DIR}")
    logging.info(f"Original directory: {ORIGINAL_DIR}")

    # Ensure all directories exist
    for dir_path in [INPUT_DIR, OUTPUT_DIR, ORIGINAL_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)
        logging.debug(f"Ensured directory exists: {dir_path}")

    # Ensure log directory exists and is writable
    os.makedirs(LOG_DIR, exist_ok=True)
    if not os.access(LOG_DIR, os.W_OK):
        print(f"Warning: No write access to log directory: {LOG_DIR}")
        logging.warning(f"No write access to log directory: {LOG_DIR}")

    logging.info("Starting image optimization process")
    successful, failed, failed_files = process_images(
        INPUT_DIR, OUTPUT_DIR, ORIGINAL_DIR
    )
    logging.info("Image optimization process completed")

    # Check contents of directories
    for dir_path in [INPUT_DIR, OUTPUT_DIR, ORIGINAL_DIR]:
        contents = list(dir_path.iterdir())
        logging.debug(f"Contents of {dir_path}: {[f.name for f in contents]}")

    logging.info(f"Log file: {LOG_DIR / log_filename}")
    summary = f"Summary: Successfully processed {successful} files, Failed to process {failed} files"
    logging.info(summary)
    logging.info(f"Failed files: {failed_files}")
    print(summary)
    print(f"Failed files: {failed_files}")
    logging.info("Script execution completed.")

    # Verify logging
    log_file_path = LOG_DIR / log_filename
    print(f"Log file should be at: {log_file_path}")
    if log_file_path.exists():
        print("Log file was successfully created.")
        with open(log_file_path, "r") as log_file:
            print("Last 5 lines of the log file:")
            print("\n".join(log_file.readlines()[-5:]))
    else:
        print("Log file was not created. Check permissions and paths.")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Log directory exists: {os.path.exists(LOG_DIR)}")
        print(f"Log directory is writable: {os.access(LOG_DIR, os.W_OK)}")
