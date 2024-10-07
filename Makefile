build:
	docker-compose up --build -d

up:
	docker-compose up -d

ssh:
	docker exec -it app-server bash

server: 
	docker exec -t app-server python manage.py migrate

down:
	docker-compose down

flake8:
	flake8 --exclude .git,__pycache__,docs/source/conf.py,venv,migrations .

test:
	docker exec -t app-server python manage.py test
