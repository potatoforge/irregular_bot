COMPOSE_FILE_TEST = docker-compose.test.yml

run-tests-doc:
	docker compose -f $(COMPOSE_FILE_TEST) up --build -d
	docker compose -f $(COMPOSE_FILE_TEST) logs -f tg_bot_test
	docker compose -f $(COMPOSE_FILE_TEST) down -v

run-tests-ci:
	docker compose -f $(COMPOSE_FILE_TEST) up --build --abort-on-container-exit --exit-code-from tg_bot_test
	docker compose -f $(COMPOSE_FILE_TEST) down -v
