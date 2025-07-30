# Makefile infra

COMPOSE = docker-compose
COMPOSE_FILE = infra/docker-compose.yml

up:
	$(COMPOSE) -f $(COMPOSE_FILE) up -d

down:
	$(COMPOSE) -f $(COMPOSE_FILE) down

restart:
	$(COMPOSE) -f $(COMPOSE_FILE) restart

build:
	$(COMPOSE) -f $(COMPOSE_FILE) build

ps:
	$(COMPOSE) -f $(COMPOSE_FILE) ps

logs:
	$(COMPOSE) -f $(COMPOSE_FILE) logs -f

shell-%:
	$(COMPOSE) -f $(COMPOSE_FILE) exec $* sh

bash-%:
	$(COMPOSE) -f $(COMPOSE_FILE) exec $* bash

clean:
	$(COMPOSE) -f $(COMPOSE_FILE) down -v

rebuild:
	$(COMPOSE) -f $(COMPOSE_FILE) down -v && $(COMPOSE) -f $(COMPOSE_FILE) up --build -d

# entrypoints
dev: up
	./scripts/run_sim.sh

test:
	pytest -q

.PHONY: up down restart build ps logs shell-% bash-% clean rebuild dev test
