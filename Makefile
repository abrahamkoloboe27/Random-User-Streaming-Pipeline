build : 
	docker compose build
up: 
	docker compose up -d
build-up: build up
down: 
	docker compose down