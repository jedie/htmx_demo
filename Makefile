SHELL := /bin/bash

all: help

help:
	@echo -e '_________________________________________________________________'
	@echo -e 'DjangoForRunners - *dev* Makefile\n'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9 -]+:.*?## / {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install-poetry:  ## install or update poetry
	pip3 install -U pip
	pip3 install -U poetry

install:  ## install project via poetry
	poetry install

update:  ## update the sources and installation
	git fetch --all
	git pull origin main
	poetry run pip install -U pip
	poetry update

manage-update:  ## Collectstatic + makemigration + migrate
	./manage.sh collectstatic --noinput
	./manage.sh makemigrations
	./manage.sh migrate

run-dev-server:  ## Run the django dev server in endless loop.
	./manage.sh collectstatic --noinput --link
	./manage.sh makemigrations
	./manage.sh migrate
	./manage.sh runserver

createsuperuser:  ## Create super user
	./manage.sh createsuperuser

.PHONY: help install-poetry install update manage-update run-dev-server createsuperuser