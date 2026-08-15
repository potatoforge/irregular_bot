COMPOSE_FILE_TEST = docker-compose.test.yml

run-tests-doc:
	docker compose -f $(COMPOSE_FILE_TEST) up --build -d
	docker compose -f $(COMPOSE_FILE_TEST) logs -f tg-bot-test
	docker compose -f $(COMPOSE_FILE_TEST) down -v
