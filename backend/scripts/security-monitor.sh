#!/bin/bash
# Enhanced security-monitor.sh with test suite
# Version 1.4

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

# Thresholds
THRESHOLD_ATTACKS_PER_HOUR=50
THRESHOLD_ATTACKS_PER_IP=20
THRESHOLD_ADMIN_ATTEMPTS=5
THRESHOLD_SENSITIVE_PATHS=10

# Custom patterns for your setup
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

# Function to ensure required directories exist
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

# Enhanced logging function
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$ALERT_LOG"
}

# Function to send email alerts
send_alert() {
    local subject="$1"
    local message="$2"
    log_message "ALERT" "$subject: $message"
    echo "$message" | mail -s "Security Alert: $subject" "$ALERT_EMAIL"
}

# Function to detect Django admin access attempts
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

# Function to monitor sensitive file access
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

# Enhanced daily report with Django-specific sections
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
        mail -s "Daily Security Report - $(date '+%Y-%m-%d')" "$ALERT_EMAIL" < "$REPORT_FILE"
    else
        log_message "ERROR" "Failed to generate report file"
        return 1
    fi
}

# Test Suite
run_tests() {
    local TEST_LOG_DIR="${BASE_LOG_DIR}/test"
    local TEST_BLOCKED_LOG="${TEST_LOG_DIR}/blocked.test.log"

    # Setup test environment
    mkdir -p "$TEST_LOG_DIR"
    log_message "INFO" "Created test directory: $TEST_LOG_DIR"

    # Test 1: Check admin access detection
    echo "[Test 1] Testing admin access detection"
    {
        echo "192.168.1.1 - - [01/Nov/2024:10:00:00 +0000] \"GET /admin/ HTTP/1.1\" 403 0"
        echo "192.168.1.1 - - [01/Nov/2024:10:00:01 +0000] \"GET /admin/ HTTP/1.1\" 403 0"
        echo "192.168.1.1 - - [01/Nov/2024:10:00:02 +0000] \"GET /admin/ HTTP/1.1\" 403 0"
    } > "$TEST_BLOCKED_LOG"

    # Test 2: Check sensitive path detection
    echo "[Test 2] Testing sensitive path detection"
    {
        echo "192.168.1.2 - - [01/Nov/2024:10:00:00 +0000] \"GET /.env HTTP/1.1\" 403 0"
        echo "192.168.1.2 - - [01/Nov/2024:10:00:01 +0000] \"GET /.git/config HTTP/1.1\" 403 0"
    } >> "$TEST_BLOCKED_LOG"

    # Test 3: Check rate limiting
    echo "[Test 3] Testing rate limiting detection"
    for i in {1..51}; do
        echo "192.168.1.3 - - [01/Nov/2024:10:00:00 +0000] \"GET / HTTP/1.1\" 429 0" >> "$TEST_BLOCKED_LOG"
    done

    # Run tests with test log
    local orig_blocked_log="$BLOCKED_LOG"
    BLOCKED_LOG="$TEST_BLOCKED_LOG"

    check_admin_attempts
    check_sensitive_paths

    BLOCKED_LOG="$orig_blocked_log"

    log_message "INFO" "Tests completed. Check ${ALERT_LOG} for results."
    echo "Tests completed. Check ${ALERT_LOG} for results."
}

# Main function
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
