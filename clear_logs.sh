#!/bin/bash
# Clear old logs and start fresh monitoring session

LOG_DIR="logs"
LOG_FILE="logs/realtime_debug.log"

echo "🧹 Clearing old logs..."

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Archive old log if it exists
if [ -f "$LOG_FILE" ]; then
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    ARCHIVE_FILE="${LOG_DIR}/realtime_debug_${TIMESTAMP}.log"
    mv "$LOG_FILE" "$ARCHIVE_FILE"
    echo "📦 Archived old log to: $ARCHIVE_FILE"
fi

echo "✅ Ready for fresh monitoring session!"
echo ""
echo "Next steps:"
echo "1. Run: streamlit run src/ui/app.py"
echo "2. Go to 'Live Monitoring' tab"
echo "3. Select your profile and start monitoring"
echo "4. Test with podcast + your voice"
echo "5. Stop monitoring"
echo "6. Run: python3 analyze_logs.py"
echo ""
