import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.prediction.predictor import Predictor
from src.utils.logger import setup_logger

logger = setup_logger(__name__, 'prediction.log')

def main():
    print("\n=== Running Daily Predictions ===\n")

    predictor = Predictor()

    print("Loading active model...")
    model_info = predictor.load_active_model()

    if not model_info:
        print("✗ No active model found. Please train a model first.")
        return

    print(f"✓ Loaded model: {model_info['model_data']['model_type']} (ID: {model_info['id']})")
    print(f"  Accuracy: {model_info['model_data']['validation_accuracy']:.4f}\n")

    print("Fetching today's matches...")
    predictions = predictor.predict_all_today()

    if not predictions:
        print("No matches scheduled for today (ATP500+)")
        return

    print(f"\n=== Predictions for Today ===\n")

    for pred in predictions:
        print(f"Tournament: {pred['tournament']}")
        print(f"  Match: {pred['match']}")
        print(f"  Predicted Winner: {pred['predicted_winner']}")
        print(f"  Confidence: {pred['confidence']:.2%}")
        print(f"  Prediction ID: {pred['prediction_id']}")
        print()

    print(f"✓ Total predictions made: {len(predictions)}")
    print(f"✓ Predictions saved to database\n")

    print("To view predictions in the database:")
    print("  SELECT * FROM predictions WHERE prediction_timestamp::date = CURRENT_DATE;\n")

    print("=== Predictions Completed ===\n")

if __name__ == "__main__":
    main()
