import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import django
import environ
from PIL import Image, ImageFile

# Allow truncated images to be processed
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Set up Django environment
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chesley_web.settings.development")
django.setup()

from django.conf import settings

# Initialize environ
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env.dev")

# Set up logging
LOG_DIR = Path(settings.BASE_DIR) / "logs"
LOG_DIR.mkdir(exist_ok=True)

log_filename = f'image_optimization_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    filename=str(LOG_DIR / log_filename),
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Add a stream handler to print logs to console as well
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logging.getLogger("").addHandler(console_handler)

MAX_FILE_SIZE = 500 * 1024  # 500 KB
MAX_OPTIMIZATION_ATTEMPTS = 5


def resize_image(img, max_size):
    if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
        img.thumbnail(max_size)
        logging.debug(f"Resized image to {img.size}")
    return img


def save_image(img, path, format, quality):
    img.save(path, format, quality=quality, optimize=True)
    logging.debug(f"Saved {format}: {path}")
    return path.stat().st_size


def optimize_format(img, path, format, initial_quality, max_size):
    quality = initial_quality
    file_size = save_image(img, path, format, quality)
    attempts = 0

    while (file_size > MAX_FILE_SIZE and
           quality > 10 and
           attempts < MAX_OPTIMIZATION_ATTEMPTS):
        quality -= 5
        file_size = save_image(img, path, format, quality)
        attempts += 1

    logging.info(
        f"{format} optimized. "
        f"New size: {file_size / 1024:.2f} KB, "
        f"Final quality: {quality}, "
        f"Attempts: {attempts}"
    )
    return file_size


def optimize_image(
    input_path, output_dir, max_size=(1200, 1200), jpeg_quality=85, webp_quality=80
):
    try:
        with Image.open(input_path) as img:
            logging.debug(
                f"Opened image: {input_path}, Mode: {img.mode}, Size: {img.size}"
            )

            if img.mode == "RGBA":
                img = img.convert("RGB")
                logging.debug(f"Converted {input_path} from RGBA to RGB")

            img = resize_image(img, max_size)

            jpeg_path = output_dir / f"{input_path.stem}.jpg"
            webp_path = output_dir / f"{input_path.stem}.webp"

            jpeg_size = save_image(img, jpeg_path, "JPEG", jpeg_quality)
            webp_size = save_image(img, webp_path, "WEBP", webp_quality)

            if jpeg_size > MAX_FILE_SIZE or webp_size > MAX_FILE_SIZE:
                logging.warning(f"Large file detected: {input_path.name}")
                logging.info(
                    f"JPEG size: {jpeg_size / 1024:.2f} KB, "
                    f"WebP size: {webp_size / 1024:.2f} KB"
                )

                if jpeg_size > MAX_FILE_SIZE:
                    jpeg_size = optimize_format(
                        img, jpeg_path, "JPEG", jpeg_quality, max_size
                    )

                if webp_size > MAX_FILE_SIZE:
                    webp_size = optimize_format(
                        img, webp_path, "WEBP", webp_quality, max_size
                    )

        logging.info(f"Successfully optimized: {input_path}")
        return True
    except Exception as e:
        logging.error(f"Error optimizing {input_path}: {str(e)}")
        return False


def main():
    static_dir = Path(settings.STATIC_ROOT) / "images"
    output_dir = static_dir / "optimized"
    output_dir.mkdir(exist_ok=True)

    image_files = list(static_dir.glob("*.{jpg,jpeg,png,gif}"))

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(optimize_image, img_path, output_dir)
            for img_path in image_files
        ]

        for future in as_completed(futures):
            future.result()

    logging.info("Image optimization completed.")


if __name__ == "__main__":
    main()
