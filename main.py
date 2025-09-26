from openai import OpenAI
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
import requests
import json
from flask_cors import CORS
from create_update_assistant import create_or_update_assistant
from api_handlers import HANDLERS

# --------------------------------------------------------------------------------
# 1) Configuración Inicial
# --------------------------------------------------------------------------------

load_dotenv('.env')
OPENAI_API_KEY = os.environ['OPEN_AI_API_KEY']
client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)
CORS(app)

# Crear o actualizar assistant (usa solo vector store + funciones)
ASSISTANT_ID, VECTOR_STORE_ID = create_or_update_assistant()


# --------------------------------------------------------------------------------
# 2) Endpoints activos
# --------------------------------------------------------------------------------

@app.route('/start', methods=['GET'])
def start_conversation():
    thread = client.beta.threads.create()
    return jsonify({
        "thread_id": thread.id,
        "assistant_id": ASSISTANT_ID,
        "vector_store_id": VECTOR_STORE_ID
    })

@app.route('/dummy', methods=['GET'])
def dummy():
    print("ola")
    return jsonify({
        "msj": "sorprise mdk"
    })


@app.route('/chat', methods=['POST'])
def chat():
    try:
        thread_id = request.form.get('thread_id')
        user_input = request.form.get('message', '')

        if not thread_id or not user_input:
            return jsonify({"error": "Missing thread_id or message"}), 400

        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input
        )

        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID,
        )

        if run.status == "requires_action" and run.required_action:
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []

            for call in tool_calls:
                name = call.function.name
                args = json.loads(call.function.arguments)
                args["thread_id"] = thread_id

                try:
                    if name in HANDLERS:
                        result = HANDLERS[name](args)
                    else:
                        result = {"error": f"Función '{name}' no está registrada."}
                except Exception as tool_error:
                    result = {"error": f"Error en '{name}': {str(tool_error)}"}

                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": json.dumps(result)
                })

            run = client.beta.threads.runs.submit_tool_outputs_and_poll(
                thread_id=thread_id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )

        if run.status == 'completed':
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            response_text = next(
                (m.content[0].text.value for m in messages.data if m.role == 'assistant' and m.content[0].type == 'text'),
                "[No assistant response found]"
            )
            return jsonify({"response": response_text})

        elif run.status == 'requires_action':
            return jsonify({
                "error": "El asistente aún requiere acción adicional.",
                "status": run.status,
                "required_action": run.required_action
            }), 202

        else:
            return jsonify({
                "error": "Run no se completó correctamente",
                "status": run.status
            }), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/threadHistory', methods=['GET'])
def get_thread_history():
    thread_id = request.args.get('thread_id')
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "assistants=v2",
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        data['data'] = data.get('data', [])[::-1]
        return jsonify(data)
    return jsonify({"error": "Failed to fetch history", "details": response.text}), response.status_code

@app.route('/listAssistants', methods=['GET'])
def list_available_assistants():
    try:
        assistants = client.beta.assistants.list().data
        return jsonify([a.id for a in assistants])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --------------------------------------------------------------------------------
# 3) Main
# --------------------------------------------------------------------------------

if __name__ == '__main__':
    print("[main] Starting Flask server...")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5001)))
