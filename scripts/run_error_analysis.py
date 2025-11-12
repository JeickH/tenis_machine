import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.analysis.error_analyzer import ErrorAnalyzer
from src.utils.logger import setup_logger

logger = setup_logger(__name__, 'error_analysis.log')

def main():
    print("\n=== Running Error Analysis ===\n")

    analyzer = ErrorAnalyzer()

    print("Analyzing yesterday's predictions...")
    analyzer.analyze_yesterday()

    print("\n✓ Error analysis completed")
    print("\nTo view error metrics:")
    print("  SELECT * FROM error_metrics ORDER BY end_date DESC;\n")

    print("=== Analysis Completed ===\n")

if __name__ == "__main__":
    main()
