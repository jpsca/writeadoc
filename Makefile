.PHONY: install
install:
	uv sync --group dev --group test
	uv pip install -e .

.PHONY: test
test:
	uv run pytest -x src/writeadoc tests

.PHONY: lint
lint:
	uv run ruff check .
	uv run ty check

# .PHONY: coverage
# coverage:
# 	uv run pytest --cov-config=pyproject.toml --cov-report html --cov writeadoc src/writeadoc tests

.PHONY: docs
docs:
	cd docs && uv run python docs.py

.PHONY: blueprint
blueprint:
	cd src/writeadoc/blueprint && uv run python docs.py

.PHONY: docs-build
docs-build:
	rm -rf docs/build
	cd docs && uv run python docs.py build

.PHONY: docs-publish
docs-publish:
	rm -rf docs/build
	cd docs && \
	uv run python docs.py build && \
	rsync --recursive --delete --progress build code:/var/www/writeadoc/
