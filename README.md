# Tennis Machine

Machine learning pipeline for predicting ATP tennis match outcomes using historical data and advanced features.

## Features

- **Multi-Model Training**: Supports XGBoost, LightGBM, and more ML models
- **Advanced Features**:
  - Sports mood scoring based on recent performance
  - Surface-specific win rates
  - Head-to-head statistics
  - Ranking and points analysis
- **Automated Pipeline**: Daily data updates, predictions, and error analysis
- **Hyperparameter Tuning**: Automatic optimization for each model
- **Performance Tracking**: Comprehensive error metrics and model evaluation

## Project Structure

```
tenis_machine/
├── config/              # Configuration files
│   ├── database.py      # Database connection
│   ├── settings.py      # Global settings
│   └── schema.sql       # Database schema
├── src/
│   ├── data/           # Data extraction and processing
│   ├── models/         # Model training and implementations
│   ├── prediction/     # Prediction module
│   ├── analysis/       # Error analysis
│   └── utils/          # Utility functions
├── scripts/            # Executable scripts
├── data/
│   ├── raw/           # Raw data files
│   ├── processed/     # Processed data
│   └── models/        # Trained model files
└── logs/              # Log files
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Database

Create `config/db_credentials.json`:

```json
{
  "host": "localhost",
  "port": 5432,
  "database": "tenis_machine",
  "user": "postgres",
  "password": "your_password"
}
```

### 3. Initialize Database

```bash
python scripts/init_database.py
```

### 4. Load Historical Data

Place the ATP tennis CSV file in `data/raw/atp_tennis.csv`, then:

```bash
python scripts/load_initial_data.py
```

## Usage

### Train Models

Train all models with hyperparameter tuning:

```bash
python scripts/run_training.py --tune
```

Quick training without tuning:

```bash
python scripts/run_training.py
```

### Make Predictions

Predict today's ATP500+ matches:

```bash
python scripts/run_prediction.py
```

### Analyze Errors

Analyze yesterday's prediction errors:

```bash
python scripts/run_error_analysis.py
```

## Database Schema

### Core Tables

- **players**: Player information and rankings
- **tournaments**: Tournament registry
- **matches**: Historical match data
- **player_stats**: Enhanced player statistics (sports mood, personal mood)
- **surface_history**: Surface-specific performance

### Model Tables

- **models**: Trained model registry
- **feature_configurations**: Feature weight configurations
- **training_configurations**: Training parameters
- **predictions**: Model predictions
- **prediction_errors**: Error analysis results
- **error_metrics**: Aggregated performance metrics

## Results Location

### Trained Models
- **Files**: `data/models/*.pkl`
- **Database**: `SELECT * FROM models ORDER BY validation_accuracy DESC;`

### Predictions
- **Database**: `SELECT * FROM predictions WHERE prediction_timestamp::date = CURRENT_DATE;`

### Performance Metrics
- **Latest Metrics**: `SELECT * FROM error_metrics ORDER BY end_date DESC;`
- **Best Model**: `SELECT * FROM models WHERE is_active = true;`

### View Results Examples

```sql
-- View today's predictions
SELECT
    p1.name as player_1,
    p2.name as player_2,
    pw.name as predicted_winner,
    pred.confidence_score,
    t.name as tournament
FROM predictions pred
JOIN players p1 ON pred.player_1_id = p1.id
JOIN players p2 ON pred.player_2_id = p2.id
JOIN players pw ON pred.predicted_winner_id = pw.id
JOIN tournaments t ON pred.tournament_id = t.id
WHERE pred.prediction_timestamp::date = CURRENT_DATE;

-- View model performance
SELECT
    model_type,
    validation_accuracy,
    validation_metrics,
    training_date
FROM models
ORDER BY validation_accuracy DESC;

-- View error metrics
SELECT
    m.model_type,
    em.period,
    em.accuracy,
    em.total_predictions,
    em.accuracy_top_50
FROM error_metrics em
JOIN models m ON em.model_id = m.id
ORDER BY em.end_date DESC, em.period;
```

## Scheduled Jobs

Configure these jobs for automated operation:

- **Daily 6:00 AM**: Data update
- **Daily 8:00 AM**: Predictions
- **Daily 10:00 PM**: Error analysis
- **Weekly Sunday 2:00 AM**: Model training

## Feature Weights

Customize feature weights by creating a new configuration:

```sql
INSERT INTO feature_configurations (name, description, configuration)
VALUES (
    'custom_config',
    'Custom weight configuration',
    '{"player_1_rank": 1.5, "player_2_rank": 1.5, ...}'::jsonb
);
```

Then train with:

```bash
python scripts/run_training.py --feature-config custom_config
```

## Model Training Configuration

Models use 80/20 train/validation split by default. Customize in `training_configurations` table.

## License

MIT License

## Author

Generated with Claude Code
