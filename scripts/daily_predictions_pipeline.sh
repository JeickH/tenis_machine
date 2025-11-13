#!/bin/bash

# Daily Predictions Pipeline for Tennis Machine
# Runs daily predictions and generates HTML report

# Configuration
PROJECT_DIR="/Users/equipo/Documents/predictor_deportivo/tenis_machine"
VENV_PATH="$PROJECT_DIR/venv"
LOG_DIR="$PROJECT_DIR/logs"
REPORT_DIR="$PROJECT_DIR/reports"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Generate timestamp for log file
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/daily_predictions_$TIMESTAMP.log"

echo "========================================" | tee -a "$LOG_FILE"
echo "Tennis Machine - Daily Predictions" | tee -a "$LOG_FILE"
echo "Date: $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Change to project directory
cd "$PROJECT_DIR" || exit 1

# Activate virtual environment
source "$VENV_PATH/bin/activate" || {
    echo "Error: Could not activate virtual environment" | tee -a "$LOG_FILE"
    exit 1
}

# Step 1: Fetch today's matches
echo "Step 1: Fetching today's matches..." | tee -a "$LOG_FILE"
python3 scripts/predict_todays_real_matches.py >> "$LOG_FILE" 2>&1
FETCH_STATUS=$?

if [ $FETCH_STATUS -eq 0 ]; then
    echo "✓ Predictions completed successfully" | tee -a "$LOG_FILE"

    # Get today's date for report filename
    TODAY=$(date +%Y%m%d)
    REPORT_FILE="$REPORT_DIR/predictions_$TODAY.html"

    if [ -f "$REPORT_FILE" ]; then
        echo "✓ Report generated: $REPORT_FILE" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
        echo "To view the report, open: $REPORT_FILE" | tee -a "$LOG_FILE"
    else
        echo "⚠ Warning: Report file not found" | tee -a "$LOG_FILE"
    fi
else
    echo "✗ Error: Predictions failed with status $FETCH_STATUS" | tee -a "$LOG_FILE"
    exit 1
fi

echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "Daily predictions pipeline completed" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# Deactivate virtual environment
deactivate

exit 0
