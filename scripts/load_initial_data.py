import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.data.match_loader import MatchLoader
from src.data.sports_mood_calculator import SportsMoodCalculator
from src.data.surface_history_calculator import SurfaceHistoryCalculator
from src.utils.logger import setup_logger

logger = setup_logger(__name__, 'load_initial_data.log')

def main():
    print("\n=== Loading Initial Historical Data ===\n")

    csv_path = Path(__file__).parent.parent / "data" / "raw" / "atp_tennis.csv"

    if not csv_path.exists():
        src_csv = Path(__file__).parent.parent.parent / "predictor_deportivo" / "datos" / "atp_tennis.csv"
        if src_csv.exists():
            import shutil
            csv_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src_csv, csv_path)
            print(f"✓ Copied CSV from {src_csv}")
        else:
            print(f"✗ CSV file not found at {csv_path}")
            print("Please download the ATP tennis dataset and place it in data/raw/atp_tennis.csv")
            return

    print("Step 1: Loading matches from CSV...")
    loader = MatchLoader()
    loaded, skipped = loader.load_from_csv(str(csv_path))
    print(f"✓ Loaded {loaded} matches, skipped {skipped}")

    print("\nStep 2: Calculating sports mood scores...")
    sports_mood_calc = SportsMoodCalculator()
    updated = sports_mood_calc.update_all_active_players()
    print(f"✓ Updated sports mood for {updated} players")

    print("\nStep 3: Calculating surface history...")
    surface_calc = SurfaceHistoryCalculator()
    updated = surface_calc.update_all_player_surfaces()
    print(f"✓ Updated {updated} player-surface combinations")

    print("\n=== Initial data loading completed! ===\n")

if __name__ == "__main__":
    main()
