import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.environ['OPEN_AI_API_KEY'])

# ------------------------------------------------------
# 1. Eliminar TODOS los vector stores
# ------------------------------------------------------
print("📦 Eliminando TODOS los Vector Stores...")

deleted_count = 0
while True:
    stores = client.vector_stores.list().data
    if not stores:
        break
    print(f"🔁 Detectados {len(stores)} vector store(s)")
    for vs in stores:
        print(f"🗑️ Eliminando Vector Store: {vs.id} ({vs.name})")
        client.vector_stores.delete(vector_store_id=vs.id)
        deleted_count += 1

print(f"✅ Eliminados {deleted_count} vector store(s)")

# ------------------------------------------------------
# 2. Eliminar TODOS los archivos del tipo 'assistants'
# ------------------------------------------------------
print("\n📁 Eliminando TODOS los archivos tipo 'assistants'...")

deleted_files = 0
while True:
    files = client.files.list().data
    assistant_files = [f for f in files if f.purpose == "assistants"]
    if not assistant_files:
        break
    print(f"🔁 Detectados {len(assistant_files)} archivo(s)")
    for f in assistant_files:
        print(f"🗑️ Eliminando Archivo: {f.id} ({f.filename})")
        client.files.delete(file_id=f.id)
        deleted_files += 1

print(f"✅ Eliminados {deleted_files} archivo(s)")


# ------------------------------------------------------
# 3. Eliminar TODOS los assistants
# ------------------------------------------------------
print("\n🤖 Eliminando TODOS los assistants...")

deleted_assistants = 0
while True:
    assistants = client.beta.assistants.list().data
    if not assistants:
        break
    print(f"🔁 Detectados {len(assistants)} assistant(s)")
    for assistant in assistants:
        print(f"🗑️ Eliminando Assistant: {assistant.id} ({assistant.name})")
        client.beta.assistants.delete(assistant_id=assistant.id)
        deleted_assistants += 1

print(f"✅ Eliminados {deleted_assistants} assistant(s)")


# ------------------------------------------------------
# 4. Verificación de limpieza
# ------------------------------------------------------
print("\n🔍 Verificando almacenamiento restante...")

# 1. Vector Stores
remaining_vs = client.vector_stores.list().data
if remaining_vs:
    print(f"❗ Vector Stores restantes: {len(remaining_vs)}")
    for vs in remaining_vs:
        print(f"  - ID: {vs.id}, Nombre: {vs.name}")
else:
    print("✅ No quedan vector stores.")

# 2. Archivos
remaining_files = client.files.list().data
if remaining_files:
    print(f"❗ Archivos restantes: {len(remaining_files)}")
    for f in remaining_files:
        print(f"  - ID: {f.id}, Nombre: {f.filename}, Purpose: {f.purpose}")
else:
    print("✅ No quedan archivos.")

# 3. (Opcional) Uso de almacenamiento - solo si la API lo soporta
try:
    usage = client.usage.retrieve()
    print(f"📊 Uso reportado de almacenamiento: {usage.get('storage_used', 'N/D')} bytes")
except Exception as e:
    print(f"⚠️ No se pudo obtener uso de almacenamiento: {e}")


