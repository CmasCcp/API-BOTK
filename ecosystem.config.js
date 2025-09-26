module.exports = {
  apps: [{
    name: 'api-botk',
    script: 'venv_api_botk/bin/gunicorn',
    args: '--bind 0.0.0.0:8096 --workers 4 --timeout 120 main:app',
    cwd: '/var/www/api-botk',
    interpreter: 'none',
    env: {
      'VIRTUAL_ENV': '/var/www/api-botk/venv_api_botk',
      'PATH': '/var/www/api-botk/venv_api_botk/bin:' + process.env.PATH,
      'PYTHONPATH': '/var/www/api-botk'
    },
    instances: 1,
    exec_mode: 'fork',
    watch: false,
    max_memory_restart: '1G',
    error_file: './logs/api-botk-error.log',
    out_file: './logs/api-botk-out.log',
    log_file: './logs/api-botk-combined.log',
    time: true,
    autorestart: true,
    max_restarts: 10,
    min_uptime: '10s'
  }]
};
