



all: upload

upload:
	rm -rf dist
	@if [ ! -f token ]; then echo "Error: token file not found"; exit 1; fi
	uv build && uv publish --token $(shell cat token)

tag:
	@if [ -z "$(TAG)" ]; then \
		echo "Error: TAG parameter is required. Usage: make tag TAG=v1.0.0"; \
		exit 1; \
	fi
	@echo "Validating tag format: $(TAG)"
	@if ! echo "$(TAG)" | grep -qE '^v[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*)?(\+[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*)?$$'; then \
		echo "Error: Invalid tag format. Expected format: v1.0.0, v1.0.0-alpha, etc."; \
		exit 1; \
	fi
	@VERSION=$$(echo "$(TAG)" | sed 's/^v//'); \
	echo "Updating version to $$VERSION in pyproject.toml"; \
	sed -i '' "s/^version = \".*\"/version = \"$$VERSION\"/" pyproject.toml
	@echo "Committing version change..."
	git add pyproject.toml
	git commit -m "Bump version to $(TAG)"
	@echo "Creating and pushing tag $(TAG)..."
	git tag $(TAG)
	git push origin $(TAG)
	git push origin main
	@echo "Successfully created and pushed tag $(TAG)"
