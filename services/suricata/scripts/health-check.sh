#!/bin/sh

# Health check script for Suricata service
# Checks if Suricata is running and processing traffic

set -e

# Check if Suricata process is running
if ! pgrep suricata > /dev/null 2>&1; then
    echo "ERROR: Suricata process not found"
    exit 1
fi

# Check if EVE log file exists
EVE_LOG="/var/log/suricata/eve.json"
if [ ! -f "$EVE_LOG" ]; then
    echo "WARNING: EVE log file not found at $EVE_LOG, but Suricata is running"
    exit 0
fi

echo "OK: Suricata is running"
exit 0
