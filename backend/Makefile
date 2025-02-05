.PHONY: test clean install-dev init clean-packages test-verbose

install-dev:
	pip install -r requirements-dev.txt

init:
	@if [ ! -d ".venv" ]; then \
		python3 -m venv .venv; \
	fi
	@. .venv/bin/activate && pip install -r requirements-dev.txt

test:
	python3 -m pytest test/ -vv $(if $(findstring verbose,$(MAKECMDGOALS)),-s,)

run:
	@. .venv/bin/activate && python3 src/server.py

test-verbose:
	python3 -m pytest test/ -vv -s

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

clean-packages:
	rm -rf python/package_sources/*
	
.DEFAULT_GOAL := test
