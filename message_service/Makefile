venv_name=myvenv
activate=. $(venv_name)/bin/activate && export PYTHONPATH="src:$$PYTHONPATH"
new_terminal=gnome-terminal -- bash -c
db_user=vanya
db_name=fast_db
working_dir=src
tasks_file=tasks
host=0.0.0.0
port=8000
loglevel=INFO
uvicorn-compose=docker-uvicorn.yaml
gunicorn-compose=docker-gunicorn.yaml

db:
	$(new_terminal) "psql -U $(db_user) -d $(db_name); exec bash"

redis: 
	$(new_terminal) "redis-server; exec bash"

celery: 
	$(activate) && celery -A ${working_dir}.services.${tasks_file} worker --loglevel=$(loglevel)

celery-beat: 
	$(activate) && celery -A ${working_dir}.services.${tasks_file}  beat --loglevel=$(loglevel)

run: 
	$(activate) && uvicorn ${working_dir}.main:app --host $(host) --port $(port)
up-uvi:
	docker compose -f $(uvicorn-compose) up
up-guni:
	docker compose -f $(gunicorn-compose) up


