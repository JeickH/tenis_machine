from config.database import get_db
from src.utils.logger import get_logger

logger = get_logger(__name__)

def get_or_create_player(player_name, country=None):
    db = get_db()

    query = "SELECT id FROM players WHERE name = %s"
    result = db.execute_query(query, (player_name,), fetch=True)

    if result:
        return result[0]['id']

    insert_query = """
        INSERT INTO players (name, country, is_active)
        VALUES (%s, %s, %s)
        RETURNING id
    """
    result = db.execute_query(insert_query, (player_name, country, True), fetch=True)
    logger.info(f"Created new player: {player_name}")
    return result[0]['id']

def get_or_create_tournament(tournament_name, series=None):
    db = get_db()

    query = "SELECT id FROM tournaments WHERE name = %s"
    result = db.execute_query(query, (tournament_name,), fetch=True)

    if result:
        return result[0]['id']

    insert_query = """
        INSERT INTO tournaments (name, series, is_active)
        VALUES (%s, %s, %s)
        RETURNING id
    """
    result = db.execute_query(insert_query, (tournament_name, series, True), fetch=True)
    logger.info(f"Created new tournament: {tournament_name}")
    return result[0]['id']

def get_surface_id(surface_name):
    db = get_db()
    query = "SELECT id FROM surfaces WHERE name = %s"
    result = db.execute_query(query, (surface_name,), fetch=True)
    return result[0]['id'] if result else None

def get_court_type_id(court_type_name):
    db = get_db()
    query = "SELECT id FROM court_types WHERE name = %s"
    result = db.execute_query(query, (court_type_name,), fetch=True)
    return result[0]['id'] if result else None

def get_round_id(round_name):
    db = get_db()
    query = "SELECT id FROM rounds WHERE name = %s"
    result = db.execute_query(query, (round_name,), fetch=True)
    return result[0]['id'] if result else None

def update_player_rank(player_id, rank, points):
    db = get_db()
    query = """
        UPDATE players
        SET current_rank = %s, current_points = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
    """
    db.execute_query(query, (rank, points, player_id))

def match_exists(tournament_id, date, player_1_id, player_2_id):
    db = get_db()
    query = """
        SELECT id FROM matches
        WHERE tournament_id = %s AND date = %s
        AND ((player_1_id = %s AND player_2_id = %s)
             OR (player_1_id = %s AND player_2_id = %s))
    """
    result = db.execute_query(
        query,
        (tournament_id, date, player_1_id, player_2_id, player_2_id, player_1_id),
        fetch=True
    )
    return result[0]['id'] if result else None

def get_player_last_n_matches(player_id, n=10, surface_id=None):
    db = get_db()

    surface_filter = "AND surface_id = %s" if surface_id else ""
    params = [player_id, player_id]
    if surface_id:
        params.append(surface_id)
    params.append(n)

    query = f"""
        SELECT
            m.*,
            p1.name as player_1_name,
            p2.name as player_2_name,
            w.name as winner_name
        FROM matches m
        JOIN players p1 ON m.player_1_id = p1.id
        JOIN players p2 ON m.player_2_id = p2.id
        LEFT JOIN players w ON m.winner_id = w.id
        WHERE (m.player_1_id = %s OR m.player_2_id = %s)
        {surface_filter}
        AND m.winner_id IS NOT NULL
        ORDER BY m.date DESC
        LIMIT %s
    """

    return db.execute_query(query, tuple(params), fetch=True)

def get_head_to_head(player_1_id, player_2_id):
    db = get_db()
    query = """
        SELECT
            COUNT(*) as total_matches,
            SUM(CASE WHEN winner_id = %s THEN 1 ELSE 0 END) as player_1_wins,
            SUM(CASE WHEN winner_id = %s THEN 1 ELSE 0 END) as player_2_wins
        FROM matches
        WHERE (player_1_id = %s AND player_2_id = %s)
           OR (player_1_id = %s AND player_2_id = %s)
    """
    result = db.execute_query(
        query,
        (player_1_id, player_2_id, player_1_id, player_2_id, player_2_id, player_1_id),
        fetch=True
    )
    return result[0] if result else {"total_matches": 0, "player_1_wins": 0, "player_2_wins": 0}
