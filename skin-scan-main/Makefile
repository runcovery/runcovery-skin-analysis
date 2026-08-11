.PHONY: setup dev test scan lint clean

setup:
	uv venv
	uv pip install -e ".[dev]"
	cp .env.example .env

dev:
	uv run uvicorn src.app.main:app --reload --port 8000

test:
	uv run pytest -q tests/

scan:
	@if [ -z "$(SCAN)" ]; then echo "Usage: make scan SCAN=path/to/image.jpg"; exit 1; fi
	uv run python -m src.cli.scan_image --input $(SCAN) --out scans/

lint:
	uv run ruff check src/ tests/
	uv run pyright src/

clean:
	rm -rf .venv __pycache__ .pytest_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
