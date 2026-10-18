# reservingT

A simple reserving engine implementing Chain Ladder and Bornhuetter-Ferguson, built with sound software engineering practices. Everything up to the commit "test for bf" was done by hand: the reserving engine, dependency management, testing and repository structure. The UI was built with spec-driven development and AI.

## Who built what

| Part | Built by | Where to look |
|---|---|---|
| Reserving engine (`reserving.py`), its tests | By hand | Commits up to [`1c5af40`](https://github.com/Niekrenz82/reservingT/commit/1c5af40) |
| Dependencies (`uv`), repository structure | By hand | Commits up to [`1c5af40`](https://github.com/Niekrenz82/reservingT/commit/1c5af40) |
| Frontend (`app/`, `triangle_io.py`, theme) | AI (Claude Code), spec-driven, reviewed by hand | Commits after [`1c5af40`](https://github.com/Niekrenz82/reservingT/commit/1c5af40) |
| Spec and rules (`docs/specs/`, `CLAUDE.md`) | Written by hand, edited with AI | From [`31bffe9`](https://github.com/Niekrenz82/reservingT/commit/31bffe9) onward |

## Run the app

```powershell
uv sync
uv run streamlit run app/streamlit_app.py
```

Upload a triangle from `testdata/` in the sidebar, press **Develop**, and the empty lower part of the triangle is filled in.

## Run the tests and linter

```powershell
uv run pytest -v
uv run ruff check
```

## More

- `docs/building_journal.md`: how the project was built, step by step.
- `docs/specs/streamlit_frontend.md`: the spec the app was built from.
