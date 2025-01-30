.PHONY: test clean install-dev init clean-packages test-verbose

install-dev:
	pip install -r requirements-dev.txt

init: install-dev

test:
	python3 -m pytest test/ -vv $(if $(findstring verbose,$(MAKECMDGOALS)),-s,)

test-verbose:
	python3 -m pytest test/ -vv -s

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

clean-packages:
	rm -rf python/package_sources/*
	
.DEFAULT_GOAL := test
