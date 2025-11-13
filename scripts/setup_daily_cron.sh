#!/bin/bash

# Setup Daily Cron Job for Tennis Predictions
# This script will add a cron job that runs daily until November 20, 2025

CRON_SCRIPT="/Users/equipo/Documents/predictor_deportivo/tenis_machine/scripts/daily_predictions_pipeline.sh"
CRON_TEMP_FILE="/tmp/tenis_machine_cron.txt"

echo "================================================"
echo "Setting up daily cron job for Tennis Machine"
echo "================================================"
echo ""

# Check if script exists
if [ ! -f "$CRON_SCRIPT" ]; then
    echo "Error: Script not found at $CRON_SCRIPT"
    exit 1
fi

# Define the cron job
# Runs every day at 8:00 AM until November 20, 2025
CRON_JOB="0 8 * * * [ \$(date +\%Y\%m\%d) -le 20251120 ] && $CRON_SCRIPT >> /Users/equipo/Documents/predictor_deportivo/tenis_machine/logs/cron_execution.log 2>&1"

# Get current crontab
crontab -l > "$CRON_TEMP_FILE" 2>/dev/null || true

# Check if cron job already exists
if grep -q "daily_predictions_pipeline.sh" "$CRON_TEMP_FILE"; then
    echo "⚠ Cron job already exists. Removing old one..."
    grep -v "daily_predictions_pipeline.sh" "$CRON_TEMP_FILE" > "${CRON_TEMP_FILE}.new"
    mv "${CRON_TEMP_FILE}.new" "$CRON_TEMP_FILE"
fi

# Add new cron job
echo "$CRON_JOB" >> "$CRON_TEMP_FILE"

# Install new crontab
crontab "$CRON_TEMP_FILE"

# Cleanup
rm -f "$CRON_TEMP_FILE"

echo "✓ Cron job installed successfully!"
echo ""
echo "Schedule: Daily at 8:00 AM"
echo "Duration: Until November 20, 2025"
echo "Script: $CRON_SCRIPT"
echo ""
echo "To view active cron jobs:"
echo "  crontab -l"
echo ""
echo "To remove the cron job:"
echo "  crontab -e  (then delete the line with 'daily_predictions_pipeline.sh')"
echo ""
echo "Logs will be saved to:"
echo "  /Users/equipo/Documents/predictor_deportivo/tenis_machine/logs/cron_execution.log"
echo ""
echo "================================================"

# Show current crontab
echo "Current crontab:"
crontab -l | grep -E "daily_predictions_pipeline|^#" || crontab -l
echo "================================================"
