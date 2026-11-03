.DEFAULT_GOAL := help

.PHONY: help build serve stop clean

help:
	@printf '%s\n' \
	  'make serve  Start the local site at http://localhost:4000' \
	  'make build  Build the static site into _site/' \
	  'make stop   Stop the local site' \
	  'make clean  Remove the generated site'

serve:
	docker compose up --build

build:
	docker compose run --rm site bundle exec jekyll build

stop:
	docker compose down

clean:
	docker compose run --rm site bundle exec jekyll clean
