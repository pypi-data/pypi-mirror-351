.PHONY: dev build test clean format lint type-check install-dev

# Development build
dev:
	maturin develop

# Release build
build:
	maturin build --release

# Install in development mode
install-dev:
	pip install -e ".[dev]"
	maturin develop

# Run tests
test:
	pytest tests/ -v

# Clean build artifacts
clean:
	rm -rf target/
	rm -rf dist/
	rm -rf python/quic_portal.egg-info/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

# Format code
format:
	black python/
	ruff check python/ --fix

# Lint code
lint:
	ruff check python/
	cargo clippy

# Type checking
type-check:
	mypy python/quic_portal/

# Run all checks
check: format lint type-check test

# Build wheels for distribution
wheels:
	maturin build --release --out dist/

# Publish to PyPI (requires MATURIN_PYPI_TOKEN)
publish:
	maturin publish

# Local development setup
setup: install-dev
	@echo "Development environment ready!"
	@echo "Run 'make dev' to build the extension"
	@echo "Run 'make test' to run tests" 