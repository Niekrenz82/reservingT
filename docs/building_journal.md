# Building reservingT: a journal

This journal records how **reservingT** was built, step by step. It explains the decisions behind each part, so you can rebuild the project or see why it looks the way it does.

## What you are building

**reservingT** is a Python package for **loss reserving** in non-life insurance. An insurer knows what it has paid so far on claims from each accident year, but not what it will eventually pay. The gap between the two is the *reserve*.

The data is a **loss triangle**. Rows are accident years, and columns are development years (how long after the accident the amount was recorded). The lower-right part is empty, because those years have not happened yet.

```
              dev 1     dev 2     dev 3     dev 4     dev 5
accident 1    1000      1600      1900      2050      2120
accident 2    1100      1800      2100      2240       ?
accident 3    1200      1950      2300        ?         ?
accident 4    1250      2000        ?         ?         ?
accident 5    1300        ?         ?         ?         ?
```

The package has three parts:

- **`Triangle`** holds the data and converts between cumulative and incremental form.
- **`ChainLadder`** (CL) estimates development factors from the data, fills in the empty part, and gives the ultimate loss for each year.
- **`BornhuetterFerguson`** (BF) blends the data with a prior estimate of the ultimate loss, for example from pricing. It suits recent years, where little has been observed.

**Goal:** a small, readable package in which each method is tested against values checked by hand. Write the goal down first, and come back to it when you are tempted to add something.

## 1. Set up the repository and environment

Create the repository on GitHub with the **Python** `.gitignore`, so the virtual environment and caches are never committed. Then use [uv](https://docs.astral.sh/uv/) for the project:

```powershell
uv init --app --package
```

`--package` gives an installable project with a `src/` layout. Set `.python-version` to `3.13`.

Dependencies are split into two groups:

```powershell
uv add numpy pandas
uv add --dev pytest ruff streamlit
```

Runtime dependencies are installed for anyone who uses the package, so keep that list short. Tools used while working (tests, linters, the app) go in `dev`. Commit `uv.lock` so everyone gets the same versions. Run tools with `uv run <command>`, which syncs the environment first.

Tell pytest where the tests are, in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
```

## 2. Repository structure

```
reservingT/
├── app/                     # Streamlit frontend (entry point: streamlit_app.py)
├── docs/
│   └── specs/               # feature specs, written before the code
├── notebooks/               # scratch work, not part of the package
├── src/reservingt/
│   ├── reserving.py         # Triangle, ChainLadder, BornhuetterFerguson
│   └── triangle_io.py       # CSV reading and writing, running a method
├── testdata/                # sample triangles in CSV form
├── tests/                   # pytest test suite
├── .streamlit/config.toml   # theme for the app
├── CLAUDE.md                # project rules for the AI assistant
└── pyproject.toml           # metadata, dependencies, tool settings
```

Each folder has a different lifecycle:

- **`src/`** is the product. Users install it and depend on it.
- **`tests/`** checks the product. The product never imports from it.
- **`notebooks/`** is exploration. It changes often and is not reviewed like library code.
- **`app/`** is the user interface. It holds no calculations; those stay in `src/`.

The `src/` layout means tests import the package the way an installed user would. A test cannot quietly import a file that is not part of the package.

## 3. The `Triangle` class

`Triangle` checks its input and converts between forms:

- The constructor rejects anything that is not a square 2D array. A triangle needs as many accident years as development years.
- `to_incremental` subtracts each cell from the one to its left.
- `to_cumulativ` does the reverse, adding up the running total.

Unobserved cells are `NaN`, not zero. Zero could mean "no claims", and the two would be indistinguishable. `NaN` also spreads through later arithmetic, so a missing value cannot quietly turn into a plausible number.

## 4. Chain Ladder

Chain Ladder estimates a **development factor** for each development year `j`, using only the rows where column `j` has been observed:

```
f_j = sum of column j  /  sum of column j-1   (over the same observed rows)
```

Each empty cell is the cell to its left times the factor for its column. The last column of the filled triangle is the **ultimate** loss for each year, and:

```
reserve = ultimate - latest observed amount
```

Check the code against numbers worked out by hand. For the 5×5 test triangle, the first factor is

```
(1600 + 1800 + 1950 + 2000) / (1000 + 1100 + 1200 + 1250) = 7350 / 4550 = 21/13
```

A test that only copies the code's output proves that the output has not changed. It does not prove the output is right.

## 5. Bornhuetter-Ferguson

BF blends the Chain Ladder projection with a prior ultimate `prior[i]`:

```
BF[i, j] = p_j * CL[i, j] + (1 - p_j) * prior[i]
```

Here `p_j` is the share of the ultimate already expected to be reported by development year `j`, which is `1 / (cumulative development from j to ultimate)`. Recent years have a small `p_j`, so they lean on the prior. Older years have `p_j` close to 1, so they lean on the data.

BF expects cumulative data, so the app converts an incremental triangle first.

## 6. Testing

A reserving calculation has no obvious "looks right" check: a wrong factor still gives plausible numbers. So each test states the expected answer in advance.

Shared test data lives in `tests/conftest.py`. Pytest passes a fixture to any test that names it as a parameter:

```python
@pytest.fixture
def cum_5x5():
    return np.array([
        [1000, 1600, 1900, 2050, 2120],
        [1100, 1800, 2100, 2240, np.nan],
        [1200, 1950, 2300, np.nan, np.nan],
        [1250, 2000, np.nan, np.nan, np.nan],
        [1300, np.nan, np.nan, np.nan, np.nan],
    ])
```

Three kinds of test are used:

- **Properties:** a round trip (cumulative → incremental → cumulative) returns the original, and a non-square triangle is rejected. These need no hand calculation and catch many bugs.
- **Hand-checked values:** the Chain Ladder full triangle and reserves match the values worked out by hand in section 4.
- **Consistency:** BF with the Chain Ladder ultimates as the prior returns the Chain Ladder ultimates. The prior and the Chain Ladder ultimate are then equal, so any blend of the two gives the same number.

Compare floats with a tolerance, for example `np.testing.assert_array_almost_equal(..., decimal=2)`. Use exact equality only for integers. A tolerance that is too loose hides real errors.

```powershell
uv run pytest -v
```

## 7. Linting

[Ruff](https://docs.astral.sh/ruff/) checks style and common mistakes:

```powershell
uv run ruff check          # report problems
uv run ruff check --fix    # fix what it can
```

Put the rules in `pyproject.toml`, not on one machine, so every run gives the same result.

## 8. The frontend, built from a spec

The library was built by hand. The Streamlit frontend was built with an AI coding assistant, using **spec-driven development**: you write down what the feature must do, and the assistant builds to that document. When the code and the spec disagree, find out which one is wrong before changing either.

The order matters:

1. **Write the spec** in `docs/specs/streamlit_frontend.md`. It covers the goal, non-goals, inputs, outputs, layout, constraints and acceptance criteria. Non-goals are as important as goals: they stop the assistant from adding features nobody asked for.
2. **Write the project rules** in `CLAUDE.md`. The assistant reads this file at the start of every session. It lists the layout, the commands, and the hard rules. The most important rule here is that `src/reservingt/reserving.py` must not change for any reason, so the frontend can only call the library.
3. **Create a skeleton app** that runs, so there is a working starting point.
4. **Implement the spec one part at a time.** After each part, run the tests and the linter, and check the diff. `reserving.py` must show no changes.

The result is a page where you upload a triangle in the sidebar, press **Develop** to fill in the empty lower part, and see the reserves, with a download for the completed triangle. The spec was updated during the work when the layout changed, so the spec and the app still agree.

Keep the calculations in `src/reservingt/` and out of the app. The calculations can then be tested without starting Streamlit.

## Next steps

- Add tests for development factors and for reserves on the 10×10 sample.
- Check the BF formula against the textbook definition, using exact values for a chosen prior.
- Decide how to handle a tail factor before comparing with other packages.
