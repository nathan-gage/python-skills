# Run claim proofs via uv.
#   make            # runtime matrix (all versions) + typing checks
#   make 3.14       # one runtime version
#   make typing     # checker-fixture claims (mypy, pyright, ty)
#   make -k         # keep going past a failing version
PYTHON_VERSIONS ?= 3.11 3.12 3.13 3.14

.PHONY: all typing $(PYTHON_VERSIONS)

all: $(PYTHON_VERSIONS) typing

$(PYTHON_VERSIONS):
	@printf '\n=== Python $@ ===\n'
	uv run --python $@ pytest

typing:
	@printf '\n=== typing checkers (mypy, pyright, ty) ===\n'
	uv run pytest typing_tests -q
