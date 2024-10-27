#!/usr/bin/env python3
"""
Website Backup Script
Handles both development and production environments with S3 and local storage options.
"""
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
from django.core.mail import send_mail


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Website backup script")
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
    parser.add_argument(
        "--local-only", action="store_true", help="Store backups locally only"
    )
    return parser.parse_args()


def setup_logging(args):
    """Configure logging based on environment."""
    log_level = logging.DEBUG if args.dry_run else logging.INFO
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Determine environment
    django_settings = os.getenv("DJANGO_SETTINGS_MODULE", "")
    is_development = "development" in django_settings or args.test_mode

    # Set paths based on environment
    if is_development:
        log_dir = Path.home() / "logs" / "website_backup"
    else:
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
    """Get backup configuration based on environment."""
    django_settings = os.getenv("DJANGO_SETTINGS_MODULE", "")
    is_development = "development" in django_settings or args.test_mode

    if is_development:
        return {
            "backup_dir": Path("/tmp/backup_test"),
            "local_backup_dir": Path.home() / "backups/website",
            "s3_prefix": "test",
            "db_name": "db.sqlite3",
            "use_s3": False,
        }
    else:
        return {
            "backup_dir": Path("/tmp/website_backup"),
            "local_backup_dir": Path("/opt/website/backups"),
            "s3_prefix": "prod",
            "db_name": env("PROD_DB_NAME"),
            "use_s3": not args.local_only,
        }


def send_notification(subject, message, logger):
    """Send email notification if configured."""
    try:
        if env("BACKUP_NOTIFICATION_EMAIL", default=None):
            from_email = env("DEFAULT_FROM_EMAIL")
            to_email = env("BACKUP_NOTIFICATION_EMAIL")

            send_mail(
                subject,
                message,
                from_email,
                [to_email],
                fail_silently=False,
            )
            logger.info(f"Notification sent: {subject}")
    except Exception as e:
        logger.error(f"Failed to send notification: {str(e)}")


def create_exclude_file():
    """Create temporary file with exclusion patterns."""
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
        ".git/",
        ".gitignore",
        "docker-compose*.yml",
        "Dockerfile*",
        ".docker/",
        "media/cache/",
        "static/admin/",
        "node_modules/",
    ]

    exclude_file = "/tmp/backup_exclude.txt"
    with open(exclude_file, "w") as f:
        f.write("\n".join(exclude_patterns))
    return exclude_file


def check_s3_storage_usage(s3_client, bucket_name, logger):
    """Monitor S3 storage usage for free tier limits."""
    try:
        objects = s3_client.list_objects_v2(Bucket=bucket_name)
        total_size = sum(obj["Size"] for obj in objects.get("Contents", []))
        total_size_gb = total_size / (1024**3)

        max_size = float(env("BACKUP_MAX_SIZE_GB", default="4.5"))
        if total_size_gb > max_size:
            message = (
                f"S3 storage usage ({total_size_gb: .2f}GB)"
                f"approaching limit ({max_size}GB)"
            )
            logger.warning(message)
            send_notification("Backup Storage Warning", message, logger)

        return total_size_gb
    except Exception as e:
        logger.error(f"Failed to check S3 storage usage: {str(e)}")
        return None


def cleanup_old_backups(s3_client, bucket_name, prefix, retention_days, logger):
    """Clean up old backups based on retention policy."""
    try:
        paginator = s3_client.get_paginator("list_objects_v2")
        current_size = 0

        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            for obj in page.get("Contents", []):
                age = (
                    datetime.now(obj["LastModified"].tzinfo) - obj["LastModified"]
                ).days
                if age > retention_days:
                    s3_client.delete_object(Bucket=bucket_name, Key=obj["Key"])
                    logger.info(f"Deleted old backup: {obj['Key']}")
                else:
                    current_size += obj["Size"]

        logger.info(f"Current backup size: {current_size / (1024**3): .2f}GB")
        return current_size
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        return None


def backup_files(backup_dir, timestamp, args, logger):
    """Handle website files backup."""
    try:
        if args.db_only or args.env_only:
            return True

        logger.info("Starting website files backup")
        website_backup = backup_dir / f"website_files_{timestamp}.tar.gz"

        exclude_file = create_exclude_file()
        if args.dry_run:
            logger.info(f"Would create website backup: {website_backup}")
        else:
            backup_path = "/opt/website" if not args.test_mode else os.getcwd()
            subprocess.run(
                f"tar --exclude-from={exclude_file} -czf {website_backup} "
                f"{backup_path}",
                shell=True,
                check=True,
            )
        os.unlink(exclude_file)
        return True
    except Exception as e:
        logger.error(f"File backup failed: {str(e)}")
        return False


def backup_database(backup_dir, timestamp, config, args, logger):
    """Handle database backup."""
    try:
        if args.files_only or args.env_only:
            return True

        logger.info("Starting database backup")
        db_backup = backup_dir / f"db_backup_{timestamp}.sql.gz"

        if args.dry_run:
            logger.info(f"Would create database backup: {db_backup}")
            return True

        if args.test_mode:
            # For SQLite, just copy the database file
            src_db = Path(config["db_name"])
            if src_db.exists():
                shutil.copy2(src_db, db_backup)
            else:
                logger.warning(f"Test database not found: {src_db}")
                return False
        else:
            # For PostgreSQL
            db_command = (
                f"PGPASSWORD='{env('PROD_DB_PASSWORD')}' "
                f"pg_dump -h {env('PROD_DB_HOST')} "
                f"-U {env('PROD_DB_USER')} {config['db_name']} "
                f"--clean --no-owner --no-acl | gzip > {db_backup}"
            )
            subprocess.run(db_command, shell=True, check=True)
        return True
    except Exception as e:
        logger.error(f"Database backup failed: {str(e)}")
        return False


def store_backup_local(backup_dir, config, timestamp, logger):
    """Store backup files locally."""
    try:
        local_backup_dir = config["local_backup_dir"]
        local_backup_dir.mkdir(parents=True, exist_ok=True)

        backup_path = local_backup_dir / timestamp
        backup_path.mkdir(parents=True)

        # Copy backup files to local storage
        for file in backup_dir.glob("*"):
            shutil.copy2(file, backup_path)

        logger.info(f"Backup stored locally at: {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Local backup storage failed: {str(e)}")
        return False


def upload_backups(backup_dir, timestamp, s3_config, current_usage, logger):
    """Upload backups to S3."""
    try:
        logger.info("Uploading backups to S3")
        s3_bucket = env("PROD_BACKUP_S3_BUCKET")

        for file in backup_dir.glob("*"):
            s3_key = f"{s3_config['s3_prefix']}/website/{timestamp}/{file.name}"
            s3_config["client"].upload_file(
                str(file),
                s3_bucket,
                s3_key,
                ExtraArgs={
                    "StorageClass": "STANDARD_IA",
                    "ServerSideEncryption": "AES256",
                },
            )

        send_notification(
            "Backup Completed Successfully",
            f"Backup completed at {timestamp}. "
            f"Storage usage: {current_usage: .2f}GB",
            logger,
        )
        return True
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        return False


def verify_backup_config(args, config, logger):
    """Verify backup configuration."""
    try:
        if config["use_s3"]:
            # Check S3 bucket access
            s3_client = boto3.client("s3")
            s3_client.head_bucket(Bucket=env("PROD_BACKUP_S3_BUCKET"))
            logger.info("S3 bucket access verified")

        if not args.test_mode:
            # Check database connection
            db_command = (
                f"PGPASSWORD='{env('PROD_DB_PASSWORD')}' "
                f"psql -h {env('PROD_DB_HOST')} "
                f"-U {env('PROD_DB_USER')} "
                f"-d {config['db_name']} -c 'SELECT 1'"
            )
            subprocess.run(db_command, shell=True, check=True)
            logger.info("Database connection verified")

        # Check backup directory permissions
        config["backup_dir"].mkdir(parents=True, exist_ok=True)
        test_file = config["backup_dir"] / "test.txt"
        test_file.touch()
        test_file.unlink()
        logger.info("Backup directory permissions verified")

        if not config["use_s3"]:
            local_backup_dir = config.get("local_backup_dir")
            if local_backup_dir:
                local_backup_dir.mkdir(parents=True, exist_ok=True)
                test_file = local_backup_dir / "test.txt"
                test_file.touch()
                test_file.unlink()
                logger.info("Local backup directory permissions verified")

        return True
    except Exception as e:
        logger.error(f"Backup configuration verification failed: {str(e)}")
        return False


def backup_website(args, config, logger):
    """Coordinate website backup process."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        config["backup_dir"].mkdir(parents=True, exist_ok=True)

        s3_config = None
        if config["use_s3"]:
            s3_client = boto3.client("s3")
            bucket_name = env("PROD_BACKUP_S3_BUCKET")
            s3_config = {
                "client": s3_client,
                "bucket": bucket_name,
                "s3_prefix": config["s3_prefix"],
            }

            # Monitor storage usage
            current_usage = check_s3_storage_usage(s3_client, bucket_name, logger)
            if current_usage:
                retention_days = int(env("BACKUP_RETENTION_DAYS", default="30"))
                cleanup_old_backups(
                    s3_client, bucket_name, config["s3_prefix"], retention_days, logger
                )

        # Perform backups
        files_success = backup_files(config["backup_dir"], timestamp, args, logger)
        db_success = backup_database(
            config["backup_dir"], timestamp, config, args, logger
        )

        # Handle storage
        storage_success = True
        if not args.dry_run and files_success and db_success:
            if config["use_s3"]:
                storage_success = upload_backups(
                    config["backup_dir"], timestamp, s3_config, current_usage, logger
                )
            else:
                storage_success = store_backup_local(
                    config["backup_dir"], config, timestamp, logger
                )

        # Cleanup
        if not args.dry_run:
            shutil.rmtree(config["backup_dir"])

        return all([files_success, db_success, storage_success])

    except Exception as e:
        error_msg = f"Backup process failed: {str(e)}"
        logger.error(error_msg)
        send_notification("Backup Failed", error_msg, logger)
        if not args.dry_run and config["backup_dir"].exists():
            shutil.rmtree(config["backup_dir"])
        return False


if __name__ == "__main__":
    # Parse arguments
    args = parse_arguments()

    # Setup logging
    logger = setup_logging(args)

    try:
        # Initialize environment
        env = environ.Env()
        if args.test_mode:
            env.read_env(".env.dev")
        else:
            env.read_env("/opt/website/.env.prod")

        # Get configuration
        config = get_backup_config(args)

        logger.info(
            f"Starting backup process in "
            f"{'test' if args.test_mode else 'production'} mode"
        )

        # Verify configuration if requested
        if args.verify_only:
            success = verify_backup_config(args, config, logger)
            sys.exit(0 if success else 1)

        # Perform backup
        success = backup_website(args, config, logger)
        sys.exit(0 if success else 1)

    except Exception as e:
        logger.error(f"Backup script failed: {str(e)}")
        sys.exit(1)
