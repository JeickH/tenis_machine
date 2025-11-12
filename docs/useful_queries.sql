-- Tennis Machine - Useful SQL Queries

-- ========================================
-- MODEL INFORMATION
-- ========================================

-- View active model details
SELECT
    id,
    model_name,
    model_type,
    model_version,
    validation_accuracy,
    training_date,
    validation_metrics
FROM models
WHERE is_active = true;

-- View all models ordered by accuracy
SELECT
    id,
    model_type,
    model_version,
    validation_accuracy,
    training_date,
    is_active
FROM models
ORDER BY validation_accuracy DESC;

-- ========================================
-- TODAY'S PREDICTIONS
-- ========================================

-- View today's predictions with player names
SELECT
    p.id as prediction_id,
    t.name as tournament,
    p1.name as player_1,
    p2.name as player_2,
    pw.name as predicted_winner,
    p.predicted_total_sets,
    p.predicted_total_games,
    p.winner_probability,
    p.confidence_score,
    p.prediction_timestamp
FROM predictions p
JOIN players p1 ON p.player_1_id = p1.id
JOIN players p2 ON p.player_2_id = p2.id
JOIN players pw ON p.predicted_winner_id = pw.id
JOIN tournaments t ON p.tournament_id = t.id
WHERE p.prediction_timestamp::date = CURRENT_DATE
ORDER BY p.prediction_timestamp DESC;

-- ========================================
-- RECENT PREDICTIONS
-- ========================================

-- View last 10 predictions
SELECT
    p.id,
    p1.name as player_1,
    p2.name as player_2,
    pw.name as predicted_winner,
    CASE
        WHEN p.actual_winner_id IS NULL THEN 'Pending'
        WHEN p.predicted_winner_id = p.actual_winner_id THEN 'Correct'
        ELSE 'Incorrect'
    END as prediction_result,
    p.confidence_score,
    p.match_date
FROM predictions p
JOIN players p1 ON p.player_1_id = p1.id
JOIN players p2 ON p.player_2_id = p2.id
JOIN players pw ON p.predicted_winner_id = pw.id
ORDER BY p.prediction_timestamp DESC
LIMIT 10;

-- ========================================
-- ERROR METRICS
-- ========================================

-- Latest error metrics summary
SELECT
    m.model_type,
    em.period,
    em.total_predictions,
    em.correct_winners,
    ROUND(em.accuracy::numeric, 4) as accuracy,
    ROUND(em.avg_sets_error::numeric, 2) as avg_sets_error,
    ROUND(em.avg_games_error::numeric, 2) as avg_games_error,
    em.end_date
FROM error_metrics em
JOIN models m ON em.model_id = m.id
WHERE m.is_active = true
ORDER BY em.end_date DESC,
    CASE em.period
        WHEN 'last_day' THEN 1
        WHEN 'last_week' THEN 2
        WHEN 'last_15_days' THEN 3
        WHEN 'last_month' THEN 4
    END;

-- Accuracy by ranking tier
SELECT
    m.model_type,
    em.period,
    ROUND(em.accuracy::numeric, 4) as overall_accuracy,
    ROUND(em.accuracy_top_10::numeric, 4) as top_10_accuracy,
    ROUND(em.accuracy_top_50::numeric, 4) as top_50_accuracy,
    ROUND(em.accuracy_both_top_10::numeric, 4) as both_top_10_accuracy,
    ROUND(em.accuracy_both_top_50::numeric, 4) as both_top_50_accuracy
FROM error_metrics em
JOIN models m ON em.model_id = m.id
WHERE em.period = 'last_month'
AND m.is_active = true;

-- ========================================
-- PREDICTION ERRORS DETAIL
-- ========================================

-- View recent prediction errors with details
SELECT
    pe.id,
    pe.match_date,
    p1.name as player_1,
    p2.name as player_2,
    CASE WHEN pe.winner_correct THEN 'Correct' ELSE 'Incorrect' END as prediction_outcome,
    pe.sets_error,
    pe.games_error,
    pe.player_1_rank,
    pe.player_2_rank,
    CASE
        WHEN pe.both_top_10 THEN 'Both Top 10'
        WHEN pe.both_top_50 THEN 'Both Top 50'
        WHEN pe.any_top_10 THEN 'One Top 10'
        ELSE 'Other'
    END as ranking_category
FROM prediction_errors pe
JOIN players p1 ON pe.player_1_id = p1.id
JOIN players p2 ON pe.player_2_id = p2.id
ORDER BY pe.match_date DESC
LIMIT 20;

-- ========================================
-- PLAYER STATISTICS
-- ========================================

-- Top players by sports mood score
SELECT
    p.name,
    p.current_rank,
    ps.sports_mood_score,
    ps.last_10_matches_wins,
    ps.last_10_matches_losses,
    ps.total_career_wins,
    ps.total_career_losses
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE p.current_rank <= 100
ORDER BY ps.sports_mood_score DESC
LIMIT 20;

-- Player surface performance
SELECT
    p.name,
    s.name as surface,
    sh.win_rate,
    sh.last_10_wins,
    sh.last_10_losses,
    sh.total_wins,
    sh.total_losses
FROM surface_history sh
JOIN players p ON sh.player_id = p.id
JOIN surfaces s ON sh.surface_id = s.id
WHERE p.current_rank <= 50
ORDER BY p.current_rank, s.name;

-- ========================================
-- MATCH HISTORY
-- ========================================

-- Recent matches
SELECT
    m.date,
    t.name as tournament,
    s.name as surface,
    p1.name as player_1,
    p2.name as player_2,
    w.name as winner,
    m.score,
    m.total_sets,
    m.total_games
FROM matches m
JOIN tournaments t ON m.tournament_id = t.id
JOIN surfaces s ON m.surface_id = s.id
JOIN players p1 ON m.player_1_id = p1.id
JOIN players p2 ON m.player_2_id = p2.id
JOIN players w ON m.winner_id = w.id
ORDER BY m.date DESC
LIMIT 20;

-- Head-to-head between two players (replace names)
SELECT
    m.date,
    t.name as tournament,
    p1.name as player_1,
    p2.name as player_2,
    w.name as winner,
    m.score
FROM matches m
JOIN tournaments t ON m.tournament_id = t.id
JOIN players p1 ON m.player_1_id = p1.id
JOIN players p2 ON m.player_2_id = p2.id
JOIN players w ON m.winner_id = w.id
WHERE (p1.name = 'Nadal R.' AND p2.name = 'Federer R.')
   OR (p1.name = 'Federer R.' AND p2.name = 'Nadal R.')
ORDER BY m.date DESC;

-- ========================================
-- DATABASE STATISTICS
-- ========================================

-- Overall database statistics
SELECT
    (SELECT COUNT(*) FROM players WHERE is_active = true) as active_players,
    (SELECT COUNT(*) FROM matches) as total_matches,
    (SELECT COUNT(*) FROM tournaments WHERE is_active = true) as active_tournaments,
    (SELECT COUNT(*) FROM predictions) as total_predictions,
    (SELECT COUNT(*) FROM models) as total_models,
    (SELECT COUNT(*) FROM models WHERE is_active = true) as active_models;

-- Matches by tournament series
SELECT
    t.series,
    COUNT(*) as match_count,
    COUNT(DISTINCT m.tournament_id) as tournament_count
FROM matches m
JOIN tournaments t ON m.tournament_id = t.id
GROUP BY t.series
ORDER BY match_count DESC;

-- Matches by surface
SELECT
    s.name as surface,
    COUNT(*) as match_count
FROM matches m
JOIN surfaces s ON m.surface_id = s.id
GROUP BY s.name
ORDER BY match_count DESC;

-- ========================================
-- FEATURE CONFIGURATIONS
-- ========================================

-- View current feature configuration
SELECT
    fc.name,
    fc.description,
    fc.configuration,
    fc.is_default
FROM feature_configurations fc
ORDER BY fc.is_default DESC, fc.created_at DESC;

-- View training configurations
SELECT
    tc.name,
    tc.description,
    tc.train_split_ratio,
    tc.validation_split_ratio,
    tc.use_error_feedback,
    tc.is_default
FROM training_configurations tc
ORDER BY tc.is_default DESC, tc.created_at DESC;
