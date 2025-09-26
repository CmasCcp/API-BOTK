import os
from flask import request
from db_logic import fetch_and_store_data, obtener_promedio_por_estacion, get_promedio_estacional
from weather_api import get_current_weather, get_forecast

DB_PATH = "data.db"

# Validación común
def validate_required(args, required_fields):
    missing = [f for f in required_fields if f not in args]
    if missing:
        return {"error": f"Faltan parámetros requeridos: {', '.join(missing)}"}
    return None

# Handler: inicializa y descarga datos si no existe la base
def handler_init_db(_=None):
    if not os.path.exists(DB_PATH):
        fetch_and_store_data()
        return {"status": "ok", "message": "Base de datos creada y poblada."}
    return {"status": "ok", "message": "Base de datos ya existe."}

# Handler: devuelve promedio por estación
def handler_get_promedio(args):
    error = validate_required(args, ["estacion"])
    if error: return error

    estacion = args["estacion"]
    promedio = obtener_promedio_por_estacion(estacion)

    if not promedio or all(v is None for v in promedio):
        return {"error": f"No hay datos para la estación '{estacion}'"}

    return {
        "estacion": estacion,
        "promedio": {
            "temperatura": round(promedio[0], 2),
            "humedad": round(promedio[1], 2),
            "nivel": round(promedio[2], 2)
        }
    }

# Handler: promedios estacionales
def handler_get_promedio_estacional(args):
    estacion = args.get("estacion")  # opcional

    try:
        resumen = get_promedio_estacional(estacion)
        if not resumen:
            return {"message": "No hay datos suficientes para calcular promedios estacionales."}

        return {
            "estacion": estacion or "todas",
            "promedio_estacional": resumen
        }

    except Exception as e:
        return {"error": f"Ocurrió un error al calcular promedios estacionales: {str(e)}"}

# Handler: clima
def handler_get_clima(args):
    loc = args.get("location", "Iquiuca")

    try:
        current = get_current_weather(loc)
        if "current" not in current:
            return {"error": f"WeatherAPI no devolvió datos válidos: {current.get('error', 'respuesta inesperada')}"}

        forecast = get_forecast(loc, days=3)
        return {
            "current": {
                "temp_c": current["current"]["temp_c"],
                "humidity": current["current"]["humidity"],
                "condition": current["current"]["condition"]["text"],
                "is_day": current["current"]["is_day"]
            },
            "forecast": [
                {
                    "date": day["date"],
                    "maxtemp_c": day["day"]["maxtemp_c"],
                    "mintemp_c": day["day"]["mintemp_c"],
                    "avgtemp_c": day["day"]["avgtemp_c"],
                    "daily_chance_of_rain": day["day"].get("daily_chance_of_rain")
                }
                for day in forecast.get("forecast", {}).get("forecastday", [])
            ]
        }
    except Exception as e:
        return {"error": f"No se pudo obtener clima: {str(e)}"}

# Handler: diagnóstico integrado (sensor + clima)
def handler_diagnostico_hidrico_integrado(_=None):
    estacion = "Iquiuca"  # valor fijo porque es la única estación

    promedio = obtener_promedio_por_estacion(estacion)
    if not promedio:
        return {"error": "No se encontraron datos para la estación."}

    nivel, humedad, temperatura = promedio[2], promedio[1], promedio[0]

    try:
        clima = get_forecast("Mamina", days=3)
        pronostico = clima.get("forecast", {}).get("forecastday", [])
    except Exception as e:
        return {"error": f"No se pudo obtener clima: {str(e)}"}

    dias_lluvia = [d for d in pronostico if d["day"].get("daily_chance_of_rain", 0) >= 50]
    resumen_clima = {
        "dias_con_lluvia": len(dias_lluvia),
        "detalle": [
            {
                "fecha": d["date"],
                "lluvia_prob": d["day"].get("daily_chance_of_rain", 0),
                "max_temp": d["day"]["maxtemp_c"]
            } for d in pronostico
        ]
    }

    analisis = []
    if nivel < 1.0:
        analisis.append("Nivel de agua bajo")
    if humedad < 30:
        analisis.append("Humedad baja en el entorno")
    if not dias_lluvia:
        analisis.append("No se esperan lluvias significativas esta semana")

    conclusion = "Condición crítica" if len(analisis) >= 2 else "Condición moderada"

    return {
        "sensor": {
            "nivel": round(nivel, 2),
            "humedad": round(humedad, 2),
            "temperatura": round(temperatura, 2)
        },
        "clima": resumen_clima,
        "diagnostico": {
            "analisis": analisis,
            "conclusion": conclusion
        },
        "contexto_documental": "Consulta al asistente para complementar con antecedentes técnicos."
    }

# Registro de todos los handlers
HANDLERS = {
    "init_db": handler_init_db,
    "get_promedio": handler_get_promedio,
    "get_promedio_estacional": handler_get_promedio_estacional,
    "get_clima": handler_get_clima,
    "diagnostico_hidrico_integrado": handler_diagnostico_hidrico_integrado,
}
