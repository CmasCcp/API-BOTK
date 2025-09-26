from openai import OpenAI
import os
from dotenv import load_dotenv, set_key
from assistant_instructions import instructions

load_dotenv()
OPENAI_API_KEY = os.environ['OPEN_AI_API_KEY']

client = OpenAI(api_key=OPENAI_API_KEY)

def create_vector_store_with_files(folder="documentos_macaya"):
    #current_dir = os.path.dirname(os.path.abspath(__file__))
    #full_path = os.path.join(current_dir, folder)
    full_path="/var/www/api-botk/documentos_macaya" 

    vector_store_response = client.beta.vector_stores.create(name="Bot_Macaya_Files")
    vector_store_id = vector_store_response.id

    for filename in os.listdir(full_path):
        if filename.endswith(".docx"):
            filepath = os.path.join(full_path, filename)
            print(filepath)
            with open(filepath, "rb") as file:
                file_response = client.files.create(file=file, purpose="assistants")
                client.beta.vector_stores.files.create(
                    vector_store_id=vector_store_id,
                    file_id=file_response.id
                )
    return vector_store_id

def create_or_update_assistant(folder="documentos_macaya"):
    assistant_name = "BaseAssistant"
    assistant_id = os.getenv("ASSISTANT_ID", None)
    vector_store_id = os.getenv("VECTOR_STORE_ID", None)
    assistant_valid = False

    if assistant_id:
        try:
            client.beta.assistants.retrieve(assistant_id=assistant_id)
            assistant_valid = True
            print(f"✅ Assistant válido detectado: {assistant_id}")
        except Exception:
            print("⚠️ Assistant ID no válido. Se recreará.")

    if not assistant_valid:
        print("🔁 Creando assistant y vector store...")

        vector_store_id = create_vector_store_with_files(folder)

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

        set_key(".env", "ASSISTANT_ID", assistant_id)
        set_key(".env", "VECTOR_STORE_ID", vector_store_id)

    return assistant_id, vector_store_id
