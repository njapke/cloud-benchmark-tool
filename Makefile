PROJECT_NAME := "cloud-benchmark-tool"
PKG := "$(PROJECT_NAME)"

.PHONY: dep build

all: build

dep: ## Get the dependencies
	@go mod download

build: dep ## Build the binary file
	@CGO_ENABLED=0 go build -o cmd/orchestrator/build -v $(PKG)/cmd/runner
	@CGO_ENABLED=1 CC=/usr/bin/musl-gcc go build --ldflags '-linkmode external -extldflags "-static"' -o build/ -v $(PKG)/cmd/orchestrator
