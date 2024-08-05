# SHELL=/bin/bash # Interpreter

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

##@ Clean-up

clean-unit-tests-cov:
	@del /q .coverage
	@rmdir /s /q htmlcov

clean-cov: ## remove output files from pytest & coverage
	@del /q .coverage
	@rmdir /s /q htmlcov
	@del /q pytest.xml
	@del /q pytest-coverage.txt
	# @rm -r dist

##@ Formatting

.PHONY: format-black
format-black: ## black (code formatter)
	@black .

.PHONY: format-isort
format-isort: ## isort (import formatter)
	@isort .

.PHONY: format
format: format-isort format-black ## run all formatters

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