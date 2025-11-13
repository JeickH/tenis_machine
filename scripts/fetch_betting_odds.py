import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime
from config.database import get_db
from src.data.betting_odds_fetcher import BettingOddsFetcher
from src.utils.logger import get_logger

logger = get_logger(__name__)

def main():
    print("=" * 60)
    print("   TENNIS MACHINE - BETTING ODDS FETCHER")
    print("=" * 60)
    print()

    today = datetime.now().date()
    print(f"📅 Fecha: {today.strftime('%d de %B de %Y')}")
    print()

    db = get_db()
    fetcher = BettingOddsFetcher()

    print("Step 1: Obteniendo partidos de hoy...")
    print("-" * 60)

    query = """
        SELECT
            m.id, m.date, m.tournament_id,
            m.player_1_id, m.player_2_id,
            p1.name as player_1_name,
            p2.name as player_2_name,
            t.name as tournament_name
        FROM matches m
        JOIN players p1 ON m.player_1_id = p1.id
        JOIN players p2 ON m.player_2_id = p2.id
        JOIN tournaments t ON m.tournament_id = t.id
        WHERE m.date = %s
        AND m.winner_id IS NULL
        AND t.series IN ('ATP500', 'Masters 1000', 'Grand Slam')
    """

    matches = db.execute_query(query, (today,), fetch=True)
    print(f"✓ Encontrados {len(matches)} partidos")
    print()

    if not matches:
        print("⚠ No hay partidos programados para hoy")
        return

    print("Step 2: Buscando cuotas en casas de apuestas...")
    print("-" * 60)

    total_odds = 0
    for i, match in enumerate(matches, 1):
        print(f"\n{i}. {match['player_1_name']} vs {match['player_2_name']}")
        print(f"   Torneo: {match['tournament_name']}")

        odds_data = fetcher.fetch_odds_for_match(
            match['date'],
            match['tournament_id'],
            match['player_1_id'],
            match['player_2_id'],
            match['player_1_name'],
            match['player_2_name']
        )

        if not odds_data:
            print(f"   ⚠ No se encontraron cuotas reales, creando datos de ejemplo...")
            fetcher.create_sample_odds_for_testing(
                match['date'],
                match['tournament_id'],
                match['player_1_id'],
                match['player_2_id']
            )
            total_odds += 2
            print(f"   ✓ Creadas 2 cuotas de ejemplo (Bet365, Betfair)")
        else:
            total_odds += len(odds_data)
            print(f"   ✓ Encontradas {len(odds_data)} cuotas")

    print()
    print("Step 3: Verificando cuotas guardadas...")
    print("-" * 60)

    query = """
        SELECT
            p1.name as player_1,
            p2.name as player_2,
            bo.bookmaker_name,
            bo.player_1_odds,
            bo.player_2_odds
        FROM betting_odds bo
        JOIN players p1 ON bo.player_1_id = p1.id
        JOIN players p2 ON bo.player_2_id = p2.id
        WHERE bo.match_date = %s
        ORDER BY p1.name, p2.name, bo.bookmaker_name
    """

    saved_odds = db.execute_query(query, (today,), fetch=True)

    print(f"✓ Total de cuotas guardadas: {len(saved_odds)}")
    print()

    print("📊 CUOTAS ENCONTRADAS:")
    print("-" * 60)

    current_match = None
    for odds in saved_odds:
        match_str = f"{odds['player_1']} vs {odds['player_2']}"
        if match_str != current_match:
            print(f"\n{match_str}")
            current_match = match_str

        print(f"  {odds['bookmaker_name']:20} | {odds['player_1_odds']:5} - {odds['player_2_odds']:5}")

    print()
    print("=" * 60)
    print("   ✅ BETTING ODDS FETCH COMPLETADO")
    print("=" * 60)
    print()

if __name__ == "__main__":
    main()
