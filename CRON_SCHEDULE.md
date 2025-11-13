# 📅 Tennis Machine - Schedule Diario de Predicciones

## ✅ Estado: ACTIVO

El sistema de predicciones diarias está configurado y ejecutándose automáticamente.

---

## 📊 Configuración Actual

### Cron Job Instalado:
```bash
0 8 * * * [ $(date +\%Y\%m\%d) -le 20251120 ] && /Users/equipo/Documents/predictor_deportivo/tenis_machine/scripts/daily_predictions_pipeline.sh >> /Users/equipo/Documents/predictor_deportivo/tenis_machine/logs/cron_execution.log 2>&1
```

### Detalles:
- **Hora de ejecución:** 8:00 AM (todos los días)
- **Duración:** Hasta el 20 de Noviembre de 2025
- **Script ejecutado:** `daily_predictions_pipeline.sh`
- **Logs:** `/Users/equipo/Documents/predictor_deportivo/tenis_machine/logs/cron_execution.log`

---

## 📋 Lo Que Hace Diariamente

El sistema ejecuta automáticamente:

1. **Busca partidos del día** (ATP Finals)
2. **Carga el modelo optimizado** (ID 4 - 85.36% precisión, 500 combinaciones)
3. **Genera predicciones** para cada partido
4. **Crea reporte HTML** con:
   - Predicciones de ganadores
   - Confianza por cada partido
   - Estadísticas de jugadores
   - Información del modelo
5. **Guarda el reporte** en: `reports/predictions_YYYYMMDD.html`

---

## 📁 Archivos Generados

### Reportes Diarios:
```
/Users/equipo/Documents/predictor_deportivo/tenis_machine/reports/
├── predictions_20251112.html  ✅ (12 Nov 2025)
├── predictions_20251113.html  ✅ (13 Nov 2025)
├── predictions_20251114.html  (14 Nov 2025)
├── predictions_20251115.html  (15 Nov 2025)
...
└── predictions_20251120.html  (20 Nov 2025)
```

### Logs de Ejecución:
```
/Users/equipo/Documents/predictor_deportivo/tenis_machine/logs/
├── cron_execution.log              (Log consolidado de cron)
├── daily_predictions_TIMESTAMP.log (Log individual por ejecución)
```

---

## 🔍 Monitoreo

### Ver cron jobs activos:
```bash
crontab -l
```

### Ver log de ejecución en tiempo real:
```bash
tail -f /Users/equipo/Documents/predictor_deportivo/tenis_machine/logs/cron_execution.log
```

### Ver últimas ejecuciones:
```bash
tail -50 /Users/equipo/Documents/predictor_deportivo/tenis_machine/logs/cron_execution.log
```

### Ver reportes generados:
```bash
ls -lht /Users/equipo/Documents/predictor_deportivo/tenis_machine/reports/
```

---

## 🛠️ Administración

### Ejecutar manualmente (sin esperar al cron):
```bash
/Users/equipo/Documents/predictor_deportivo/tenis_machine/scripts/daily_predictions_pipeline.sh
```

### Probar el script:
```bash
cd /Users/equipo/Documents/predictor_deportivo/tenis_machine
bash scripts/daily_predictions_pipeline.sh
```

### Ver reporte de hoy:
```bash
# Abre el HTML en el navegador
open /Users/equipo/Documents/predictor_deportivo/tenis_machine/reports/predictions_$(date +%Y%m%d).html
```

---

## ❌ Desinstalar Cron Job

### Opción 1: Editar manualmente
```bash
crontab -e
# Elimina la línea con "daily_predictions_pipeline.sh"
```

### Opción 2: Eliminar todos los cron jobs (¡CUIDADO!)
```bash
crontab -r
```

### Opción 3: Remover solo este cron job
```bash
crontab -l | grep -v "daily_predictions_pipeline.sh" | crontab -
```

---

## 🔄 Re-instalar Cron Job

Si necesitas reinstalar el cron job:

```bash
/Users/equipo/Documents/predictor_deportivo/tenis_machine/scripts/setup_daily_cron.sh
```

---

## ⚠️ Importante

1. **El script se auto-detiene después del 20 de Noviembre de 2025**
   - No necesitas desinstalarlo manualmente
   - Después del 20/11/2025, el cron job seguirá existiendo pero no se ejecutará

2. **Asegúrate de que la Mac esté encendida a las 8:00 AM**
   - Si la Mac está apagada o dormida, el cron no se ejecutará
   - Los reportes solo se generan si hay partidos ese día

3. **Logs automáticos**
   - Cada ejecución guarda un log detallado
   - Los logs se pueden revisar para debugging

---

## 📞 Comandos Útiles

### Ver reporte de hoy en navegador:
```bash
open ~/Documents/predictor_deportivo/tenis_machine/reports/predictions_$(date +%Y%m%d).html
```

### Ver todos los reportes:
```bash
ls -1 ~/Documents/predictor_deportivo/tenis_machine/reports/
```

### Verificar si el cron está activo:
```bash
crontab -l | grep "daily_predictions_pipeline"
```

### Ver próxima ejecución del cron:
```bash
# Los cron jobs se ejecutan según la hora del sistema
date  # Ver hora actual
```

---

## ✅ Verificación Post-Instalación

- [✓] Cron job instalado
- [✓] Script con permisos de ejecución
- [✓] Test manual ejecutado exitosamente
- [✓] Reporte HTML generado para hoy (13/11/2025)
- [✓] Logs funcionando correctamente

---

**Última actualización:** 13 de Noviembre de 2025
**Modelo activo:** ID 4 (XGBoost con 500 combinaciones, 85.36% precisión)
