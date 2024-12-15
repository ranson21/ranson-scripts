# Configuration variables
PROJECT_ID := $(shell gcloud config get-value project)
LOCATION := us-central1
BUILDER_NAME := github-ops-builder
BUILDER_TAG := latest
BUILDER_IMAGE := $(LOCATION)-docker.pkg.dev/$(PROJECT_ID)/docker/$(BUILDER_NAME):$(BUILDER_TAG)

# Directory structure setup
.PHONY: setup
setup:
	@mkdir -p builders/github-ops

# Copy files to builder directory
.PHONY: copy-files
copy-files: setup
	@cp github_ops.py builders/github-ops/
	@cp cli.py builders/github-ops/
	@cp Dockerfile builders/github-ops/
	@cp requirements.txt builders/github-ops/

# Build the Docker image
.PHONY: build
build: copy-files
	@echo "Building $(BUILDER_IMAGE)..."
	@cd builders/github-ops && docker build -t $(BUILDER_IMAGE) .

# Test the Docker image locally
.PHONY: test
test: build
	@echo "Testing $(BUILDER_IMAGE)..."
	@docker run --rm $(BUILDER_IMAGE) --help

# Push the image to Docker Repository
.PHONY: push
push: build
	@echo "Pushing $(BUILDER_IMAGE)..."
	@docker push $(BUILDER_IMAGE)

# Configure Docker authentication
.PHONY: configure-docker
configure-docker:
	@echo "Configuring Docker authentication..."
	@gcloud auth configure-docker $(LOCATION)-docker.pkg.dev

# All-in-one command to build and push
.PHONY: deploy
deploy: configure-docker build test push
	@echo "Successfully built and pushed $(BUILDER_IMAGE)"

# Clean up build artifacts
.PHONY: clean
clean:
	@echo "Cleaning up..."
	@rm -rf builders
	@docker rmi $(BUILDER_IMAGE) || true

# Display help information
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make setup          - Create necessary directories"
	@echo "  make build          - Build the Docker image"
	@echo "  make test           - Test the Docker image locally"
	@echo "  make push           - Push the image to Docker repository"
	@echo "  make deploy         - Configure Docker, build, test, and push"
	@echo "  make clean          - Clean up build artifacts"
	@echo "  make help           - Display this help message"