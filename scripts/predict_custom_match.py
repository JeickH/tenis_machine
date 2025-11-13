import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime
from config.database import get_db
from src.prediction.predictor import Predictor
from src.utils.database_utils import get_or_create_player
from src.data.sports_mood_calculator import SportsMoodCalculator
from src.data.surface_history_calculator import SurfaceHistoryCalculator

def predict_custom_match(player_1_name, player_2_name, tournament="Custom Match",
                        surface="Hard", court_type="Outdoor",
                        rank_1=None, rank_2=None):

    print("=" * 70)
    print("   TENNIS MACHINE - PREDICCIÓN PERSONALIZADA")
    print("=" * 70)
    print()

    db = get_db()

    # Get or create players
    print(f"Buscando jugadores en la base de datos...")
    player_1_id = get_or_create_player(player_1_name)
    player_2_id = get_or_create_player(player_2_name)

    # Get player info
    query = "SELECT name, current_rank FROM players WHERE id = %s"
    p1_info = db.execute_query(query, (player_1_id,), fetch=True)[0]
    p2_info = db.execute_query(query, (player_2_id,), fetch=True)[0]

    # Use database ranks if not provided
    if rank_1 is None:
        rank_1 = p1_info['current_rank'] if p1_info['current_rank'] else 100
    if rank_2 is None:
        rank_2 = p2_info['current_rank'] if p2_info['current_rank'] else 100

    print(f"✓ {p1_info['name']} (Ranking: {rank_1})")
    print(f"✓ {p2_info['name']} (Ranking: {rank_2})")
    print()

    # Calculate stats
    print("Calculando estadísticas de jugadores...")
    sports_mood_calc = SportsMoodCalculator()
    surface_calc = SurfaceHistoryCalculator()

    sports_mood_calc.update_player_sports_mood(player_1_id)
    sports_mood_calc.update_player_sports_mood(player_2_id)

    # Get surface ID
    surface_query = "SELECT id FROM surfaces WHERE name = %s"
    surface_result = db.execute_query(surface_query, (surface,), fetch=True)
    surface_id = surface_result[0]['id'] if surface_result else 1

    surface_calc.update_player_surface_history(player_1_id, surface_id)
    surface_calc.update_player_surface_history(player_2_id, surface_id)
    print("✓ Estadísticas calculadas")
    print()

    # Get tournament ID
    tournament_query = "SELECT id FROM tournaments WHERE name = %s"
    tournament_result = db.execute_query(tournament_query, (tournament,), fetch=True)

    if tournament_result:
        tournament_id = tournament_result[0]['id']
    else:
        # Create custom tournament
        insert_query = """
            INSERT INTO tournaments (name, series)
            VALUES (%s, %s)
            RETURNING id
        """
        result = db.execute_query(insert_query, (tournament, "ATP500"), fetch=True)
        tournament_id = result[0]['id']

    # Get court type ID
    court_type_query = "SELECT id FROM court_types WHERE name = %s"
    court_type_result = db.execute_query(court_type_query, (court_type,), fetch=True)
    court_type_id = court_type_result[0]['id'] if court_type_result else 2

    # Get round ID (default to "Final")
    round_query = "SELECT id FROM rounds WHERE name = %s"
    round_result = db.execute_query(round_query, ("Final",), fetch=True)
    round_id = round_result[0]['id'] if round_result else 1

    # Create temporary match for prediction
    today = datetime.now().date()
    match_query = """
        INSERT INTO matches
        (tournament_id, date, round_id, court_type_id, surface_id,
         player_1_id, player_2_id, rank_1, rank_2)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """

    match_result = db.execute_query(
        match_query,
        (tournament_id, today, round_id, court_type_id, surface_id,
         player_1_id, player_2_id, rank_1, rank_2),
        fetch=True
    )
    match_id = match_result[0]['id']

    print("Generando predicción...")
    print("-" * 70)

    # Load predictor and make prediction
    predictor = Predictor()
    predictor.load_active_model()

    # Get match data with all stats
    match_data_query = """
        SELECT
            m.id as match_id,
            m.date,
            m.tournament_id,
            m.player_1_id,
            m.player_2_id,
            m.surface_id,
            m.court_type_id,
            m.round_id,
            t.series as tournament_series,
            t.name as tournament_name,
            p1.name as player_1_name,
            p2.name as player_2_name,
            p1.current_rank as rank_1,
            p2.current_rank as rank_2,
            p1.current_points as pts_1,
            p2.current_points as pts_2,
            ps1.sports_mood_score as player_1_sports_mood,
            ps1.personal_mood_score as player_1_personal_mood,
            ps2.sports_mood_score as player_2_sports_mood,
            ps2.personal_mood_score as player_2_personal_mood,
            sh1.win_rate as player_1_surface_win_rate,
            sh2.win_rate as player_2_surface_win_rate
        FROM matches m
        JOIN tournaments t ON m.tournament_id = t.id
        JOIN players p1 ON m.player_1_id = p1.id
        JOIN players p2 ON m.player_2_id = p2.id
        LEFT JOIN player_stats ps1 ON m.player_1_id = ps1.player_id
        LEFT JOIN player_stats ps2 ON m.player_2_id = ps2.player_id
        LEFT JOIN surface_history sh1 ON m.player_1_id = sh1.player_id AND m.surface_id = sh1.surface_id
        LEFT JOIN surface_history sh2 ON m.player_2_id = sh2.player_id AND m.surface_id = sh2.surface_id
        WHERE m.id = %s
    """

    match_data = db.execute_query(match_data_query, (match_id,), fetch=True)[0]

    # Convert Decimals to float
    decimal_cols = ['player_1_sports_mood', 'player_2_sports_mood',
                   'player_1_personal_mood', 'player_2_personal_mood',
                   'player_1_surface_win_rate', 'player_2_surface_win_rate']

    for col in decimal_cols:
        if match_data.get(col) is not None:
            match_data[col] = float(match_data[col])

    # Make prediction
    prediction = predictor.predict_match(match_data)

    # Determine winner
    is_player_1_winner = prediction['predicted_winner_id'] == player_1_id
    winner_name = p1_info['name'] if is_player_1_winner else p2_info['name']

    # Display results
    print()
    print("=" * 70)
    print("   RESULTADO DE LA PREDICCIÓN")
    print("=" * 70)
    print()
    print(f"🎾 Partido:")
    print(f"   {p1_info['name']} (#{rank_1}) vs {p2_info['name']} (#{rank_2})")
    print()
    print(f"🏆 Ganador Predicho: {winner_name}")
    print(f"📊 Confianza: {prediction['confidence_score']*100:.2f}%")
    print(f"📈 Probabilidad de victoria: {prediction['winner_probability']*100:.2f}%")
    print()
    print(f"🏟️  Superficie: {surface}")
    print(f"🏢 Tipo de cancha: {court_type}")
    print(f"🏆 Torneo: {tournament}")
    print()

    # Show player stats
    print("📊 Estadísticas de los jugadores:")
    print("-" * 70)
    print(f"{p1_info['name']:25} | {p2_info['name']:25}")
    print("-" * 70)

    mood_1 = match_data.get('player_1_sports_mood', 0) or 0
    mood_2 = match_data.get('player_2_sports_mood', 0) or 0
    print(f"Sports Mood: {mood_1:10.2f}      | Sports Mood: {mood_2:10.2f}")

    surf_1 = match_data.get('player_1_surface_win_rate', 0) or 0
    surf_2 = match_data.get('player_2_surface_win_rate', 0) or 0
    print(f"Surface WR:  {surf_1*100:9.1f}%     | Surface WR:  {surf_2*100:9.1f}%")

    print()
    print("=" * 70)
    print(f"Modelo usado: {predictor.active_model['model_data']['model_type']}")
    print(f"Precisión del modelo: {float(predictor.active_model['model_data']['validation_accuracy'])*100:.2f}%")
    print("=" * 70)

    # Delete temporary match
    db.execute_query("DELETE FROM matches WHERE id = %s", (match_id,))

    return {
        'winner': winner_name,
        'confidence': prediction['confidence_score'],
        'probability': prediction['winner_probability']
    }

def main():
    print()
    print("=" * 70)
    print("   TENNIS MACHINE - PREDICCIÓN DE PARTIDO PERSONALIZADO")
    print("=" * 70)
    print()

    # Interactive mode
    if len(sys.argv) == 1:
        print("Ingresa los datos del partido:")
        print()
        player_1 = input("Jugador 1 (ej: Nadal R.): ").strip()
        player_2 = input("Jugador 2 (ej: Federer R.): ").strip()

        print()
        print("Superficie (opciones: Hard, Clay, Grass) [Default: Hard]: ", end="")
        surface = input().strip() or "Hard"

        print("Tipo de cancha (opciones: Indoor, Outdoor) [Default: Outdoor]: ", end="")
        court_type = input().strip() or "Outdoor"

        print("Torneo [Default: Custom Match]: ", end="")
        tournament = input().strip() or "Custom Match"

        print()
        rank_1_input = input(f"Ranking de {player_1} [Default: auto]: ").strip()
        rank_1 = int(rank_1_input) if rank_1_input else None

        rank_2_input = input(f"Ranking de {player_2} [Default: auto]: ").strip()
        rank_2 = int(rank_2_input) if rank_2_input else None

        print()

    # Command line mode
    elif len(sys.argv) >= 3:
        player_1 = sys.argv[1]
        player_2 = sys.argv[2]
        surface = sys.argv[3] if len(sys.argv) > 3 else "Hard"
        court_type = sys.argv[4] if len(sys.argv) > 4 else "Outdoor"
        tournament = sys.argv[5] if len(sys.argv) > 5 else "Custom Match"
        rank_1 = int(sys.argv[6]) if len(sys.argv) > 6 else None
        rank_2 = int(sys.argv[7]) if len(sys.argv) > 7 else None
    else:
        print("Uso:")
        print("  Modo interactivo:")
        print("    python3 predict_custom_match.py")
        print()
        print("  Modo comando:")
        print("    python3 predict_custom_match.py 'Jugador 1' 'Jugador 2' [superficie] [tipo_cancha] [torneo] [rank1] [rank2]")
        print()
        print("Ejemplos:")
        print("  python3 predict_custom_match.py 'Nadal R.' 'Federer R.'")
        print("  python3 predict_custom_match.py 'Djokovic N.' 'Alcaraz C.' Hard Indoor 'ATP Finals' 1 2")
        sys.exit(1)

    # Make prediction
    predict_custom_match(player_1, player_2, tournament, surface, court_type, rank_1, rank_2)

if __name__ == "__main__":
    main()
