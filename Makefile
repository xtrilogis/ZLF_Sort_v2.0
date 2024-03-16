SHELL=/bin/bash # Interpreter

.DEFAULT_GOAL := help
.PHONY: help
help:  ## display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Tree
print-file-tree: ## display the tree with files
	tree /f

print-dir-tree: ## display only the directories
	tree

##@ Installer
exe: ## Run pyinstaller
	pyinstaller --name ZLF-sort --onefile --windowed --icon assests/Icon.ico

##@ Tests
# todo fix python path
.PHONY: unit-tests
unit-tests: ## run unit-tests with pytest
	@pytest

.PHONY: unit-tests-cov
unit-tests-cov: ## run unit-tests with pytest and show coverage (terminal + html)
	@pytest --cov=. --cov-report term-missing --cov-report=html

.PHONY: unit-tests-cov-fail
unit-tests-cov-fail: ## run unit tests with pytest and show coverage (terminal + html) & fail if coverage too low & create files for CI
	@pytest --cov=. --cov-report term-missing --cov-report=html --cov-fail-under=80 --junitxml=pytest.xml | tee pytest-coverage.txt

check-cov:
	@python3 -m coverage report --fail-under 70
	@count=$$(grep -o 'FAILED' pytest-coverage.txt | wc -l) && [ $$count -gt 0 ] && echo -e "\nFailed tests found: $$count \n" && exit 1 || true

##@ Clean-up

clean-cov: ## remove output files from pytest & coverage
	@rm -rf .coverage
	@rm -rf htmlcov
	@rm -rf pytest.xml
	@rm -rf pytest-coverage.txt
	@rm -rf dist

##@ Formatting

.PHONY: format-black
format-black: ## black (code formatter)
	@black .

.PHONY: format-isort
format-isort: ## isort (import formatter)
	@isort .

.PHONY: format
format: format-black format-isort ## run all formatters

##@ Linting

.PHONY: lint-black
lint-black: ## black in linting mode
	@black . --check

.PHONY: lint-isort
lint-isort: ## isort in linting mode
	@isort . --check

.PHONY: lint-flake8
lint-flake8: ## flake8 (linter)
	@flake8 .

lint: lint-black lint-isort lint-flake8 ## run all linters