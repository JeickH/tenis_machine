# 🎾 Cómo Usar las Predicciones Personalizadas

## ✅ Sí, puedes predecir cualquier partido!

Ahora puedes ingresar **cualquier jugador vs cualquier jugador** y el sistema te dirá quién ganará.

---

## 🚀 Formas de Usar

### 1. Modo Interactivo (Más Fácil)

Solo ejecuta el script sin argumentos y te pedirá los datos paso a paso:

```bash
cd /Users/equipo/Documents/predictor_deportivo/tenis_machine
source venv/bin/activate
python3 scripts/predict_custom_match.py
```

**Ejemplo de sesión interactiva:**
```
Ingresa los datos del partido:

Jugador 1 (ej: Nadal R.): Federer R.
Jugador 2 (ej: Federer R.): Djokovic N.

Superficie (opciones: Hard, Clay, Grass) [Default: Hard]: Clay
Tipo de cancha (opciones: Indoor, Outdoor) [Default: Outdoor]: Outdoor
Torneo [Default: Custom Match]: Roland Garros

Ranking de Federer R. [Default: auto]: 5
Ranking de Djokovic N. [Default: auto]: 1
```

### 2. Modo Rápido (Línea de Comandos)

Puedes pasar todo en una sola línea:

```bash
python3 scripts/predict_custom_match.py 'Jugador1' 'Jugador2' [superficie] [tipo_cancha] [torneo] [rank1] [rank2]
```

---

## 📋 Ejemplos Reales

### Ejemplo 1: Nadal vs Djokovic en Roland Garros (Arcilla)
```bash
python3 scripts/predict_custom_match.py "Nadal R." "Djokovic N." Clay Outdoor "Roland Garros" 2 1
```

**Resultado:**
```
🏆 Ganador Predicho: Djokovic N.
📊 Confianza: 56.88%
🏟️  Superficie: Clay
```

### Ejemplo 2: Federer vs Alcaraz en Wimbledon (Césped)
```bash
python3 scripts/predict_custom_match.py "Federer R." "Alcaraz C." Grass Outdoor "Wimbledon"
```

### Ejemplo 3: Sinner vs Medvedev en Indoor Hard
```bash
python3 scripts/predict_custom_match.py "Sinner J." "Medvedev D." Hard Indoor "ATP Finals" 1 4
```

### Ejemplo 4: Cualquier partido simple
```bash
python3 scripts/predict_custom_match.py "Tsitsipas S." "Rublev A."
```
_(Usa valores por defecto: Hard, Outdoor, rankings automáticos)_

---

## ⚙️ Parámetros

| Parámetro | Opciones | Default | Obligatorio |
|-----------|----------|---------|-------------|
| **Jugador 1** | Cualquier nombre | - | ✅ Sí |
| **Jugador 2** | Cualquier nombre | - | ✅ Sí |
| **Superficie** | Hard, Clay, Grass | Hard | No |
| **Tipo de cancha** | Indoor, Outdoor | Outdoor | No |
| **Torneo** | Cualquier nombre | Custom Match | No |
| **Ranking 1** | 1-500 | Auto (de BD) | No |
| **Ranking 2** | 1-500 | Auto (de BD) | No |

---

## 🎯 Qué Muestra el Sistema

Cuando haces una predicción, obtienes:

```
======================================================================
   RESULTADO DE LA PREDICCIÓN
======================================================================

🎾 Partido:
   Nadal R. (#2) vs Djokovic N. (#1)

🏆 Ganador Predicho: Djokovic N.
📊 Confianza: 56.88%
📈 Probabilidad de victoria: 56.88%

🏟️  Superficie: Clay
🏢 Tipo de cancha: Outdoor
🏆 Torneo: Roland Garros

📊 Estadísticas de los jugadores:
----------------------------------------------------------------------
Nadal R.                  | Djokovic N.
----------------------------------------------------------------------
Sports Mood:      -1.00      | Sports Mood:      13.00
Surface WR:       60.0%     | Surface WR:       90.0%

======================================================================
Modelo usado: XGBoost
Precisión del modelo: 85.36%
======================================================================
```

---

## 📊 Cómo Funcionan las Estadísticas

### Sports Mood (Estado Deportivo)
- Basado en los **últimos 10 partidos** del jugador
- Rango: -10 (muy malo) a +10 (excelente)
- Considera victorias fáciles vs difíciles

### Surface Win Rate (% de Victorias en Superficie)
- Porcentaje de victorias del jugador en esa superficie específica
- **Clay** (arcilla), **Hard** (dura), **Grass** (césped)
- Basado en todo el historial del jugador

### Confianza
- **> 80%**: Predicción muy segura
- **60-80%**: Predicción confiable
- **50-60%**: Partido muy parejo
- **< 50%**: El otro jugador tiene ventaja

---

## 🎮 Casos de Uso

### 1. Predecir partidos del día
```bash
# Alcaraz vs Musetti (hoy en ATP Finals)
python3 scripts/predict_custom_match.py "Alcaraz C." "Musetti L." Hard Indoor "ATP Finals"
```

### 2. Partidos hipotéticos
```bash
# ¿Qué pasaría si Nadal jugara contra Alcaraz en tierra?
python3 scripts/predict_custom_match.py "Nadal R." "Alcaraz C." Clay Outdoor "Roland Garros"
```

### 3. Analizar diferentes superficies
```bash
# Federer vs Nadal en Hard
python3 scripts/predict_custom_match.py "Federer R." "Nadal R." Hard

# Federer vs Nadal en Clay
python3 scripts/predict_custom_match.py "Federer R." "Nadal R." Clay

# Federer vs Nadal en Grass
python3 scripts/predict_custom_match.py "Federer R." "Nadal R." Grass
```

---

## ⚠️ Notas Importantes

1. **Nombres de Jugadores:**
   - Usa el formato: `"Apellido Inicial."`
   - Ejemplos: `"Nadal R."`, `"Djokovic N."`, `"Federer R."`
   - Si el jugador no existe en la BD, se crea automáticamente

2. **Rankings:**
   - Si no especificas ranking, se usa el último disponible en la BD
   - Si el jugador es nuevo, se asume ranking 100

3. **Estadísticas:**
   - Los jugadores nuevos no tendrán historial de Sports Mood o Surface Win Rate
   - El modelo puede hacer predicciones incluso sin historial

4. **Partido Temporal:**
   - El partido que creas es temporal (se elimina después de la predicción)
   - No afecta las estadísticas de los jugadores

---

## 🔧 Troubleshooting

### "Player not found"
- Verifica la ortografía del nombre
- Usa comillas si el nombre tiene espacios: `"De Minaur A."`

### Error de superficie
- Opciones válidas: `Hard`, `Clay`, `Grass` (case-sensitive)

### Error de tipo de cancha
- Opciones válidas: `Indoor`, `Outdoor` (case-sensitive)

---

## 📞 Comandos Rápidos de Referencia

```bash
# Activar entorno
cd /Users/equipo/Documents/predictor_deportivo/tenis_machine
source venv/bin/activate

# Modo interactivo
python3 scripts/predict_custom_match.py

# Partido simple (usa defaults)
python3 scripts/predict_custom_match.py "Nadal R." "Djokovic N."

# Partido completo con todos los parámetros
python3 scripts/predict_custom_match.py "Jugador1" "Jugador2" Hard Indoor "ATP Finals" 5 10

# Ver ayuda
python3 scripts/predict_custom_match.py --help
```

---

## ✅ ¡Listo para Usar!

Ahora puedes predecir cualquier partido que quieras. El sistema:
- ✅ Busca los jugadores en la BD (o los crea)
- ✅ Calcula estadísticas automáticamente
- ✅ Usa el modelo optimizado (85.36% precisión)
- ✅ Te da predicción + confianza + estadísticas

**¡Pruébalo ahora!** 🎾🚀
