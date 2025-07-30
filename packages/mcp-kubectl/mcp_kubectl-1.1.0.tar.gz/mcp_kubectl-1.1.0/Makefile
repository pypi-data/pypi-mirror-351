.PHONY: help build test clean publish-test publish-prod

# Default target
help:
	@echo "Available targets:"
	@echo "  build        - Build the package"
	@echo "  test         - Run tests"
	@echo "  clean        - Clean build artifacts"
	@echo "  publish-test - Publish to Test PyPI"
	@echo "  publish-prod - Publish to Production PyPI"
	@echo ""
	@echo "Set your tokens in .env file (copy from .env.example)"

# Build the package
build:
	uv build

# Run tests
test:
	uv run pytest

# Clean build artifacts
clean:
	rm -rf dist/ build/ *.egg-info/

# Validate package
check: build
	uv run --with twine twine check dist/*

# Publish to Test PyPI
publish-test: clean check test
	@if [ ! -f .env ]; then echo "❌ .env file not found! Copy .env.example to .env"; exit 1; fi
	@. .env && \
	if [ -z "$$UV_PUBLISH_TOKEN_TEST" ]; then echo "❌ UV_PUBLISH_TOKEN_TEST not set in .env"; exit 1; fi && \
	UV_PUBLISH_TOKEN=$$UV_PUBLISH_TOKEN_TEST uv publish --publish-url https://test.pypi.org/legacy/
	@echo "✅ Published to Test PyPI: https://test.pypi.org/project/mcp-kubectl/"

# Publish to Production PyPI  
publish-prod: clean check test
	@if [ ! -f .env ]; then echo "❌ .env file not found! Copy .env.example to .env"; exit 1; fi
	@. .env && \
	if [ -z "$$UV_PUBLISH_TOKEN_PROD" ]; then echo "❌ UV_PUBLISH_TOKEN_PROD not set in .env"; exit 1; fi && \
	echo "⚠️  Publishing to PRODUCTION PyPI!" && \
	read -p "Are you sure? (y/N): " confirm && \
	if [ "$$confirm" != "y" ] && [ "$$confirm" != "Y" ]; then echo "❌ Cancelled"; exit 1; fi && \
	UV_PUBLISH_TOKEN=$$UV_PUBLISH_TOKEN_PROD uv publish
	@echo "✅ Published to PyPI: https://pypi.org/project/mcp-kubectl/"