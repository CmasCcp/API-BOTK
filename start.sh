#!/bin/bash

# Script para iniciar la aplicación con PM2
cd /var/www/api-botk

# Activar el entorno virtual y ejecutar con gunicorn
source venv_api_botk/bin/activate
exec gunicorn --bind 0.0.0.0:8096 --workers 4 --timeout 120 main:app
