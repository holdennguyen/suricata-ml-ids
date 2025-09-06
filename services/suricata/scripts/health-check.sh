#!/bin/bash

# Health check script for Suricata service
# Checks if Suricata is running and processing traffic

set -e

# Check if Suricata process is running
if ! pgrep -x "suricata" > /dev/null; then
    echo "ERROR: Suricata process not found"
    exit 1
fi

# Check if EVE log file exists and is being written to
EVE_LOG="/var/log/suricata/eve.json"
if [ ! -f "$EVE_LOG" ]; then
    echo "ERROR: EVE log file not found at $EVE_LOG"
    exit 1
fi

# Check if log file has been updated recently (within last 5 minutes)
if [ $(find "$EVE_LOG" -mmin -5 | wc -l) -eq 0 ]; then
    echo "WARNING: EVE log file not updated recently"
fi

# Check if unix socket exists for management
SOCKET="/var/run/suricata/suricata-command.socket"
if [ ! -S "$SOCKET" ]; then
    echo "WARNING: Suricata command socket not found"
fi

# Test basic functionality
if [ -f "$EVE_LOG" ] && [ -s "$EVE_LOG" ]; then
    # Check if we have recent events
    RECENT_EVENTS=$(tail -100 "$EVE_LOG" | grep '"timestamp"' | wc -l)
    if [ "$RECENT_EVENTS" -gt 0 ]; then
        echo "OK: Suricata is healthy and processing events ($RECENT_EVENTS recent events)"
        exit 0
    else
        echo "WARNING: No recent events found in EVE log"
        exit 0
    fi
else
    echo "WARNING: EVE log file is empty or missing"
    exit 0
fi
