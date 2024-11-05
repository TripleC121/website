#!/bin/bash
# Enhanced security-monitor.sh with AWS SES integration
# Version 1.5

# Configuration
BASE_LOG_DIR="/var/log/chesley_web"
NGINX_LOG_DIR="${BASE_LOG_DIR}/nginx"
SECURITY_LOG_DIR="${BASE_LOG_DIR}/security"
DEPLOYMENT_LOG_DIR="${BASE_LOG_DIR}/deployment"

# Log files
BLOCKED_LOG="${NGINX_LOG_DIR}/security/blocked.log"
ALERT_LOG="${SECURITY_LOG_DIR}/alerts.log"
REPORT_FILE="${SECURITY_LOG_DIR}/daily_report.txt"
AUDIT_LOG="${NGINX_LOG_DIR}/security/audit.log"

# Email configuration
ALERT_EMAIL="colby86colby@gmail.com"
FROM_EMAIL="colby86colby@gmail.com"
AWS_REGION="us-east-1"

# Thresholds (unchanged)
THRESHOLD_ATTACKS_PER_HOUR=50
THRESHOLD_ATTACKS_PER_IP=20
THRESHOLD_ADMIN_ATTEMPTS=5
THRESHOLD_SENSITIVE_PATHS=10

# Sensitive paths and user agents (unchanged)
SENSITIVE_PATHS=(
    "wp-admin"
    "administrator"
    "admin"
    "xmlrpc.php"
    ".env"
    ".git"
    "staticfiles"
    "media"
)

BLOCKED_USER_AGENTS=(
    "sqlmap"
    "nikto"
    "gobuster"
    "wpscan"
    "masscan"
    "nmap"
    "dirbuster"
)

# Function to ensure required directories exist (unchanged)
setup_directories() {
    local dirs=(
        "$SECURITY_LOG_DIR"
        "$NGINX_LOG_DIR/security"
        "${BASE_LOG_DIR}/test"
    )

    for dir in "${dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            chown webapps:www-data "$dir"
            chmod 750 "$dir"
        fi
    done
}

# Enhanced logging function (unchanged)
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$ALERT_LOG"
}

# New function to send email via AWS SES
send_ses_email() {
    local subject="$1"
    local message="$2"
    local recipient="$3"

    # Prepare the JSON for AWS SES
    local email_json=$(cat <<EOF
{
    "Source": "$FROM_EMAIL",
    "Destination": {
        "ToAddresses": ["$recipient"]
    },
    "Message": {
        "Subject": {
            "Data": "$subject",
            "Charset": "UTF-8"
        },
        "Body": {
            "Text": {
                "Data": "$message",
                "Charset": "UTF-8"
            }
        }
    }
}
EOF
)

    # Send email using AWS SES
    local response
    response=$(aws ses send-email \
        --region "$AWS_REGION" \
        --cli-input-json "$email_json" 2>&1)

    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        log_message "INFO" "Email sent successfully via SES: $subject"
        return 0
    else
        log_message "ERROR" "Failed to send email via SES: $response"
        return 1
    fi
}

# Updated alert function to use SES
send_alert() {
    local subject="$1"
    local message="$2"
    log_message "ALERT" "$subject: $message"
    send_ses_email "Security Alert: $subject" "$message" "$ALERT_EMAIL"
}

# Function to detect Django admin access attempts (unchanged)
check_admin_attempts() {
    if [[ ! -f "$BLOCKED_LOG" ]]; then
        log_message "ERROR" "Blocked log file not found: $BLOCKED_LOG"
        return 1
    fi

    local admin_attempts=$(grep -c "/admin/" "$BLOCKED_LOG")
    if (( admin_attempts > THRESHOLD_ADMIN_ATTEMPTS )); then
        send_alert "High Admin Access Attempts" "Detected $admin_attempts admin access attempts"
    fi
}

# Function to monitor sensitive file access (unchanged)
check_sensitive_paths() {
    if [[ ! -f "$BLOCKED_LOG" ]]; then
        log_message "ERROR" "Blocked log file not found: $BLOCKED_LOG"
        return 1
    fi

    for path in "${SENSITIVE_PATHS[@]}"; do
        local attempts=$(grep -c "$path" "$BLOCKED_LOG")
        if (( attempts > THRESHOLD_SENSITIVE_PATHS )); then
            send_alert "Sensitive Path Access" "High access attempts to $path: $attempts times"
        fi
    done
}

# Updated daily report function to use SES
generate_daily_report() {
    if [[ ! -f "$BLOCKED_LOG" ]]; then
        log_message "ERROR" "Blocked log file not found: $BLOCKED_LOG"
        return 1
    fi

    {
        echo "Security Report - $(date '+%Y-%m-%d')"
        echo "=================================="

        echo -e "\n1. Django Admin Access Attempts:"
        grep "/admin/" "$BLOCKED_LOG" 2>/dev/null | awk '{print $2}' | sort | uniq -c | sort -nr

        echo -e "\n2. Static/Media File Access Attempts:"
        egrep "/(static|media)/" "$BLOCKED_LOG" 2>/dev/null | awk '{print $2}' | sort | uniq -c

        echo -e "\n3. Sensitive File Access Attempts:"
        for path in "${SENSITIVE_PATHS[@]}"; do
            echo "Path: $path"
            grep "$path" "$BLOCKED_LOG" 2>/dev/null | awk '{print $2}' | sort | uniq -c
        done

        echo -e "\n4. Known Bad User Agents:"
        for agent in "${BLOCKED_USER_AGENTS[@]}"; do
            echo "Agent: $agent"
            grep "$agent" "$BLOCKED_LOG" 2>/dev/null | wc -l
        done
    } > "$REPORT_FILE"

    if [[ -f "$REPORT_FILE" ]]; then
        local report_content=$(<"$REPORT_FILE")
        send_ses_email "Daily Security Report - $(date '+%Y-%m-%d')" "$report_content" "$ALERT_EMAIL"
    else
        log_message "ERROR" "Failed to generate report file"
        return 1
    fi
}

# Test Suite with SES integration
run_tests() {
    local TEST_LOG_DIR="${BASE_LOG_DIR}/test"
    local TEST_BLOCKED_LOG="${TEST_LOG_DIR}/blocked.test.log"

    # Setup test environment
    mkdir -p "$TEST_LOG_DIR"
    log_message "INFO" "Created test directory: $TEST_LOG_DIR"

    # Test 1: Test SES email sending
    echo "[Test 1] Testing SES email sending"
    send_ses_email "Test Email" "This is a test email from security-monitor.sh" "$ALERT_EMAIL"

    # Remaining tests (unchanged)
    echo "[Test 2] Testing admin access detection"
    {
        echo "192.168.1.1 - - [01/Nov/2024:10:00:00 +0000] \"GET /admin/ HTTP/1.1\" 403 0"
        echo "192.168.1.1 - - [01/Nov/2024:10:00:01 +0000] \"GET /admin/ HTTP/1.1\" 403 0"
        echo "192.168.1.1 - - [01/Nov/2024:10:00:02 +0000] \"GET /admin/ HTTP/1.1\" 403 0"
    } > "$TEST_BLOCKED_LOG"

    # Continue with existing tests...
    local orig_blocked_log="$BLOCKED_LOG"
    BLOCKED_LOG="$TEST_BLOCKED_LOG"

    check_admin_attempts
    check_sensitive_paths

    BLOCKED_LOG="$orig_blocked_log"

    log_message "INFO" "Tests completed. Check ${ALERT_LOG} for results."
    echo "Tests completed. Check ${ALERT_LOG} for results."
}

# Main function (unchanged)
main() {
    setup_directories

    case "$1" in
        "hourly")
            log_message "INFO" "Starting hourly checks"
            check_admin_attempts
            check_sensitive_paths
            ;;
        "daily")
            log_message "INFO" "Generating daily report"
            generate_daily_report
            ;;
        "test")
            log_message "INFO" "Running test suite"
            run_tests
            ;;
        *)
            echo "Usage: $0 {hourly|daily|test}"
            exit 1
            ;;
    esac
}

main "$@"
