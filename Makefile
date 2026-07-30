.PHONY: lint format-check typecheck check test

lint:
	docker compose exec backend ruff check .

format-check:
	docker compose exec backend ruff format --check .

typecheck:
	docker compose exec backend mypy app/

check: lint format-check typecheck

test:
	docker compose exec backend pytest
