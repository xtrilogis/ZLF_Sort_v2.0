# SHELL=/bin/bash # Interpreter

.DEFAULT_GOAL := help
.PHONY: help
help:  ## display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Tests
# todo fix python path
.PHONY: unit-tests
unit-tests: ## run unit-tests with pytest
	python -m pytest --ignore=tests/integration-tests

.PHONY: unit-tests-cov
unit-tests-cov: ## run unit-tests with pytest and show coverage (terminal + html)
	@python -m pytest --cov=. --cov-report term-missing --cov-report=html --ignore=tests/integration-tests

.PHONY: unit-integr-tests-cov
unit-integr-tests-cov: ## run unit-tests with pytest and show coverage (terminal + html)
	@python -m pytest --cov=. --cov-report term-missing --cov-report=html

.PHONY: unit-tests-cov-fail
unit-tests-cov-fail: ## run unit tests with pytest and show coverage (terminal + html) & fail if coverage too low & create files for CI
	@python -m pytest --cov=. --cov-report term-missing --cov-report=html --cov-fail-under=80 --junitxml=pytest.xml --ignore=tests/integration-tests

check-cov:
	@python3 -m coverage report --fail-under 70
	@count=$$(grep -o 'FAILED' pytest-coverage.txt | wc -l) && [ $$count -gt 0 ] && echo -e "\nFailed tests found: $$count \n" && exit 1 || true
