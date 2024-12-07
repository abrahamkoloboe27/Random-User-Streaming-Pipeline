build : 
	docker compose build
up: 
	docker compose up -d 
up-remove-orphans: 
	docker compose up -d --remove-orphans
build-up: build up
down: 
	docker compose down
down-v: 
	docker compose down -v