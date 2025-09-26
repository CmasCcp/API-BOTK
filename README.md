# API BOTK

Una API Flask que utiliza OpenAI Assistant para procesamiento de documentos y chat inteligente.

## 🚀 Configuración Rápida

### 1. Clonar el repositorio
```bash
git clone https://github.com/CmasCcp/API-BOTK.git
cd API-BOTK
```

### 2. Configurar el entorno
```bash
# Copiar el archivo de configuración
cp .env.example .env

# Editar .env con tus credenciales
nano .env
```

### 3. Configurar el entorno virtual
```bash
# Activar el entorno virtual
source venv_api_botk/bin/activate

# Instalar dependencias (si es necesario)
pip install -r requirements.txt
```

### 4. Ejecutar con PM2 (Producción)
```bash
# Iniciar con PM2
pm2 start ecosystem.config.js

# Ver estado
pm2 status

# Ver logs
pm2 logs api-botk
```

### 5. Ejecutar en desarrollo
```bash
python main.py
```

## 📋 Variables de Entorno

Configura las siguientes variables en tu archivo `.env`:

```env
# OpenAI API Configuration (REQUERIDO)
OPEN_AI_API_KEY=tu-clave-api-de-openai

# Assistant Configuration (Opcional - se auto-genera)
ASSISTANT_ID=tu-id-de-asistente
VECTOR_STORE_ID=tu-id-de-vector-store

# API Configuration (Opcional)
API_HASH=tu-hash-api
```

## 🛠 Endpoints

### `GET /start`
Inicia una nueva conversación
- **Respuesta**: `{"thread_id": "...", "assistant_id": "...", "vector_store_id": "..."}`

### `POST /chat`
Envía un mensaje al asistente
- **Parámetros**: 
  - `thread_id`: ID del hilo de conversación
  - `message`: Mensaje a enviar
- **Respuesta**: `{"response": "..."}`

### `GET /threadHistory`
Obtiene el historial de una conversación
- **Parámetros**: `thread_id`
- **Respuesta**: Historial completo del hilo

### `GET /listAssistants`
Lista todos los asistentes disponibles
- **Respuesta**: Array de IDs de asistentes

### `GET /dummy`
Endpoint de prueba
- **Respuesta**: `{"msj": "sorprise mdk"}`

## 🔧 Gestión con PM2

```bash
# Iniciar
pm2 start ecosystem.config.js

# Detener
pm2 stop api-botk

# Reiniciar
pm2 restart api-botk

# Eliminar
pm2 delete api-botk

# Ver logs en tiempo real
pm2 logs api-botk --lines 50

# Monitoreo
pm2 monit
```

## 📁 Estructura del Proyecto

```
├── main.py                 # Aplicación principal Flask
├── api_handlers.py         # Manejadores de funciones del asistente
├── create_update_assistant.py # Creación/actualización del asistente
├── assistant_instructions.py  # Instrucciones del asistente
├── db_logic.py            # Lógica de base de datos
├── weather_api.py         # API del clima
├── document_manipulation.py # Manipulación de documentos
├── ecosystem.config.js    # Configuración PM2
├── requirements.txt       # Dependencias Python
├── .env.example          # Plantilla de configuración
├── documentos_macaya/    # Documentos del proyecto
├── logs/                 # Archivos de log
└── venv_api_botk/       # Entorno virtual Python
```

## 🔐 Seguridad

- **NUNCA** commits el archivo `.env` al repositorio
- Usa variables de entorno para datos sensibles
- El archivo `.env` está incluido en `.gitignore`
- Usa `.env.example` como plantilla

## 🐛 Solución de Problemas

### Error: "Missing thread_id or message"
- Asegúrate de enviar tanto `thread_id` como `message` en las peticiones POST a `/chat`

### Error: "OPEN_AI_API_KEY no encontrada"
- Verifica que el archivo `.env` existe y contiene la clave API válida

### Error de permisos en PM2
- Ejecuta `pm2 kill` y luego `pm2 start ecosystem.config.js`

## 📊 Monitoreo

Los logs se almacenan en:
- `logs/api-botk-combined-{id}.log` - Logs combinados
- `logs/api-botk-error-{id}.log` - Solo errores
- `logs/api-botk-out-{id}.log` - Solo salida estándar

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.
