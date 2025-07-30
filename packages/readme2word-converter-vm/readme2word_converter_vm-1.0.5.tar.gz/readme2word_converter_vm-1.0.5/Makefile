.PHONY: help build run dev stop clean logs test

# Default target
help:
	@echo "Available commands:"
	@echo ""
	@echo "Docker Commands:"
	@echo "  build     - Build the Docker image"
	@echo "  run       - Run the application in production mode"
	@echo "  dev       - Run the application in development mode with hot reload"
	@echo "  stop      - Stop all running containers"
	@echo "  clean     - Remove containers and images"
	@echo "  logs      - Show application logs"
	@echo "  shell     - Open shell in running container"
	@echo ""
	@echo "Kubernetes Commands:"
	@echo "  k8s-deploy   - Deploy to Kubernetes using Helm"
	@echo "  k8s-cleanup  - Remove Kubernetes deployment"
	@echo "  k8s-status   - Check Kubernetes deployment status"
	@echo "  k8s-logs     - View Kubernetes application logs"
	@echo "  k8s-shell    - Open shell in Kubernetes pod"
	@echo ""
	@echo "Helm Commands:"
	@echo "  helm-install   - Install Helm chart"
	@echo "  helm-upgrade   - Upgrade Helm release"
	@echo "  helm-uninstall - Uninstall Helm release"
	@echo ""
	@echo "Package Commands:"
	@echo "  package-build     - Build Python package"
	@echo "  package-clean     - Clean build artifacts"
	@echo "  package-validate  - Validate package structure"
	@echo "  package-check     - Check built package"
	@echo "  publish-test      - Publish to Test PyPI"
	@echo "  publish-prod      - Publish to PyPI"
	@echo "  install-local     - Install package locally"
	@echo ""
	@echo "Testing Commands:"
	@echo "  test         - Run all tests"
	@echo "  test-quick   - Run quick tests"
	@echo "  check-deps   - Check dependencies"
	@echo ""
	@echo "Development Commands:"
	@echo "  install    - Install dependencies locally"
	@echo "  setup-dev  - Setup development environment"

# Build the Docker image
build:
	docker-compose build

# Run in production mode
run:
	docker-compose up -d
	@echo "Application running at http://localhost:8501"

# Run in development mode
dev:
	docker-compose --profile dev up readme2word-dev
	@echo "Development server running at http://localhost:8502"

# Stop all containers
stop:
	docker-compose down

# Clean up containers and images
clean:
	docker-compose down --rmi all --volumes --remove-orphans
	docker system prune -f

# Show logs
logs:
	docker-compose logs -f

# Run tests
test:
	python tests/run_all_tests.py

# Run quick tests for development
test-quick:
	python tests/run_all_tests.py --quick

# Run specific test suites
test-mermaid:
	python tests/test_mermaid.py

test-converter:
	python tests/test_converter.py

test-ui:
	python tests/test_ui.py

test-integration:
	python tests/test_integration.py

# Check dependencies
check-deps:
	python tests/run_all_tests.py --check-deps

# Open shell in running container
shell:
	docker-compose exec readme2word /bin/bash

# Install dependencies locally
install:
	pip install -r requirements.txt

# Quick start (build and run)
start: build run

# Development setup
setup-dev:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	@echo "Virtual environment created. Activate with: source venv/bin/activate"

# Kubernetes deployment commands
k8s-deploy:
	cd infra && ./deploy-k8s.sh

k8s-cleanup:
	cd infra && ./deploy-k8s.sh cleanup

k8s-status:
	cd infra && ./deploy-k8s.sh status

k8s-logs:
	cd infra && ./deploy-k8s.sh logs

k8s-shell:
	cd infra && ./deploy-k8s.sh shell

# Helm commands
helm-install:
	helm install readme2word infra/helm/readme2word --namespace readme2word --create-namespace

helm-upgrade:
	helm upgrade readme2word infra/helm/readme2word --namespace readme2word

helm-uninstall:
	helm uninstall readme2word --namespace readme2word

# Package building and publishing commands
package-build:
	./scripts/build-package.sh

package-clean:
	./scripts/build-package.sh clean

package-test:
	./scripts/build-package.sh test

package-validate:
	./scripts/build-package.sh validate

package-check:
	./scripts/build-package.sh check

package-info:
	./scripts/build-package.sh info

# Publishing commands
publish-test:
	./scripts/publish-package.sh test

publish-prod:
	./scripts/publish-package.sh prod

publish-check:
	./scripts/publish-package.sh check

# Install package locally for testing
install-local:
	pip install -e .

install-local-dev:
	pip install -e .[dev] 