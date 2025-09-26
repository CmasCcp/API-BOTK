from api_handlers import HANDLERS
from db_logic import fetch_and_store_data, explorar_datos
from api_handlers import HANDLERS
import os

print("Clave:", os.getenv("WEATHERAPI_KEY"))
# Asegurarse que la DB y la tabla existan
fetch_and_store_data()

# Ahora testear el handler
args = {"estacion": "Iquiuca"}
resultado = HANDLERS["get_promedio"](args)
print("Resultado:", resultado)


info = explorar_datos(limit=5)

print("🧱 Columnas:", info["columnas"])
print("📊 Estaciones:", info["conteo_estaciones"])
print("🧪 Tipos de sensor:", info["conteo_tipo_sensor"])
print("🔎 Muestra de datos:")
for fila in info["muestra"]:
    print(fila)



# Test: promedios por estación del año para todos los datos
args = {}  # sin filtro
res = HANDLERS["get_promedio_estacional"](args)
print("\n📊 Promedio estacional (todas las estaciones):")
print(res)

# Test: promedios por estación del año solo para 'Iquiuca'
args = {"estacion": "Iquiuca"}
res = HANDLERS["get_promedio_estacional"](args)
print("\n📍 Promedio estacional para Iquiuca:")
print(res)


print(HANDLERS["get_clima"]({}))
# Con ubicación específica:
print(HANDLERS["get_clima"]({"location": "Mamina"}))