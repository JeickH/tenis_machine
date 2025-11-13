import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from src.prediction.match_fetcher import MatchFetcher
from src.prediction.predictor import Predictor
from src.utils.html_report_generator import HTMLReportGenerator
from src.utils.logger import setup_logger

logger = setup_logger(__name__, 'full_pipeline.log')

def main():
    print("\n" + "="*60)
    print("   TENNIS MACHINE - FULL PREDICTION PIPELINE")
    print("="*60 + "\n")

    today = datetime.now().date()
    print(f"📅 Fecha: {today.strftime('%d de %B de %Y')}\n")

    print("Step 1: Buscando partidos de hoy...")
    print("-" * 60)

    fetcher = MatchFetcher()

    web_matches = fetcher.fetch_todays_matches_from_web()

    if web_matches:
        print(f"✓ Encontrados {len(web_matches)} partidos en la web")
        saved = fetcher.save_scheduled_matches(web_matches)
        print(f"✓ Guardados {saved} partidos nuevos en la base de datos")
    else:
        print("⚠ No se encontraron partidos en la web")
        print("  Creando partido de ejemplo para demostración...")
        fetcher.create_sample_match_for_testing()
        print("✓ Partido de ejemplo creado")

    print("\nStep 2: Cargando modelo y haciendo predicciones...")
    print("-" * 60)

    predictor = Predictor()

    model_info = predictor.load_active_model()

    if not model_info:
        print("✗ No hay modelo activo. Por favor entrena un modelo primero.")
        return

    print(f"✓ Modelo cargado: {model_info['model_data']['model_type']}")
    print(f"  ID: {model_info['id']}")
    print(f"  Precisión: {model_info['model_data']['validation_accuracy']:.4f}")

    predictions = predictor.predict_all_today()

    print(f"\n✓ Predicciones completadas: {len(predictions)}")

    if predictions:
        print("\n📊 PREDICCIONES:")
        print("-" * 60)
        for i, pred in enumerate(predictions, 1):
            print(f"\n{i}. {pred['tournament']}")
            print(f"   {pred['match']}")
            print(f"   → Ganador Predicho: {pred['predicted_winner']}")
            print(f"   → Confianza: {pred['confidence']:.2%}")

    print("\nStep 3: Generando reporte HTML...")
    print("-" * 60)

    report_gen = HTMLReportGenerator()
    report_path = report_gen.generate_daily_report(today)

    print(f"✓ Reporte generado exitosamente")
    print(f"  📄 Ubicación: {report_path}")
    print(f"  🌐 Abre el archivo en tu navegador para ver el reporte")

    print("\n" + "="*60)
    print("   ✅ PIPELINE COMPLETADO EXITOSAMENTE")
    print("="*60 + "\n")

    print(f"📈 Resumen:")
    print(f"  • Predicciones realizadas: {len(predictions)}")
    print(f"  • Reporte generado: {report_path.name}")
    print(f"  • Ubicación: {report_path}")
    print()

if __name__ == "__main__":
    main()
