import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.prediction.match_fetcher import MatchFetcher
from src.prediction.predictor import Predictor
from src.utils.logger import setup_logger

logger = setup_logger(__name__, 'test_prediction.log')

def main():
    print("\n=== Testing Tennis Prediction System ===\n")

    print("Step 1: Creating sample match for today...")
    fetcher = MatchFetcher()
    created = fetcher.create_sample_match_for_testing()

    if created > 0:
        print(f"✓ Created {created} sample match(es)")
    else:
        print("✗ Could not create sample match")
        return

    print("\nStep 2: Running prediction on sample match...")
    predictor = Predictor()

    print("Loading active model...")
    model_info = predictor.load_active_model()

    if not model_info:
        print("✗ No active model found")
        return

    print(f"✓ Loaded model: {model_info['model_data']['model_type']} (ID: {model_info['id']})")
    print(f"  Accuracy: {model_info['model_data']['validation_accuracy']:.4f}")

    print("\nMaking predictions...")
    predictions = predictor.predict_all_today()

    if predictions:
        print(f"\n=== Predictions Made ===\n")

        for pred in predictions:
            print(f"Tournament: {pred['tournament']}")
            print(f"  Match: {pred['match']}")
            print(f"  Predicted Winner: {pred['predicted_winner']}")
            print(f"  Confidence: {pred['confidence']:.2%}")
            print(f"  Prediction ID: {pred['prediction_id']}")
            print()

        print(f"✓ Total predictions: {len(predictions)}")
    else:
        print("No predictions made")

    print("\n=== Test Completed ===\n")

if __name__ == "__main__":
    main()
