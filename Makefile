DOCKER_COMPOSE=docker-compose
DOCKER_IMAGE=sa_project_app

# Default target
.PHONY: help
help:  ## Display this help
	@echo "Usage: make [target] ..."
	@echo
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / { printf "  %-15s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

.PHONY: build

build:  ## Build the Docker image
	$(DOCKER_COMPOSE) build

.PHONY: up
up:  ## Start the Docker Compose services
	$(DOCKER_COMPOSE) up -d

.PHONY: down
down:  ## Stop the Docker Compose services
	$(DOCKER_COMPOSE) down

.PHONY: logs
logs:  ## Tail the logs of the Docker Compose services
	$(DOCKER_COMPOSE) logs -f

.PHONY: shell
shell:  ## Get a shell inside the app container
	$(DOCKER_COMPOSE) exec app /bin/bash

.PHONY: migrate
migrate:  ## Run Django database migrations
	$(DOCKER_COMPOSE) exec app python manage.py migrate

.PHONY: makemigrations
makemigrations:  ## Create new Django migrations
	$(DOCKER_COMPOSE) exec app python manage.py makemigrations

.PHONY: createsuperuser
createsuperuser:  ## Create a Django superuser
	$(DOCKER_COMPOSE) exec app python manage.py createsuperuser


.PHONE: load_fixtures
fixtures:  ## Load fixtures
	$(DOCKER_COMPOSE) exec app python manage.py loaddata tasks
	$(DOCKER_COMPOSE) exec app python manage.py loaddata details



.PHONY: collectstatic
collectstatic:  ## Collect static files
	$(DOCKER_COMPOSE) exec app python manage.py collectstatic --noinput

.PHONY: test
test:  ## Run Django tests
	$(DOCKER_COMPOSE) exec app python manage.py test

.PHONY: clean
clean:  ## Clean up unused Docker resources
	docker system prune -f
