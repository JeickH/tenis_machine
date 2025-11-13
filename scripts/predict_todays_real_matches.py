import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime
from src.prediction.match_fetcher import MatchFetcher
from src.prediction.predictor import Predictor
from src.utils.html_report_generator import HTMLReportGenerator
from src.utils.logger import get_logger

logger = get_logger(__name__)

def main():
    print("=" * 60)
    print("   TENNIS MACHINE - PREDICCIONES REALES DE HOY")
    print("=" * 60)
    print()

    today = datetime.now()
    print(f"📅 Fecha: {today.strftime('%d de %B de %Y')}")
    print()

    print("Step 1: Agregando partidos reales de hoy...")
    print("-" * 60)
    fetcher = MatchFetcher()
    matches_saved = fetcher.create_todays_real_matches()

    if matches_saved > 0:
        print(f"✓ Se agregaron {matches_saved} partidos reales")
    else:
        print("⚠ Los partidos ya existen en la base de datos")
    print()

    print("Step 2: Generando predicciones...")
    print("-" * 60)
    predictor = Predictor()
    predictions = predictor.predict_all_today()

    print(f"✓ Predicciones completadas: {len(predictions)}")
    print()

    if predictions:
        print("📊 PREDICCIONES:")
        print("-" * 60)
        print()

        for i, pred in enumerate(predictions, 1):
            print(f"{i}. {pred['tournament']}")
            print(f"   {pred['match']}")
            print(f"   → Ganador Predicho: {pred['predicted_winner']}")
            print(f"   → Confianza: {pred['confidence']*100:.2f}%")
            print()

    print("Step 3: Generando reporte HTML...")
    print("-" * 60)
    report_gen = HTMLReportGenerator()
    report_path = report_gen.generate_daily_report()

    print(f"✓ Reporte generado exitosamente")
    print(f"  📄 Ubicación: {report_path}")
    print(f"  🌐 Abre el archivo en tu navegador para ver el reporte")
    print()

    print("=" * 60)
    print("   ✅ PREDICCIONES COMPLETADAS")
    print("=" * 60)
    print()
    print("📈 Resumen:")
    print(f"  • Partidos agregados: {matches_saved}")
    print(f"  • Predicciones realizadas: {len(predictions)}")
    print(f"  • Reporte: {report_path.name}")
    print()

if __name__ == "__main__":
    main()
