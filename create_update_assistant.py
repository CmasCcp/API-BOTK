from openai import OpenAI
import os
from dotenv import load_dotenv, set_key
from assistant_instructions import instructions

load_dotenv()
OPENAI_API_KEY = os.environ['OPEN_AI_API_KEY']

client = OpenAI(api_key=OPENAI_API_KEY)

def create_vector_store_with_files(communities_dict):
    """
    Crea un vector store con documentos de múltiples comunidades
    communities_dict: {"macaya": "documentos_macaya", "otra": "documentos_otra"}
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Crear vector store con nombre que refleje múltiples comunidades
    community_names = "_".join(communities_dict.keys())
    vector_store_response = client.beta.vector_stores.create(
        name=f"Bot_MultiComunidades_{community_names}"
    )
    vector_store_id = vector_store_response.id
    print(f"📁 Vector store creado: {vector_store_id}")

    # Procesar documentos de todas las comunidades
    total_files = 0
    for community_name, folder in communities_dict.items():
        full_path = os.path.join(current_dir, folder)
        print(f"📂 Procesando comunidad: {community_name} desde {folder}")
        
        if not os.path.exists(full_path):
            print(f"⚠️ Carpeta no encontrada: {full_path}")
            continue
            
        for filename in os.listdir(full_path):
            
            if filename.endswith((".docx", ".pdf")):
                filepath = os.path.join(full_path, filename)
                print(f"📄 Subiendo: {community_name}/{filename}")
                with open(filepath, "rb") as file:
                    file_response = client.files.create(file=file, purpose="assistants")
                    client.beta.vector_stores.files.create(
                        vector_store_id=vector_store_id,
                        file_id=file_response.id
                    )
                    total_files += 1
    
    print(f"✅ Vector store creado con {total_files} documentos de {len(communities_dict)} comunidades")
    return vector_store_id

def create_or_update_assistant(communities=None):
    """
    Crea o actualiza un asistente con un vector store que contiene documentos de múltiples comunidades
    communities: dict como {"macaya": "documentos_macaya", "otra": "documentos_otra"}
    """
    if communities is None:
        communities = {"macaya": "documentos_macaya"}
    
    assistant_name = "BaseAssistant_MultiComunidades"
    assistant_id = os.getenv("ASSISTANT_ID", None)
    vector_store_id = None
    assistant_valid = False

    if assistant_id:
        try:
            client.beta.assistants.retrieve(assistant_id=assistant_id)
            assistant_valid = True
            print(f"✅ Assistant válido detectado: {assistant_id}")
            
            # Obtener vector store ID existente del .env
            vector_store_id = os.getenv("VECTOR_STORE_ID", "")
            if vector_store_id:
                print(f"✅ Vector store existente: {vector_store_id}")
            else:
                # Si no hay ID guardado, crear el vector store
                print("⚠️ No se encontró vector store ID. Recreando...")
                assistant_valid = False
        except Exception:
            print("⚠️ Assistant ID no válido. Se recreará.")

    if not assistant_valid:
        print("🔁 Creando assistant y vector store...")

        # Crear UN vector store con documentos de todas las comunidades
        vector_store_id = create_vector_store_with_files(communities)

        tools = [
            {"type": "file_search"},
            {
                "type": "function",
                "function": {
                    "name": "modify_document",
                    "description": "Modifica una sección específica de un documento LaTeX",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "Section": {"type": "string"},
                            "Content": {"type": "string"}
                        },
                        "required": ["Section", "Content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_promedio",
                    "description": "Devuelve el promedio de temperatura, humedad y nivel para una estación.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "estacion": {"type": "string"}
                        },
                        "required": ["estacion"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_promedio_estacional",
                    "description": "Calcula promedios estacionales por estación.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "estacion": {"type": "string"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_clima",
                    "description": "Entrega clima actual y pronóstico para una localidad.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "diagnostico_hidrico_integrado",
                    "description": "Entrega un diagnóstico hídrico combinado usando sensores y pronóstico. No requiere parámetros.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            }

        ]

        new_assistant = client.beta.assistants.create(
            name=assistant_name,
            instructions=instructions,
            model="gpt-4o",
            tools=tools,
            tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}}
        )
        assistant_id = new_assistant.id
        print("✅ Assistant creado:", assistant_id)

        # Guardar el vector store ID único
        set_key(".env", "ASSISTANT_ID", assistant_id)
        set_key(".env", "VECTOR_STORE_ID", vector_store_id)

    return assistant_id, vector_store_id
