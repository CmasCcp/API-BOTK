import requests
import sqlite3
import os
from datetime import datetime

DB_PATH = "data.db"
DATA_URL = "https://southamerica-west1-kuskalla.cloudfunctions.net/listarDatos"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mediciones (
            idDato INTEGER PRIMARY KEY,
            estacion TEXT,
            location TEXT,  -- interpretado como tipo_sensor
            dispositivo TEXT,
            timestamp INTEGER,
            bateria REAL,
            humedad REAL,
            nivel REAL,
            temperatura REAL
        );
    """)
    conn.commit()
    conn.close()

def fetch_and_store_data():
    print("🔽 Descargando datos...")
    resp = requests.get(DATA_URL)
    resp.raise_for_status()
    data = resp.json().get("data", [])

    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for d in data:
        cursor.execute("""
            INSERT OR IGNORE INTO mediciones
            (idDato, estacion, location, dispositivo, timestamp,
             bateria, humedad, nivel, temperatura)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            d.get("idDato"),
            d.get("estacion"),
            d.get("location"),
            d.get("dispositivo"),
            d.get("timestamp"),
            float(d.get("bateria") or 0.0),
            float(d.get("humedad") or 0.0),
            float(d.get("nivel") or 0.0),
            float(d.get("temperatura") or 0.0)
        ))
    conn.commit()
    conn.close()
    print(f"✅ Insertados {len(data)} registros en la base de datos.")

def obtener_promedio_por_estacion(estacion):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT AVG(temperatura), AVG(humedad), AVG(nivel)
        FROM mediciones
        WHERE estacion = ?
    """, (estacion,))
    result = cursor.fetchone()
    conn.close()
    return result

def explorar_datos(limit=10):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Obtener nombres de columnas
    cursor.execute("PRAGMA table_info(mediciones)")
    columnas = [col[1] for col in cursor.fetchall()]

    # Obtener primeros N registros
    cursor.execute(f"SELECT * FROM mediciones LIMIT {limit}")
    filas = cursor.fetchall()

    # Conteo de estaciones y tipo_sensor (antes 'location')
    cursor.execute("SELECT estacion, COUNT(*) FROM mediciones GROUP BY estacion")
    estaciones = cursor.fetchall()

    cursor.execute("SELECT location AS tipo_sensor, COUNT(*) FROM mediciones GROUP BY location")
    tipos_sensor = cursor.fetchall()

    conn.close()
    return {
        "columnas": columnas,
        "muestra": filas,
        "conteo_estaciones": estaciones,
        "conteo_tipo_sensor": tipos_sensor
    }


def get_promedio_estacional(estacion_nombre=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = "SELECT timestamp, temperatura, humedad, nivel FROM mediciones"
    params = []

    if estacion_nombre:
        query += " WHERE estacion = ?"
        params.append(estacion_nombre)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    # Agrupar por estación del año
    estaciones = {
        "Verano": [],
        "Otoño": [],
        "Invierno": [],
        "Primavera": []
    }

    for ts, temp, hum, niv in rows:
        mes = datetime.utcfromtimestamp(ts).month
        if mes in [12, 1, 2]:
            estaciones["Verano"].append((temp, hum, niv))
        elif mes in [3, 4, 5]:
            estaciones["Otoño"].append((temp, hum, niv))
        elif mes in [6, 7, 8]:
            estaciones["Invierno"].append((temp, hum, niv))
        elif mes in [9, 10, 11]:
            estaciones["Primavera"].append((temp, hum, niv))

    # Calcular promedios por estación
    resumen = {}
    for est, valores in estaciones.items():
        if valores:
            temps, hums, nivs = zip(*valores)
            resumen[est] = {
                "temperatura": round(sum(temps) / len(temps), 2),
                "humedad": round(sum(hums) / len(hums), 2),
                "nivel": round(sum(nivs) / len(nivs), 2),
                "n": len(valores)
            }

    return resumen