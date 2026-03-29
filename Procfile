release: python manage.py migrate
web: daphne bookflow_api.asgi:application --port $PORT --bind 0.0.0.0 -v2
worker: python manage.py runworker channels -v2
scheduler: python manage.py scheduler