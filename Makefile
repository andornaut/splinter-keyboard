.DEFAULT_GOAL := check

NODE_IMAGE := node:$(shell sed 's/^v//' .nvmrc)
PYTHON_IMAGE := python:$(shell cat .python-version)
SHELLCHECK_IMAGE := koalaman/shellcheck:v0.11.0

export NODE_IMAGE PYTHON_IMAGE SHELLCHECK_IMAGE
export CHECK_TIMEOUT_SECONDS CHECK_MEMORY CHECK_SCRATCH_SIZE CHECK_WORK_SIZE CHECK_TMP_SIZE

.PHONY: check lint test

check lint test:
	@./tests/container/check-stock $@
