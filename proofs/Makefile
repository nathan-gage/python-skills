# Run claim proofs across supported Python versions via uv.
#   make            # all versions
#   make 3.14       # one version
#   make -k         # keep going past a failing version
PYTHON_VERSIONS ?= 3.11 3.12 3.13 3.14

.PHONY: all $(PYTHON_VERSIONS)

all: $(PYTHON_VERSIONS)

$(PYTHON_VERSIONS):
	@printf '\n=== Python $@ ===\n'
	uv run --python $@ pytest
