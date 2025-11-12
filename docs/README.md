# Tennis Machine - Documentation

This folder contains architecture and flow diagrams for the Tennis Machine system.

## Diagrams

### 1. Architecture by Modules (`architecture_by_modules.puml`)

**Purpose:** Shows the complete system organized by the 4 main modules

**Key Highlights:**
- **Module 1 - Data Extraction:** How match data is loaded and statistics are calculated
- **Module 2 - Model Training:** How training data is generated and models are trained
- **Module 3 - Prediction:** How daily predictions are made
- **Module 4 - Error Analysis:** How prediction accuracy is tracked

**Important:** This diagram shows that **FeatureEngineer** is the component responsible for generating training data dynamically. There's no table that stores training data - it's generated in memory from multiple source tables.

### 2. Database Schema (`database_schema.puml`)

**Purpose:** Shows all database tables and their relationships

**Tables organized by:**
- Reference Tables: players, tournaments, surfaces, court_types, rounds
- Main Tables: matches, player_stats, surface_history, external_predictions
- Model & Feature Tables: models, features, feature_configurations, training_configurations
- Prediction & Analysis Tables: predictions, prediction_errors, error_metrics

### 3. System Flow (`system_flow.puml`)

**Purpose:** Shows the execution flow of the 4 daily/weekly jobs

**Jobs:**
- Daily 6:00 AM: Data update
- Daily 8:00 AM: Predictions
- Daily 10:00 PM: Error analysis
- Sunday 2:00 AM: Model training

## How to View PlantUML Diagrams

### Option 1: Online Viewers

1. Copy the content of any `.puml` file
2. Paste into one of these online editors:
   - https://www.plantuml.com/plantuml/
   - https://planttext.com/
   - https://www.planttext.com/

### Option 2: VS Code Extension

1. Install "PlantUML" extension in VS Code
2. Open any `.puml` file
3. Press `Alt+D` to preview

### Option 3: Command Line

```bash
# Install PlantUML
brew install plantuml  # macOS
# or download from https://plantuml.com/download

# Generate PNG
plantuml architecture_by_modules.puml

# Generate SVG
plantuml -tsvg architecture_by_modules.puml
```

## Key Concepts Explained

### Training Data Generation

**Q: Where is the training data stored?**

**A:** Training data is **NOT stored in a table**. It's generated dynamically by the `FeatureEngineer` component.

**Process:**
1. FeatureEngineer queries multiple tables (matches, player_stats, surface_history, etc.)
2. Joins them together in a SQL query
3. Calculates derived features (rank_difference, sports_mood_difference, etc.)
4. Applies feature weights
5. Returns a pandas DataFrame with ~66,000 rows and 25+ features
6. This DataFrame is fed directly to the model trainer

**Why no table?**
- The source data is immutable (matches table)
- Features can be regenerated anytime
- Saves database space
- Allows dynamic feature engineering

### Feature Engineering Flow

```
[matches] ─┐
[player_stats] ─┤
[surface_history] ─┤──> [FeatureEngineer] ──> [DataFrame in RAM] ──> [ModelTrainer]
[tournaments] ─┤           (Python)              (25+ features)
[external_preds] ─┘
```

### Model Selection

The system trains multiple models and automatically selects the best one based on validation accuracy. The selected model is marked as `is_active = true` in the `models` table.

## SQL Queries

See [useful_queries.sql](useful_queries.sql) for common queries to:
- View active model
- Check predictions
- Analyze errors
- View player statistics
- Examine training runs

## Additional Resources

- Main README: `../README.md`
- Database Schema SQL: `../config/schema.sql`
- Python Source Code: `../src/`
