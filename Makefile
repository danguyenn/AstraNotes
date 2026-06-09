# AstraNotes developer task runner.
# On Windows, install `make` (e.g. `choco install make`) or run the underlying
# commands directly — each target is a thin wrapper around a real command.
.PHONY: install test cov lint format typecheck check run seed diagrams docker-build docker-run

install:
	python -m pip install --upgrade pip
	pip install -e ".[dev,prod]"

test:
	pytest

cov:
	pytest --cov=astranotes --cov-report=term-missing

lint:
	ruff check src tests

format:
	ruff format src tests

typecheck:
	mypy src

# Everything CI runs, in CI order.
check: lint typecheck test
	ruff format --check src tests

run:
	astranotes

seed:
	python demo/seed_data.py --reset

# Re-render every Mermaid diagram in the docs to PNG/SVG (needs Node + npx).
diagrams:
	python tools/render_diagrams.py

docker-build:
	docker build -t astranotes:latest .

docker-run:
	docker run --rm -p 5000:5000 -v astranotes_data:/data \
	  -e ASTRANOTES_ENCRYPTION_KEY \
	  -e ASTRANOTES_SECRET_KEY \
	  astranotes:latest
