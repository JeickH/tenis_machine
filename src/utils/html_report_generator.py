from datetime import datetime
from pathlib import Path
from config.database import get_db
from config.settings import BASE_DIR
from src.utils.logger import get_logger

logger = get_logger(__name__)

class HTMLReportGenerator:
    def __init__(self):
        self.db = get_db()
        self.reports_dir = BASE_DIR / "reports"
        self.reports_dir.mkdir(exist_ok=True)

    def generate_daily_report(self, report_date=None):
        if report_date is None:
            report_date = datetime.now().date()

        logger.info(f"Generating HTML report for {report_date}")

        predictions = self._get_predictions_for_date(report_date)
        model_info = self._get_active_model_info()
        error_metrics = self._get_recent_error_metrics()

        html_content = self._build_html(predictions, model_info, error_metrics, report_date)

        report_filename = f"predictions_{report_date.strftime('%Y%m%d')}.html"
        report_path = self.reports_dir / report_filename

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"Report saved to: {report_path}")
        return report_path

    def _get_predictions_for_date(self, report_date):
        query = """
            SELECT
                p.id as prediction_id,
                t.name as tournament,
                t.series as tournament_series,
                p1.name as player_1,
                p1.current_rank as player_1_rank,
                p1.country as player_1_country,
                p2.name as player_2,
                p2.current_rank as player_2_rank,
                p2.country as player_2_country,
                pw.name as predicted_winner,
                p.predicted_total_sets,
                p.predicted_total_games,
                p.winner_probability,
                p.confidence_score,
                p.prediction_timestamp,
                m.round_id,
                r.name as round_name,
                s.name as surface,
                ct.name as court_type,
                p.actual_winner_id,
                aw.name as actual_winner,
                ps1.sports_mood_score as player_1_mood,
                ps2.sports_mood_score as player_2_mood,
                sh1.win_rate as player_1_surface_wr,
                sh2.win_rate as player_2_surface_wr
            FROM predictions p
            JOIN players p1 ON p.player_1_id = p1.id
            JOIN players p2 ON p.player_2_id = p2.id
            JOIN players pw ON p.predicted_winner_id = pw.id
            LEFT JOIN players aw ON p.actual_winner_id = aw.id
            JOIN tournaments t ON p.tournament_id = t.id
            LEFT JOIN matches m ON p.match_id = m.id
            LEFT JOIN rounds r ON m.round_id = r.id
            LEFT JOIN surfaces s ON m.surface_id = s.id
            LEFT JOIN court_types ct ON m.court_type_id = ct.id
            LEFT JOIN player_stats ps1 ON p1.id = ps1.player_id
            LEFT JOIN player_stats ps2 ON p2.id = ps2.player_id
            LEFT JOIN surface_history sh1 ON p1.id = sh1.player_id AND m.surface_id = sh1.surface_id
            LEFT JOIN surface_history sh2 ON p2.id = sh2.player_id AND m.surface_id = sh2.surface_id
            WHERE p.match_date = %s
            ORDER BY t.series DESC, p.prediction_timestamp ASC
        """

        predictions = self.db.execute_query(query, (report_date,), fetch=True)
        return [dict(p) for p in predictions] if predictions else []

    def _get_active_model_info(self):
        query = """
            SELECT
                id,
                model_type,
                model_version,
                validation_accuracy,
                validation_metrics,
                training_date
            FROM models
            WHERE is_active = true
            LIMIT 1
        """

        result = self.db.execute_query(query, fetch=True)
        return dict(result[0]) if result else None

    def _get_recent_error_metrics(self):
        query = """
            SELECT
                period,
                total_predictions,
                correct_winners,
                accuracy,
                avg_sets_error,
                avg_games_error,
                accuracy_top_50
            FROM error_metrics
            WHERE model_id = (SELECT id FROM models WHERE is_active = true LIMIT 1)
            ORDER BY
                CASE period
                    WHEN 'last_day' THEN 1
                    WHEN 'last_week' THEN 2
                    WHEN 'last_15_days' THEN 3
                    WHEN 'last_month' THEN 4
                END
            LIMIT 4
        """

        result = self.db.execute_query(query, fetch=True)
        return [dict(r) for r in result] if result else []

    def _build_html(self, predictions, model_info, error_metrics, report_date):
        total_predictions = len(predictions)
        correct_predictions = sum(1 for p in predictions if p.get('actual_winner') == p.get('predicted_winner'))
        accuracy = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0

        html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tennis Machine - Predicciones del {report_date.strftime('%d/%m/%Y')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}

        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}

        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}

        .summary-card h3 {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            margin-bottom: 10px;
        }}

        .summary-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #2a5298;
        }}

        .model-info {{
            padding: 20px 30px;
            background: #e8f4f8;
            border-left: 5px solid #2a5298;
        }}

        .model-info h2 {{
            color: #2a5298;
            margin-bottom: 15px;
        }}

        .model-info p {{
            margin: 5px 0;
            color: #555;
        }}

        .predictions {{
            padding: 30px;
        }}

        .predictions h2 {{
            color: #2a5298;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #2a5298;
        }}

        .match-card {{
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}

        .match-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        }}

        .match-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }}

        .tournament-info {{
            flex: 1;
        }}

        .tournament-name {{
            font-size: 1.2em;
            font-weight: bold;
            color: #2a5298;
        }}

        .tournament-series {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-top: 5px;
        }}

        .match-details {{
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }}

        .players {{
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            gap: 20px;
            align-items: center;
            margin: 20px 0;
        }}

        .player {{
            text-align: center;
            padding: 15px;
            border-radius: 8px;
            background: #f8f9fa;
        }}

        .player.winner {{
            background: #d4edda;
            border: 2px solid #28a745;
        }}

        .player-name {{
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 5px;
            color: #333;
        }}

        .player-rank {{
            color: #666;
            font-size: 0.9em;
        }}

        .player-stats {{
            margin-top: 10px;
            font-size: 0.85em;
            color: #666;
        }}

        .vs {{
            font-size: 1.5em;
            font-weight: bold;
            color: #999;
        }}

        .prediction-info {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin-top: 15px;
            border-radius: 5px;
        }}

        .prediction-info strong {{
            color: #856404;
        }}

        .confidence {{
            display: inline-block;
            background: #28a745;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin-left: 10px;
        }}

        .confidence.high {{
            background: #28a745;
        }}

        .confidence.medium {{
            background: #ffc107;
        }}

        .confidence.low {{
            background: #dc3545;
        }}

        .no-predictions {{
            text-align: center;
            padding: 60px 30px;
            color: #999;
        }}

        .no-predictions svg {{
            width: 100px;
            height: 100px;
            margin-bottom: 20px;
            opacity: 0.5;
        }}

        .footer {{
            background: #2a5298;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}

        .metrics-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}

        .metrics-table th,
        .metrics-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}

        .metrics-table th {{
            background: #f8f9fa;
            font-weight: bold;
            color: #2a5298;
        }}

        .metrics-table tr:hover {{
            background: #f8f9fa;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎾 Tennis Machine</h1>
            <p class="subtitle">Predicciones del {report_date.strftime('%d de %B de %Y')}</p>
        </div>

        <div class="summary">
            <div class="summary-card">
                <h3>Total Predicciones</h3>
                <div class="value">{total_predictions}</div>
            </div>
            <div class="summary-card">
                <h3>Predicciones Correctas</h3>
                <div class="value">{correct_predictions}</div>
            </div>
            <div class="summary-card">
                <h3>Precisión del Día</h3>
                <div class="value">{accuracy:.1f}%</div>
            </div>
        </div>
"""

        if model_info:
            html += f"""
        <div class="model-info">
            <h2>Modelo Activo</h2>
            <p><strong>Tipo:</strong> {model_info['model_type']}</p>
            <p><strong>Versión:</strong> {model_info['model_version']}</p>
            <p><strong>Precisión de Validación:</strong> {float(model_info['validation_accuracy']) * 100:.2f}%</p>
            <p><strong>Fecha de Entrenamiento:</strong> {model_info['training_date'].strftime('%d/%m/%Y %H:%M')}</p>
        </div>
"""

        html += """
        <div class="predictions">
            <h2>Predicciones</h2>
"""

        if not predictions:
            html += """
            <div class="no-predictions">
                <svg fill="#999" viewBox="0 0 24 24">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/>
                </svg>
                <h3>No hay predicciones para este día</h3>
                <p>No se encontraron partidos ATP500+ programados</p>
            </div>
"""
        else:
            for pred in predictions:
                is_p1_winner = pred['predicted_winner'] == pred['player_1']
                confidence = float(pred['confidence_score']) * 100
                confidence_class = 'high' if confidence >= 80 else 'medium' if confidence >= 60 else 'low'

                actual_result = ""
                if pred.get('actual_winner'):
                    is_correct = pred['actual_winner'] == pred['predicted_winner']
                    result_icon = "✓" if is_correct else "✗"
                    result_color = "#28a745" if is_correct else "#dc3545"
                    actual_result = f"""
                    <div style="margin-top: 10px; padding: 10px; background: {'#d4edda' if is_correct else '#f8d7da'}; border-radius: 5px;">
                        <strong style="color: {result_color};">{result_icon} Resultado Real:</strong> Ganador: <strong>{pred['actual_winner']}</strong>
                    </div>
"""

                html += f"""
            <div class="match-card">
                <div class="match-header">
                    <div class="tournament-info">
                        <div class="tournament-name">{pred['tournament']}</div>
                        <span class="tournament-series">{pred.get('tournament_series', 'ATP')}</span>
                        <div class="match-details">
                            {pred.get('round_name', '')} | {pred.get('surface', '')} | {pred.get('court_type', '')}
                        </div>
                    </div>
                </div>

                <div class="players">
                    <div class="player {'winner' if is_p1_winner else ''}">
                        <div class="player-name">{pred['player_1']}</div>
                        <div class="player-rank">#{pred.get('player_1_rank', 'N/A')} {pred.get('player_1_country', '')}</div>
                        <div class="player-stats">
                            Mood: {float(pred.get('player_1_mood') or 0):.1f} |
                            Surface WR: {float(pred.get('player_1_surface_wr') or 0) * 100:.1f}%
                        </div>
                    </div>

                    <div class="vs">VS</div>

                    <div class="player {'winner' if not is_p1_winner else ''}">
                        <div class="player-name">{pred['player_2']}</div>
                        <div class="player-rank">#{pred.get('player_2_rank', 'N/A')} {pred.get('player_2_country', '')}</div>
                        <div class="player-stats">
                            Mood: {float(pred.get('player_2_mood') or 0):.1f} |
                            Surface WR: {float(pred.get('player_2_surface_wr') or 0) * 100:.1f}%
                        </div>
                    </div>
                </div>

                <div class="prediction-info">
                    <strong>Predicción:</strong> Ganador: <strong>{pred['predicted_winner']}</strong>
                    <span class="confidence {confidence_class}">{confidence:.1f}% confianza</span>
                    <br>
                    <strong>Sets predichos:</strong> {pred['predicted_total_sets']} |
                    <strong>Games predichos:</strong> {pred['predicted_total_games']}
                    {actual_result}
                </div>
            </div>
"""

        html += """
        </div>
"""

        if error_metrics:
            html += """
        <div style="padding: 30px; background: #f8f9fa;">
            <h2 style="color: #2a5298; margin-bottom: 20px;">Métricas Históricas del Modelo</h2>
            <table class="metrics-table">
                <thead>
                    <tr>
                        <th>Período</th>
                        <th>Total Pred.</th>
                        <th>Correctas</th>
                        <th>Precisión</th>
                        <th>Error Sets</th>
                        <th>Error Games</th>
                        <th>Precisión Top 50</th>
                    </tr>
                </thead>
                <tbody>
"""

            period_names = {
                'last_day': 'Último Día',
                'last_week': 'Última Semana',
                'last_15_days': 'Últimos 15 Días',
                'last_month': 'Último Mes'
            }

            for metric in error_metrics:
                html += f"""
                    <tr>
                        <td><strong>{period_names.get(metric['period'], metric['period'])}</strong></td>
                        <td>{metric.get('total_predictions', 0)}</td>
                        <td>{metric.get('correct_winners', 0)}</td>
                        <td><strong>{float(metric.get('accuracy', 0)) * 100:.2f}%</strong></td>
                        <td>{float(metric.get('avg_sets_error', 0)):.2f}</td>
                        <td>{float(metric.get('avg_games_error', 0)):.2f}</td>
                        <td>{float(metric.get('accuracy_top_50', 0)) * 100:.2f}%</td>
                    </tr>
"""

            html += """
                </tbody>
            </table>
        </div>
"""

        html += f"""
        <div class="footer">
            <p>🤖 Generado automáticamente por Tennis Machine</p>
            <p>Reporte generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M:%S')}</p>
            <p style="margin-top: 10px; opacity: 0.8;">
                Generated with Claude Code |
                <a href="https://github.com/JeickH/tenis_machine" style="color: white;">GitHub Repository</a>
            </p>
        </div>
    </div>
</body>
</html>
"""

        return html
