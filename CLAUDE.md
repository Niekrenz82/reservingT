# reservingT

Python package for loss reserving: `Triangle`, `ChainLadder`, `BornhuetterFerguson`.

## Layout

- `src/reservingt/`: library
- `tests/`: pytest tests
- `notebooks/`: scratch work, not part of the package
- `docs/specs/`: feature specs. Feature specs live in `docs/specs/`. Read the relevant one before implementing.
- `app/`: Streamlit frontend

## Commands

- `uv run pytest -v`
- `uv run ruff check`
- `uv run streamlit run app/streamlit_app.py`

## Rules

- Do not change the calculation logic in `src/reservingt/reserving.py` for UI reasons.
