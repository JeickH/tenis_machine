import sys
import json
import psycopg2
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from config.database import get_db
from src.utils.logger import setup_logger

logger = setup_logger(__name__, 'init_database.log')

def create_database():
    credentials_path = Path(__file__).parent.parent / "config" / "db_credentials.json"

    if not credentials_path.exists():
        logger.error("Database credentials file not found!")
        print("\nPlease create config/db_credentials.json with your PostgreSQL credentials")
        print("Use config/db_credentials.json.example as a template\n")
        return False

    with open(credentials_path, 'r') as f:
        credentials = json.load(f)

    try:
        conn = psycopg2.connect(
            host=credentials["host"],
            port=credentials["port"],
            user=credentials["user"],
            password=credentials["password"],
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()

        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{credentials['database']}'")
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(f"CREATE DATABASE {credentials['database']}")
            logger.info(f"Database '{credentials['database']}' created successfully")
            print(f"✓ Database '{credentials['database']}' created")
        else:
            logger.info(f"Database '{credentials['database']}' already exists")
            print(f"✓ Database '{credentials['database']}' already exists")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        logger.error(f"Error creating database: {e}")
        print(f"✗ Error creating database: {e}")
        return False

def run_schema():
    schema_path = Path(__file__).parent.parent / "config" / "schema.sql"

    try:
        with open(schema_path, 'r') as f:
            schema_sql = f.read()

        db = get_db()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(schema_sql)
            conn.commit()
            cursor.close()

        logger.info("Database schema created successfully")
        print("✓ Database schema created successfully")
        return True

    except Exception as e:
        logger.error(f"Error creating schema: {e}")
        print(f"✗ Error creating schema: {e}")
        return False

def insert_default_configurations():
    db = get_db()

    try:
        default_feature_config = {
            "player_1_rank": 1.0,
            "player_2_rank": 1.0,
            "rank_difference": 1.0,
            "player_1_points": 1.0,
            "player_2_points": 1.0,
            "points_difference": 1.0,
            "player_1_sports_mood": 1.0,
            "player_2_sports_mood": 1.0,
            "sports_mood_difference": 1.0,
            "player_1_personal_mood": 1.0,
            "player_2_personal_mood": 1.0,
            "personal_mood_difference": 1.0,
            "player_1_surface_win_rate": 1.0,
            "player_2_surface_win_rate": 1.0,
            "surface_advantage": 1.0,
            "h2h_player_1_wins": 1.0,
            "h2h_player_2_wins": 1.0,
            "h2h_total_matches": 1.0,
            "tournament_series_encoded": 1.0,
            "surface_encoded": 1.0,
            "court_type_encoded": 1.0,
            "round_encoded": 1.0,
            "external_predictions_player_1": 1.0,
            "external_predictions_player_2": 1.0,
            "external_confidence_avg": 1.0,
            "player_1_last_5_win_rate": 1.0,
            "player_2_last_5_win_rate": 1.0,
            "player_1_recent_form_trend": 1.0,
            "player_2_recent_form_trend": 1.0
        }

        query = """
            INSERT INTO feature_configurations (name, description, configuration, is_default)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (name) DO NOTHING
        """
        db.execute_query(
            query,
            ("default_weights_v1", "Default equal weights for all features", json.dumps(default_feature_config), True)
        )

        training_config_query = """
            INSERT INTO training_configurations
            (name, description, train_split_ratio, validation_split_ratio, is_default)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (name) DO NOTHING
        """
        db.execute_query(
            training_config_query,
            ("default_training_v1", "Default 80/20 train/validation split", 0.8, 0.2, True)
        )

        logger.info("Default configurations inserted successfully")
        print("✓ Default configurations inserted")
        return True

    except Exception as e:
        logger.error(f"Error inserting default configurations: {e}")
        print(f"✗ Error inserting configurations: {e}")
        return False

def main():
    print("\n=== Tennis Machine Database Initialization ===\n")

    print("Step 1: Creating database...")
    if not create_database():
        return

    print("\nStep 2: Creating schema...")
    if not run_schema():
        return

    print("\nStep 3: Inserting default configurations...")
    if not insert_default_configurations():
        return

    print("\n=== Database initialization completed successfully! ===\n")

if __name__ == "__main__":
    main()
