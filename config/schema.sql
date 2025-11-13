-- Tennis Match Prediction Database Schema

-- Reference Tables

CREATE TABLE IF NOT EXISTS players (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    country VARCHAR(3),
    birth_date DATE,
    current_rank INTEGER,
    current_points INTEGER,
    highest_rank INTEGER,
    highest_rank_date DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_players_name ON players(name);
CREATE INDEX idx_players_rank ON players(current_rank);

CREATE TABLE IF NOT EXISTS tournaments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    series VARCHAR(50),
    category VARCHAR(100),
    location VARCHAR(255),
    country VARCHAR(3),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tournaments_name ON tournaments(name);
CREATE INDEX idx_tournaments_series ON tournaments(series);

CREATE TABLE IF NOT EXISTS surfaces (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_surfaces_name ON surfaces(name);

CREATE TABLE IF NOT EXISTS court_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_court_types_name ON court_types(name);

CREATE TABLE IF NOT EXISTS rounds (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    order_number INTEGER,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_rounds_name ON rounds(name);
CREATE INDEX idx_rounds_order ON rounds(order_number);

-- Main Match Data

CREATE TABLE IF NOT EXISTS matches (
    id SERIAL PRIMARY KEY,
    tournament_id INTEGER REFERENCES tournaments(id),
    date DATE NOT NULL,
    round_id INTEGER REFERENCES rounds(id),
    court_type_id INTEGER REFERENCES court_types(id),
    surface_id INTEGER REFERENCES surfaces(id),
    best_of INTEGER,
    player_1_id INTEGER REFERENCES players(id) NOT NULL,
    player_2_id INTEGER REFERENCES players(id) NOT NULL,
    winner_id INTEGER REFERENCES players(id),
    rank_1 INTEGER,
    rank_2 INTEGER,
    pts_1 INTEGER,
    pts_2 INTEGER,
    odd_1 DECIMAL(10, 2),
    odd_2 DECIMAL(10, 2),
    score VARCHAR(100),
    total_sets INTEGER,
    total_games INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_different_players CHECK (player_1_id != player_2_id)
);

CREATE INDEX idx_matches_date ON matches(date);
CREATE INDEX idx_matches_player1 ON matches(player_1_id);
CREATE INDEX idx_matches_player2 ON matches(player_2_id);
CREATE INDEX idx_matches_tournament ON matches(tournament_id);
CREATE INDEX idx_matches_surface ON matches(surface_id);
CREATE INDEX idx_matches_winner ON matches(winner_id);

-- Player Statistics

CREATE TABLE IF NOT EXISTS player_stats (
    id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(id) UNIQUE NOT NULL,
    sports_mood_score DECIMAL(5, 2),
    last_10_matches_wins INTEGER,
    last_10_matches_losses INTEGER,
    last_10_matches_details JSONB,
    personal_mood_score DECIMAL(5, 2),
    last_mood_update TIMESTAMP,
    total_career_wins INTEGER,
    total_career_losses INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_player_stats_player_id ON player_stats(player_id);

CREATE TABLE IF NOT EXISTS surface_history (
    id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(id) NOT NULL,
    surface_id INTEGER REFERENCES surfaces(id) NOT NULL,
    last_10_wins INTEGER,
    last_10_losses INTEGER,
    win_rate DECIMAL(5, 4),
    total_wins INTEGER,
    total_losses INTEGER,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_player_surface UNIQUE (player_id, surface_id)
);

CREATE INDEX idx_surface_history_player ON surface_history(player_id);
CREATE INDEX idx_surface_history_surface ON surface_history(surface_id);

CREATE TABLE IF NOT EXISTS player_news (
    id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(id) NOT NULL,
    news_date DATE NOT NULL,
    news_summary TEXT,
    news_category VARCHAR(50),
    sentiment_score DECIMAL(5, 2),
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_player_news_player ON player_news(player_id);
CREATE INDEX idx_player_news_date ON player_news(news_date);

-- External Predictions

CREATE TABLE IF NOT EXISTS external_predictions (
    id SERIAL PRIMARY KEY,
    match_date DATE NOT NULL,
    tournament_id INTEGER REFERENCES tournaments(id),
    player_1_id INTEGER REFERENCES players(id) NOT NULL,
    player_2_id INTEGER REFERENCES players(id) NOT NULL,
    source_name VARCHAR(255) NOT NULL,
    source_url TEXT,
    predicted_winner_id INTEGER REFERENCES players(id),
    confidence_score DECIMAL(5, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_external_predictions_date ON external_predictions(match_date);
CREATE INDEX idx_external_predictions_players ON external_predictions(player_1_id, player_2_id);
CREATE INDEX idx_external_predictions_source ON external_predictions(source_name);

-- Betting Odds

CREATE TABLE IF NOT EXISTS betting_odds (
    id SERIAL PRIMARY KEY,
    match_date DATE NOT NULL,
    tournament_id INTEGER REFERENCES tournaments(id),
    player_1_id INTEGER REFERENCES players(id) NOT NULL,
    player_2_id INTEGER REFERENCES players(id) NOT NULL,
    bookmaker_name VARCHAR(255) NOT NULL,
    player_1_odds DECIMAL(6, 2),
    player_2_odds DECIMAL(6, 2),
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_match_bookmaker UNIQUE (match_date, player_1_id, player_2_id, bookmaker_name)
);

CREATE INDEX idx_betting_odds_date ON betting_odds(match_date);
CREATE INDEX idx_betting_odds_players ON betting_odds(player_1_id, player_2_id);
CREATE INDEX idx_betting_odds_bookmaker ON betting_odds(bookmaker_name);

-- Feature Management

CREATE TABLE IF NOT EXISTS features (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    feature_type VARCHAR(50) NOT NULL,
    data_source VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_features_name ON features(name);
CREATE INDEX idx_features_active ON features(is_active);

CREATE TABLE IF NOT EXISTS feature_configurations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    configuration JSONB NOT NULL,
    is_default BOOLEAN DEFAULT false,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_feature_configurations_name ON feature_configurations(name);
CREATE INDEX idx_feature_configurations_default ON feature_configurations(is_default);

CREATE TABLE IF NOT EXISTS training_configurations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    train_split_ratio DECIMAL(3, 2) DEFAULT 0.8,
    validation_split_ratio DECIMAL(3, 2) DEFAULT 0.2,
    test_split_ratio DECIMAL(3, 2) DEFAULT 0.0,
    random_seed INTEGER DEFAULT 42,
    cross_validation_folds INTEGER,
    min_samples_per_class INTEGER,
    stratify_by VARCHAR(100),
    date_cutoff DATE,
    use_error_feedback BOOLEAN DEFAULT false,
    feature_configuration_id INTEGER REFERENCES feature_configurations(id),
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_training_configurations_name ON training_configurations(name);
CREATE INDEX idx_training_configurations_default ON training_configurations(is_default);

CREATE TABLE IF NOT EXISTS training_runs (
    id SERIAL PRIMARY KEY,
    model_id INTEGER,
    training_configuration_id INTEGER REFERENCES training_configurations(id),
    feature_configuration_id INTEGER REFERENCES feature_configurations(id),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status VARCHAR(50) NOT NULL,
    train_samples INTEGER,
    validation_samples INTEGER,
    test_samples INTEGER,
    training_metrics JSONB,
    validation_metrics JSONB,
    test_metrics JSONB,
    best_hyperparameters JSONB,
    feature_importance JSONB,
    error_log TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_training_runs_model ON training_runs(model_id);
CREATE INDEX idx_training_runs_status ON training_runs(status);
CREATE INDEX idx_training_runs_start_time ON training_runs(start_time);

-- Model Registry

CREATE TABLE IF NOT EXISTS models (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(255) NOT NULL,
    model_type VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    training_run_id INTEGER REFERENCES training_runs(id),
    training_configuration_id INTEGER REFERENCES training_configurations(id),
    feature_configuration_id INTEGER REFERENCES feature_configurations(id),
    hyperparameters JSONB,
    training_date TIMESTAMP NOT NULL,
    training_samples_count INTEGER,
    validation_samples_count INTEGER,
    validation_accuracy DECIMAL(5, 4),
    validation_metrics JSONB,
    model_file_path VARCHAR(500) NOT NULL,
    weights_file_path VARCHAR(500),
    feature_importance JSONB,
    is_active BOOLEAN DEFAULT false,
    use_error_feedback BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_models_active ON models(is_active);
CREATE INDEX idx_models_validation_accuracy ON models(validation_accuracy DESC);
CREATE INDEX idx_models_type ON models(model_type);
CREATE INDEX idx_models_training_run ON models(training_run_id);

CREATE TABLE IF NOT EXISTS feature_weights (
    id SERIAL PRIMARY KEY,
    model_id INTEGER REFERENCES models(id),
    feature_id INTEGER REFERENCES features(id),
    weight DECIMAL(10, 6) NOT NULL,
    is_enabled BOOLEAN DEFAULT true,
    importance_score DECIMAL(10, 6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_model_feature UNIQUE (model_id, feature_id)
);

CREATE INDEX idx_feature_weights_model ON feature_weights(model_id);
CREATE INDEX idx_feature_weights_feature ON feature_weights(feature_id);
CREATE INDEX idx_feature_weights_enabled ON feature_weights(is_enabled);

-- Predictions

CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    model_id INTEGER REFERENCES models(id) NOT NULL,
    match_date DATE NOT NULL,
    tournament_id INTEGER REFERENCES tournaments(id),
    player_1_id INTEGER REFERENCES players(id) NOT NULL,
    player_2_id INTEGER REFERENCES players(id) NOT NULL,
    predicted_winner_id INTEGER REFERENCES players(id) NOT NULL,
    predicted_total_sets INTEGER,
    predicted_total_games INTEGER,
    winner_probability DECIMAL(5, 4),
    confidence_score DECIMAL(5, 4),
    prediction_timestamp TIMESTAMP NOT NULL,
    actual_winner_id INTEGER REFERENCES players(id),
    actual_total_sets INTEGER,
    actual_total_games INTEGER,
    match_id INTEGER REFERENCES matches(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_different_players_pred CHECK (player_1_id != player_2_id)
);

CREATE INDEX idx_predictions_match_date ON predictions(match_date);
CREATE INDEX idx_predictions_model ON predictions(model_id);
CREATE INDEX idx_predictions_players ON predictions(player_1_id, player_2_id);
CREATE INDEX idx_predictions_timestamp ON predictions(prediction_timestamp);

-- Error Analysis

CREATE TABLE IF NOT EXISTS prediction_errors (
    id SERIAL PRIMARY KEY,
    prediction_id INTEGER REFERENCES predictions(id) UNIQUE NOT NULL,
    model_id INTEGER REFERENCES models(id) NOT NULL,
    match_id INTEGER REFERENCES matches(id) NOT NULL,
    match_date DATE NOT NULL,
    player_1_id INTEGER REFERENCES players(id) NOT NULL,
    player_2_id INTEGER REFERENCES players(id) NOT NULL,
    winner_correct BOOLEAN,
    sets_error INTEGER,
    games_error INTEGER,
    player_1_rank INTEGER,
    player_2_rank INTEGER,
    both_top_10 BOOLEAN,
    both_top_20 BOOLEAN,
    both_top_50 BOOLEAN,
    both_top_100 BOOLEAN,
    any_top_10 BOOLEAN,
    any_top_20 BOOLEAN,
    any_top_50 BOOLEAN,
    any_top_100 BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_prediction_errors_model ON prediction_errors(model_id);
CREATE INDEX idx_prediction_errors_date ON prediction_errors(match_date);
CREATE INDEX idx_prediction_errors_correct ON prediction_errors(winner_correct);
CREATE INDEX idx_prediction_errors_rankings ON prediction_errors(both_top_10, both_top_20, both_top_50, both_top_100);

CREATE TABLE IF NOT EXISTS error_metrics (
    id SERIAL PRIMARY KEY,
    model_id INTEGER REFERENCES models(id) NOT NULL,
    period VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_predictions INTEGER,
    correct_winners INTEGER,
    accuracy DECIMAL(5, 4),
    avg_sets_error DECIMAL(5, 2),
    avg_games_error DECIMAL(5, 2),
    accuracy_top_10 DECIMAL(5, 4),
    accuracy_top_20 DECIMAL(5, 4),
    accuracy_top_50 DECIMAL(5, 4),
    accuracy_top_100 DECIMAL(5, 4),
    accuracy_both_top_10 DECIMAL(5, 4),
    accuracy_both_top_20 DECIMAL(5, 4),
    accuracy_both_top_50 DECIMAL(5, 4),
    accuracy_both_top_100 DECIMAL(5, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_model_period UNIQUE (model_id, period, end_date)
);

CREATE INDEX idx_error_metrics_model ON error_metrics(model_id);
CREATE INDEX idx_error_metrics_period ON error_metrics(period);
CREATE INDEX idx_error_metrics_date_range ON error_metrics(start_date, end_date);

-- Insert initial reference data

INSERT INTO surfaces (name, description) VALUES
    ('Hard', 'Hard court surface'),
    ('Clay', 'Clay court surface'),
    ('Grass', 'Grass court surface'),
    ('Carpet', 'Carpet court surface')
ON CONFLICT (name) DO NOTHING;

INSERT INTO court_types (name, description) VALUES
    ('Indoor', 'Indoor court'),
    ('Outdoor', 'Outdoor court')
ON CONFLICT (name) DO NOTHING;

INSERT INTO rounds (name, order_number, description) VALUES
    ('1st Round', 1, 'First round of tournament'),
    ('2nd Round', 2, 'Second round of tournament'),
    ('3rd Round', 3, 'Third round of tournament'),
    ('4th Round', 4, 'Fourth round of tournament'),
    ('Quarterfinals', 5, 'Quarter finals'),
    ('Semifinals', 6, 'Semi finals'),
    ('The Final', 7, 'Final match')
ON CONFLICT (name) DO NOTHING;
