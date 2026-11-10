CHECK_TASKS := lint test
BUILD_OUTPUTS :=
CONTAINER_BUILD_ARGS := NODE_VERSION=$(patsubst v%,%,$(shell cat .nvmrc)) PYTHON_VERSION=$(shell cat .python-version)

override COMMAND := $(value COMMAND)
override TEST_ARGS := $(value TEST_ARGS)

export CHECK_TASKS BUILD_OUTPUTS CONTAINER_BUILD_ARGS TEST_ARGS COMMAND

.PHONY: check check-info lint test build exec

check lint test build exec:
	@./tests/container/run $@

check-info:
	@./tests/container/run info
.DEFAULT_GOAL := check
