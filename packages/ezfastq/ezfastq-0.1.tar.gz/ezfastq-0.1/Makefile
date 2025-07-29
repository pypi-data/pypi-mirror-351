SHELL = bash

## #===== development tasks =====#

## help:        print this help message and exit
help: Makefile
	@sed -n 's/^## //p' Makefile

## test:        run automated test suite
test:
	pytest --cov=ezfastq ezfastq

## style:       check code style vs Black
style:
	black --line-length=99 --check $(shell find ezfastq/ -type f -name "*.py")

## format:      autoformat Python code
format:
	black --line-length=99 $(shell find ezfastq/ -type f -name "*.py")

## hooks:       deploy git pre-commit hooks for development
hooks:
	echo "#!/usr/bin/env bash" > .git/hooks/pre-commit
	echo "set -eo pipefail" >> .git/hooks/pre-commit
	echo "make style" >> .git/hooks/pre-commit
	chmod 755 .git/hooks/pre-commit
