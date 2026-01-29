.PHONY: dev prod run help

# Development mode - runs locally with DEV_MODE enabled
dev:
	@echo "Starting ATR-demo app in development mode..."
	@echo "  - Disabling @spaces.GPU decorator"
	@echo "  - Disabling Matomo analytics"
	@echo "  - Setting proxy path for Coder workspace"
	DEV_MODE=true \
	GRADIO_ROOT_PATH="/@Borg93/crimson-moth-98.main/apps/code-server/proxy/7860" \
	MAX_IMAGES=5 \
	uv run app/main.py

# Production mode - runs as if on Hugging Face Spaces
prod:
	@echo "Starting ATR-demo app in production mode..."
	@echo "  - Enabling @spaces.GPU decorator"
	@echo "  - Enabling Matomo analytics"
	uv run app/main.py

# Alias for dev
run: dev

# Show available commands
help:
	@echo "Available commands:"
	@echo "  make dev   - Run in development mode (local)"
	@echo "               • Disables @spaces.GPU decorator"
	@echo "               • Disables Matomo analytics tracking"
	@echo "               • Sets GRADIO_ROOT_PATH for proxy"
	@echo "               • Sets MAX_IMAGES=5"
	@echo ""
	@echo "  make prod  - Run in production mode (Hugging Face Spaces)"
	@echo "               • Enables @spaces.GPU decorator"
	@echo "               • Enables Matomo analytics tracking"
	@echo ""
	@echo "  make run   - Alias for 'make dev'"
	@echo "  make help  - Show this help message"
	@echo ""
	@echo "Environment variables for Matomo (production only):"
	@echo "  MATOMO_URL        - Matomo instance URL (default: https://matomo.riksarkivet.se/)"
	@echo "  MATOMO_SITE_ID    - Site ID for tracking (default: 25)"
	@echo "  MATOMO_DOMAINS    - Comma-separated domains (default: *.riksarkivet.se,huggingface.co)"
