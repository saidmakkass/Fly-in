NAME = src

install:
	@uv sync

run:
	@uv run python -m $(NAME)

lint:
	flake8 $(NAME)
	mypy $(NAME) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --follow-imports=skip

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +

debug:
	@uv run python -m pdb -m $(NAME)
