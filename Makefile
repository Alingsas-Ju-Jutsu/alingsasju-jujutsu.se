.DEFAULT_GOAL := help

.PHONY: help build serve stop clean scrape scrape-test import import-test

ARCHIVE ?= _old_site/2026-11-03T09-40-05-601Z

help:
	@printf '%s\n' \
	  'make serve  Start the local site at http://localhost:4000' \
	  'make build  Build the static site into _site/' \
	  'make stop   Stop the local site' \
	  'make clean  Remove the generated site' \
	  'make scrape Archive public pages into _old_site/' \
	  'make scrape-test Test the browser archiver locally' \
	  'make import Import the completed public archive into Jekyll' \
	  'make import-test Verify imported content against the archive (after make build)'

serve:
	docker compose up --build


build:
	docker compose run --build --rm site sh -c 'bundle exec jekyll build'

generate_poster:
	docker compose run --build --rm poster_generator sh -c 'python3 tools/build_poster.py'

stop:
	docker compose down

clean:
	docker compose run --rm site bundle exec jekyll clean

scrape:
	LOCAL_UID=$$(id -u) LOCAL_GID=$$(id -g) docker compose --profile archive run --build --rm scraper

scrape-test:
	LOCAL_UID=$$(id -u) LOCAL_GID=$$(id -g) docker compose --profile archive run --build --rm scraper npm test

import:
	docker compose run --rm site ruby tools/archive/import.rb "$(ARCHIVE)"

import-test:
	docker compose run --rm site ruby tools/archive/validate_import.rb "$(ARCHIVE)"
