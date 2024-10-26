import argparse
import base64
import hashlib
import logging
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import boto3
import environ
from botocore.exceptions import ClientError
from cryptography.fernet import Fernet


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Website and environment file backup script"
    )
    parser.add_argument("--test-mode", action="store_true", help="Run in test mode")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done"
    )
    parser.add_argument("--db-only", action="store_true", help="Backup only database")
    parser.add_argument("--files-only", action="store_true", help="Backup only files")
    parser.add_argument(
        "--env-only", action="store_true", help="Backup only environment file"
    )
    parser.add_argument(
        "--verify-only", action="store_true", help="Only verify backup configuration"
    )
    return parser.parse_args()


def setup_logging(args):
    """Configure logging based on mode"""
    log_level = logging.DEBUG if args.dry_run else logging.INFO
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = Path("/var/log/chesley_web/backup")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"backup_{timestamp}.log"

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
    )
    return logging.getLogger(__name__)


def get_backup_config(args):
    """Get backup configuration based on mode"""
    if args.test_mode:
        return {
            "backup_dir": Path("/tmp/backup_test"),
            "s3_prefix": "test",
            "db_name": "website_test",
        }
    else:
        return {
            "backup_dir": Path("/tmp/website_backup"),
            "s3_prefix": "prod",
            "db_name": env("PROD_DB_NAME"),
        }


def create_encryption_key(password, salt=None):
    """Create a Fernet key from a password"""
    if salt is None:
        salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    key = base64.urlsafe_b64encode(key[:32])
    return key, salt


def encrypt_file(file_path, key):
    """Encrypt a file using Fernet"""
    f = Fernet(key)
    with open(file_path, "rb") as file:
        file_data = file.read()
    encrypted_data = f.encrypt(file_data)
    with open(f"{file_path}.encrypted", "wb") as file:
        file.write(encrypted_data)


def backup_env_file(args, config, logger):
    """Backup environment file securely"""
    if args.dry_run:
        logger.info("Would backup environment file")
        return True

    try:
        env_file = Path("/opt/website/.env.prod")
        if not env_file.exists():
            logger.error(f"Environment file not found: {env_file}")
            return False

        # Create encryption key from backup key
        backup_key = env("BACKUP_KEY")
        key, salt = create_encryption_key(backup_key)

        # Encrypt env file
        encrypt_file(env_file, key)
        encrypted_file = Path(f"{env_file}.encrypted")

        # Upload to S3
        s3_client = boto3.client("s3")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        s3_key = f"{config['s3_prefix']}/env/{timestamp}/.env.prod.encrypted"

        s3_client.upload_file(
            str(encrypted_file),
            env("PROD_BACKUP_S3_BUCKET"),
            s3_key,
            ExtraArgs={"ServerSideEncryption": "AES256"},
        )

        # Upload salt
        s3_client.put_object(
            Bucket=env("PROD_BACKUP_S3_BUCKET"),
            Key=f"{config['s3_prefix']}/env/{timestamp}/salt",
            Body=salt,
            ServerSideEncryption="AES256",
        )

        # Cleanup
        encrypted_file.unlink()
        logger.info("Environment file backup completed successfully")
        return True

    except Exception as e:
        logger.error(f"Environment file backup failed: {str(e)}")
        return False


def create_exclude_file():
    """Create temporary file with exclusion patterns"""
    exclude_patterns = [
        "*.pyc",
        "__pycache__",
        "*.pyo",
        "*.pyd",
        ".Python",
        "*.log",
        "*.pid",
        ".env*",
        "*.env",
        "local_settings.py",
        "*.sqlite3",
        ".coverage",
        "htmlcov/",
        ".pytest_cache/",
        ".tox/",
        ".git/",
        ".gitignore",
        ".gitattributes",
        "docker-compose*.yml",
        "Dockerfile*",
        ".docker/",
        "media/cache/",
        "static/admin/",
        "static/debug_toolbar/",
        ".idea/",
        ".vscode/",
        "*.swp",
        "*.swo",
        "*.bak",
        "*.tmp",
        "*~",
        "node_modules/",
        "package-lock.json",
        "yarn.lock",
    ]

    exclude_file = "/tmp/backup_exclude.txt"
    with open(exclude_file, "w") as f:
        f.write("\n".join(exclude_patterns))
    return exclude_file


def backup_website(args, config, logger):
    """Backup website files and database"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create backup directory
        config["backup_dir"].mkdir(parents=True, exist_ok=True)

        if not args.db_only and not args.env_only:
            logger.info("Starting website files backup")
            website_backup = config["backup_dir"] / f"website_files_{timestamp}.tar.gz"

            exclude_file = create_exclude_file()
            if args.dry_run:
                logger.info(f"Would create website backup: {website_backup}")
            else:
                subprocess.run(
                    f"tar --exclude-from={exclude_file} -czf {website_backup} /opt/website",
                    shell=True,
                    check=True,
                )
            os.unlink(exclude_file)

        if not args.files_only and not args.env_only:
            logger.info("Starting database backup")
            db_backup = config["backup_dir"] / f"db_backup_{timestamp}.sql.gz"
            if args.dry_run:
                logger.info(f"Would create database backup: {db_backup}")
            else:
                db_command = (
                    f"PGPASSWORD='{env('PROD_DB_PASSWORD')}' pg_dump -h {env('PROD_DB_HOST')} "
                    f"-U {env('PROD_DB_USER')} {config['db_name']} --clean --no-owner --no-acl "
                    f"| gzip > {db_backup}"
                )
                subprocess.run(db_command, shell=True, check=True)

        if not args.dry_run:
            logger.info("Uploading backups to S3")
            s3_client = boto3.client("s3")
            s3_bucket = env("PROD_BACKUP_S3_BUCKET")

            # Upload backups
            for file in config["backup_dir"].glob("*"):
                s3_key = f"{config['s3_prefix']}/website/{timestamp}/{file.name}"
                s3_client.upload_file(
                    str(file),
                    s3_bucket,
                    s3_key,
                    ExtraArgs={
                        "StorageClass": "STANDARD_IA",
                        "ServerSideEncryption": "AES256",
                    },
                )

            # Cleanup
            shutil.rmtree(config["backup_dir"])

        logger.info("Website backup completed successfully")
        return True

    except Exception as e:
        logger.error(f"Website backup failed: {str(e)}")
        if not args.dry_run and config["backup_dir"].exists():
            shutil.rmtree(config["backup_dir"])
        return False


def verify_backup_config(args, config, logger):
    """Verify backup configuration"""
    try:
        # Check S3 bucket access
        s3_client = boto3.client("s3")
        s3_client.head_bucket(Bucket=env("PROD_BACKUP_S3_BUCKET"))

        # Check database connection
        db_command = (
            f"PGPASSWORD='{env('PROD_DB_PASSWORD')}' psql -h {env('PROD_DB_HOST')} "
            f"-U {env('PROD_DB_USER')} -d {config['db_name']} -c 'SELECT 1'"
        )
        subprocess.run(db_command, shell=True, check=True)

        # Check backup directory permissions
        config["backup_dir"].mkdir(parents=True, exist_ok=True)
        test_file = config["backup_dir"] / "test.txt"
        test_file.touch()
        test_file.unlink()

        logger.info("Backup configuration verified successfully")
        return True
    except Exception as e:
        logger.error(f"Backup configuration verification failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Parse arguments
    args = parse_arguments()

    # Setup logging
    logger = setup_logging(args)

    # Initialize environment
    env = environ.Env()
    env.read_env("/opt/website/.env.prod")

    # Get configuration
    config = get_backup_config(args)

    logger.info(
        f"Starting backup process in {'test' if args.test_mode else 'production'} mode"
    )

    # Verify configuration if requested
    if args.verify_only:
        success = verify_backup_config(args, config, logger)
        sys.exit(0 if success else 1)

    # Perform backups
    success = True
    if not args.db_only and not args.files_only:
        success = success and backup_env_file(args, config, logger)
    if not args.env_only:
        success = success and backup_website(args, config, logger)

    sys.exit(0 if success else 1)
