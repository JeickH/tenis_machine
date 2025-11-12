import sys
import argparse
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.models.trainer import ModelTrainer
from src.utils.logger import setup_logger

logger = setup_logger(__name__, 'training.log')

def main():
    parser = argparse.ArgumentParser(description='Train tennis prediction models')
    parser.add_argument('--tune', action='store_true', help='Enable hyperparameter tuning')
    parser.add_argument('--limit', type=int, help='Limit number of matches for training')
    args = parser.parse_args()

    print("\n=== Starting Model Training ===\n")

    trainer = ModelTrainer()

    print("Training all models...")
    if args.tune:
        print("(Hyperparameter tuning enabled)")

    results = trainer.train_all_models(tune_hyperparameters=args.tune, limit=args.limit)

    print("\n=== Training Results ===\n")

    for result in results:
        print(f"Model: {result['model_type']}")
        print(f"  Model ID: {result['model_id']}")
        print(f"  Accuracy: {result['accuracy']:.4f}")
        print(f"  Metrics: {result['metrics']}")
        print()

    if results:
        best = max(results, key=lambda x: x['accuracy'])
        print(f"✓ Best Model: {best['model_type']} (ID: {best['model_id']}) with accuracy {best['accuracy']:.4f}")
        print(f"\n✓ Model saved in: data/models/")
        print(f"✓ Model ID {best['model_id']} is now active\n")

    print("=== Training Completed ===\n")

if __name__ == "__main__":
    main()
