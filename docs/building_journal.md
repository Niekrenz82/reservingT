# Building reservingT: a step-by-step journal

This journal is a guide to building **reservingT** from an empty GitHub repository. Each step says what to do, gives the commands and code, and ends with a suggested commit message. Follow the steps in order and you end up with the same project.

## What you are building

**reservingT** is a Python package for **loss reserving** in non-life insurance. An insurer knows how much it has paid so far on claims from each accident year, but not how much it will eventually pay. Reserving methods estimate that future amount, which is the *reserve*.

The data is a **loss triangle**. Rows are accident years, and columns are development years (how many years after the accident the amount was recorded). The bottom-right part of the triangle is empty, because those years have not happened yet.

```
              dev 0     dev 1     dev 2     dev 3     dev 4
accident 0    1000      1600      1900      2050      2120
accident 1    1100      1800      2100      2240       ?
accident 2    1200      1950      2300        ?         ?
accident 3    1250      2000        ?         ?         ?
accident 4    1300        ?         ?         ?         ?
```

The package has three parts:

- **`Triangle`** holds the data and converts between cumulative and incremental form.
- **`ChainLadder`** (CL) estimates development factors from the observed data, projects the triangle forward and gives the ultimate loss for each year.
- **`BornhuetterFerguson`** (BF) blends the data with a prior estimate of the ultimate loss, for example from pricing. This helps for recent years, where little has been observed.

**Goal:** a small, readable package in which each method is tested against values checked by hand, with a history that explains each decision.

> **Box: Write the goal down first.**
> A one-paragraph goal and a short list of what is in and out of scope keeps a project from growing by accident. Write it before the first line of code, and come back to it when you are tempted to add something.

## Step 1: Create the repository

1. On GitHub, create a new repository named `reservingT`. Choose the **Python** option for `.gitignore`.
2. Clone it locally.

The `.gitignore` file tells git which files to leave out, such as `.venv/`, cache folders and build output. It is the first commit, so the virtual environment can never be committed by accident.

> **Box: Version control basics.**
> - Commit small, related changes. Each message says what changed and why.
> - Put ignore rules in place before the first real commit. Generated files (environments, caches, build output) are never tracked.
> - Never commit secrets or machine-specific settings.
> - The history is documentation. A reader in a year should be able to follow it.

*Suggested commit:* `Initial commit` (the GitHub-generated `.gitignore`).

## Step 2: Initialise the project with uv

[uv](https://docs.astral.sh/uv/) replaces `pip`, `venv`, `pyenv` and the lock-file tools. Install it first, then run:

```powershell
uv init --app --package
```

- `--package` creates an installable project with a `src/` layout and a `pyproject.toml`.
- `--app` adds a command-line entry point, so the project has a `main` function.

This creates `pyproject.toml`, `.python-version`, `uv.lock`, `src/reservingt/__init__.py` and a `README.md`. Set the Python version in `.python-version` to `3.13`, and check that `pyproject.toml` contains `requires-python = ">=3.13"`.

Add the editor word list the project uses. Create `.vscode/ltex.hiddenFalsePositives.en-US.txt` containing:

```
{"rule":"UPPERCASE_SENTENCE_START","sentence":"^\\Qbuilding Journal\\E$"}
```

Create the folders for the rest of the project:

```powershell
mkdir docs, notebooks, tests
```

> **Box: Dependency management with uv.**
> `pyproject.toml` records what the project *wants*. `uv.lock` records what it *uses*: every dependency, including indirect ones, pinned to one version. Commit both, so everyone who clones the repository gets the same versions.
>
> | Command | What it does |
> |---|---|
> | `uv add numpy pandas` | Adds runtime dependencies (installed for users of the package) |
> | `uv add --dev pytest ruff` | Adds development-only dependencies |
> | `uv sync` | Makes `.venv` match `uv.lock` exactly |
> | `uv run <command>` | Syncs the environment, then runs the command inside it |
>
> Prefer `uv run pytest` to `.venv\Scripts\python.exe -m pytest`. The direct call skips the sync, so it can run against stale packages.

> **Box: Keep the runtime list short.**
> Every runtime dependency becomes a requirement for anyone who installs the package. Put tools you use while working (notebooks, dashboards, linters) in the `dev` group.

### 2.1 Add the dependencies

```powershell
uv add numpy pandas
uv add --dev pytest ruff ipykernel jupyter marimo plotly streamlit
```

Notebook and dashboard tools go in the `dev` group, so the package's runtime requirements stay at `numpy` and `pandas`.

### 2.2 Set up pytest

Add this to the end of `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
```

This tells pytest to look only in `tests/`. Without it, pytest would also search the notebooks folder for files matching `test_*.py`.

*Suggested commit:* `Set up uv project with runtime and dev dependencies`

## Step 3: Folder structure

Before writing code, the folders look like this:

```
reservingT/
├── .gitignore               # files git must not track
├── .python-version          # Python version for the project (3.13)
├── .vscode/                 # editor settings shared with the repository
├── app/
│   └── streamlit_app.py     # Streamlit frontend (added in Step 10)
├── CLAUDE.md                # project rules read automatically by Claude Code
├── docs/
│   ├── building_journal.md  # this file
│   └── specs/               # feature specs, written before the code
├── notebooks/               # interactive scratch work, not part of the package
├── src/
│   └── reservingt/
│       ├── __init__.py      # package marker and placeholder main()
│       └── reserving.py     # Triangle, ChainLadder, BornhuetterFerguson
├── tests/                   # pytest test suite
├── pyproject.toml           # project metadata, dependencies, tool settings
├── uv.lock                  # exact versions of every dependency
└── README.md
```

> **Box: Repository structure.**
> Separate things with different lifecycles:
> - **`src/`** is the product: code users install and depend on.
> - **`tests/`** checks the product. The product never imports from it.
> - **`notebooks/`** is exploration. It changes often and is not reviewed like library code.
> - **`docs/`** is for people reading about the project.
>
> When one folder mixes these, changes become hard to review. Keep them apart from the start.

### 3.1 Why a `src/` layout

The code lives in `src/reservingt/`, not at the top level. Tests and notebooks then import the package the way an installed user would. A test cannot accidentally import a file from the working folder that is not part of the package, so packaging mistakes show up early.

uv installs the project in *editable* mode. `import reservingt` points at `src/reservingt/`, and edits take effect without reinstalling. If the import fails with `ModuleNotFoundError`, run `uv sync`.

## Step 4: The `Triangle` class

Create `src/reservingt/reserving.py`:

```python
from abc import ABC, abstractmethod
import numpy as np

class Triangle:
    """
    Triangle to hold losses over origin and development.
    """
    def __init__(self, data: np.ndarray, incremental: bool, ):
        data_shape = data.shape
        if data.ndim != 2:
            raise ValueError("Triangle must be 2d")
        if data_shape[0] != data_shape[1]:
            raise ValueError("Must have same rows and columns")
        self.data = data
        self.incremental = incremental
        self.n = data.shape[0]

    # Method: Go from cumulativ to incremental triangle
    def to_incremental(self) -> np.ndarray:
        if self.incremental:
            raise ValueError("Triangle is already incremental.")
        incremental = np.full_like(self.data, np.nan)
        C = self.data.copy()
        for i in range(self.n):
            for j in range(self.n - i):
                if j == 0:
                    incremental[i,j] = C[i,j]
                else:
                    incremental[i,j] = C[i,j] - C[i, j-1]
        return incremental

    # Method: Go from incremental to cumulativ triangle
    def to_cumulativ(self) -> np.ndarray:
        if not self.incremental:
            raise ValueError("Triangle is already cumulativ.")
        cumulativ = np.full_like(self.data, np.nan)
        I = self.data
        for i in range(self.n):
            for j in range(self.n - i):
                if j == 0:
                    cumulativ[i,j] = I[i,j]
                else:
                    cumulativ[i,j] = I[i,j] + cumulativ[i,j-1]
        return cumulativ

class ReservingMethod(ABC):

    @abstractmethod
    def calc_reserve(self, triangle: Triangle):
        """calculate the reserve."""
```

What this does:

- The constructor rejects anything that is not a square 2D array. A triangle must have as many origin years as development years.
- `to_incremental` subtracts each cell from the one to its left. The first column is unchanged.
- `to_cumulativ` does the reverse, adding the running total.
- The output cells that are not observed are `NaN`, not zero. A zero could mean "no claims" or "a real zero loss", and the two would be indistinguishable. `NaN` stays visible in later arithmetic, so a missing value cannot quietly become a plausible number.

> **Box: Small commits that do one thing.**
> Commit the constructor and the conversions separately, or together if they form one idea. Do not mix a notebook experiment into the same commit.

*Suggested commit:* `Add Triangle class with incremental and cumulative conversions`

## Step 5: Chain Ladder

Chain Ladder estimates a **development factor** for each development year `j`. It is the sum of column `j` divided by the sum of column `j-1`, using only the rows where column `j` is observed:

```
f_j = sum over observed rows of C[:, j]  /  sum over the same rows of C[:, j-1]
```

Each empty cell is then the cell to its left times the factor for its column. The last column of the filled triangle gives the ultimate loss for each year.

Add this to `reserving.py`, below `ReservingMethod`:

```python
class ChainLadder(ReservingMethod):
    """
    Method for ChainLadder based reserving
    """

    def __init__(self):
        self.dev_factors = None
        self.full_triangle = None

    # Method: Calc dev factors
    def _calc_dev_factors(self, triangle: Triangle):
        n = triangle.n
        dev_factors = np.zeros(n-1)
        C = triangle.data
        for j in range (1,n):
            dev_factors[j-1] = C[0:(n-j),j].sum()/C[0:(n-j),j-1].sum()
        return dev_factors

    # Method: Fill triangle using CL method
    def _fill_triangle(self, triangle: Triangle, dev_factors):
        full_data = triangle.data.copy()
        n = triangle.n
        for i in range(1, n):
            for j in range(n-i, n):
                full_data[i, j] = full_data[i, j-1] * dev_factors[j-1]
        return full_data

    # Method: Main for calculating the reserve
    def calc_reserve(self, triangle: Triangle):
        """
        Method for calculating the reserves and incremental developed triangle.
        """
        cumulativ = Triangle(triangle.to_cumulativ(), incremental=False) if triangle.incremental else triangle
        self.dev_factors = self._calc_dev_factors(cumulativ)
        full_triangle = self._fill_triangle(cumulativ, self.dev_factors)
        n = triangle.n

        ultimates = full_triangle[:,-1]
        diagnol = [full_triangle[i,n-(i+1)] for i in range(n)]
        reserves = ultimates - diagnol

        full_incremental = np.zeros_like(full_triangle)
        for i in range(n):
            for j in range(n):
                if j == 0:
                    full_incremental[i,j] = full_triangle[i,j]
                else:
                    full_incremental[i,j] = full_triangle[i,j] - full_triangle[i,j-1]

        return {
            "ultimates": ultimates,
            "reserves": reserves,
            "development_factor": self.dev_factors,
            "full_triangle": full_triangle,
            "full_incremental_triangle": full_incremental
        }
```

Worked check: for the 5×5 test triangle in Step 7, the first factor is

```
(1600 + 1800 + 1950 + 2000) / (1000 + 1100 + 1200 + 1250) = 7350 / 4550 = 21/13
```

> **Box: Check a few numbers by hand before you test them.**
> A test that copies the code's output only proves the output has not changed. Work one or two values out by hand, or in a spreadsheet, before you write them into a test.

*Suggested commit:* `Add Chain Ladder development factors, projection and reserves`

## Step 6: Bornhuetter-Ferguson

BF blends the Chain Ladder projection with a prior estimate of the ultimate loss `prior[i]`. For each empty cell:

```
BF[i, j] = p_j * CL[i, j] + (1 - p_j) * prior[i],   where p_j = 1 / (cumulative development from j to ultimate)
```

Recent years have a small `p_j`, so they lean on the prior. Older years have a `p_j` close to 1, so they lean on the data.

Add this to `reserving.py`:

```python
class BornhuetterFerguson(ReservingMethod):
    """
    Implementation of the BornhuetterFerguson method.
    """
    def __init__(self, prior: np.ndarray):
        self.prior = prior

    def calc_reserve(self, triangle: Triangle):
        CL = ChainLadder()
        n = triangle.n
        prior = self.prior
        CL_res = CL.calc_reserve(triangle=triangle)
        CL_triangle = CL_res['full_triangle']
        CL_factors = CL_res['development_factor']
        BF_triangle = triangle.data.copy()
        for i in range(1, n):
            for j in range(n-i,n):
                if j == (n-i):
                    F = CL_factors[j-1]
                else:
                    F = F*CL_factors[j-1]
                p = 1/F
                BF_triangle[i,j] = p*CL_triangle[i,j]+(1-p)*prior[i]

        ultimates = BF_triangle[:,-1]
        diagnol = [BF_triangle[i,n-(i+1)] for i in range(n)]
        reserves = ultimates - diagnol

        full_incremental = np.zeros_like(BF_triangle)
        for i in range(n):
            for j in range(n):
                if j == 0:
                    full_incremental[i,j] = BF_triangle[i,j]
                else:
                    full_incremental[i,j] = BF_triangle[i,j] - BF_triangle[i,j-1]

        return {
            "ultimates": ultimates,
            "reserves": reserves,
            "development_factor": CL_factors,
            "full_triangle": BF_triangle,
            "full_incremental_triangle": full_incremental
        }
```

> **Box: Keep exploration out of library commits.**
> Experiments belong in `notebooks/`. Commit the library change on its own, and either commit the notebook separately or leave it out of git. A commit that mixes both is hard to review.

### 6.1 The scratch notebook

Create `notebooks/adhoc.py`. It is a plain Python file with `#%%` cell markers, which VS Code and other editors run one cell at a time:

```python
#%%
import numpy as np
from reservingt.reserving import Triangle, ChainLadder, BornhuetterFerguson

tri = Triangle(np.array([
    [1000.0, 1600.0, 1900.0],
    [1100.0, 1800.0, np.nan],
    [1200.0, np.nan, np.nan],
]), incremental=False)

# %%
ChainLadder().calc_reserve(tri)["development_factor"]
```

Name it `adhoc.py`, not `test_*.py`. Pytest collects files whose names start with `test_`, and a scratch file should never be run as a test.

*Suggested commit:* `Add BornhuetterFerguson class` (the notebook file is a separate commit, or left out).

## Step 7: Testing

A reserving calculation has no obvious "looks right" check. A wrong development factor gives plausible-looking numbers. A test states the expected answer in advance, so any change to the result is caught at once.

Create the test files below in `tests/`.

### 7.1 Shared fixtures: `tests/conftest.py`

```python
import numpy as np
import pytest

NAN = np.nan

@pytest.fixture
def cum_5x5():
    """
    Cumulativ 5x5 triangle for testing.
    """
    return np.array([
        [1000, 1600, 1900, 2050, 2120],
        [1100.0, 1800.0, 2100.0, 2240.0, NAN],
        [1200.0, 1950.0, 2300.0, NAN, NAN],
        [1250.0, 2000.0, NAN, NAN, NAN],
        [1300.0, NAN, NAN, NAN, NAN]
    ])

@pytest.fixture
def expected_CL_5x5():
    """
    Expected values, computed by hand with exact fractions in a separate script.
    """
    return {
        "factors": [21 / 13, 126 / 107, 429 / 400, 212 / 205],
        "full_triangle": np.array([
            [1000.0, 1600.0, 1900.0, 2050.0, 2120.0],
            [1100.0, 1800.0, 2100.0, 2240.0, 2316.4878],
            [1200.0, 1950.0, 2300.0, 2466.7500, 2550.9805],
            [1250.0, 2000.0, 2355.1402, 2525.8879, 2612.1377],
            [1300.0, 2100.0, 2472.8972, 2652.1822, 2742.7446],
        ]),
        "ultimates": [2120.0, 2316.4878, 2550.9805, 2612.1377, 2742.7446],
        "reserves": [0.0, 76.4878, 250.9805, 612.1377, 1442.7446],
        "total_reserve": 2382.3505,
    }

@pytest.fixture
def triangle_3x2():
    """
    Triangle with wrong dimensions.
    """
    return np.array([
        [1, 2, 3],
        [1, 2, NAN]
    ])
```

A fixture is a function that prepares data. A test requests it by naming it as a parameter, and pytest passes in the result. `conftest.py` is loaded automatically, so no test file imports it.

### 7.2 Triangle tests: `tests/test_triangle.py`

```python
import pytest
import numpy as np

from reservingt.reserving import Triangle

def test_wrong_dimensions(triangle_3x2):
    with pytest.raises(ValueError, match= "Must have same rows and columns"):
        Triangle(data=triangle_3x2, incremental=False)

def test_cum_inc_cum(cum_5x5):
    tri = Triangle(data=cum_5x5, incremental=False)
    tri_inc = Triangle(tri.to_incremental(),incremental=True)
    tri_cum = tri_inc.to_cumulativ()

    np.testing.assert_array_almost_equal(cum_5x5, tri_cum)
```

The second test is a round trip: convert to incremental and back, and check that the original comes back.

### 7.3 Chain Ladder test: `tests/test_chain_ladder.py`

```python
import numpy as np
import pytest

from reservingt.reserving import Triangle, ChainLadder

def test_CL_reserving_calc(cum_5x5, expected_CL_5x5):
    """
    Testing calculations using the chain ladder method.
    """
    tri = Triangle(cum_5x5, incremental=False)
    CL = ChainLadder()
    res = CL.calc_reserve(triangle=tri)

    np.testing.assert_array_almost_equal(
        expected_CL_5x5['full_triangle'],
        res['full_triangle'],
        decimal=2
    )
```

### 7.4 Bornhuetter-Ferguson test: `tests/test_bf.py`

```python
import numpy as np
import pytest

from reservingt.reserving import Triangle, ChainLadder, BornhuetterFerguson

def test_bf_calculations(cum_5x5, expected_CL_5x5):
    tri = Triangle(cum_5x5, incremental=False)
    BF = BornhuetterFerguson(prior=expected_CL_5x5['ultimates'])
    res = BF.calc_reserve(triangle=tri)

    np.testing.assert_array_almost_equal(
        expected_CL_5x5['ultimates'],
        res['ultimates'],
        decimal=1
    )
```

This test uses the Chain Ladder ultimates as the prior. With that prior, BF gives the Chain Ladder ultimate for every year, so the check is valid. The projected cells in between do differ from Chain Ladder, which is expected for BF. The test only checks consistency with Chain Ladder. To check the BF formula itself, compare against exact values for a different prior, calculated by hand.

> **Box: Choose tolerances on purpose.**
> Values such as `1.1333…` cannot be stored exactly, so compare floats with a tolerance: `assert_array_almost_equal(..., decimal=...)` or `assert_allclose(..., atol=...)`. Use exact equality only for exact values, such as the integers in an incremental triangle. Pick the tightest tolerance your expected values support. A loose one hides real errors.

> **Box: Test the predictable properties first.**
> Round trips, rejected shapes and totals equal to the sum of their parts need no hand calculation, and they catch many bugs. Add exact-value tests after them.

> **Box: Tests are plain functions.**
> Pytest finds `test_*` functions in `test_*.py` files. Classes are optional. Keep one test file per part of the code.

Run them:

```powershell
uv run pytest -v
```

*Suggested commit:* `Add tests for Triangle, Chain Ladder and BF`

## Step 8: Linting with ruff

Ruff checks style and common mistakes, and fixes many of them automatically:

```powershell
uv run ruff check          # report problems
uv run ruff check --fix    # fix what it can
```

Run it after each step. Fix what it reports in the library code first, then the tests. The unused `pytest` and `ChainLadder` imports in the test files are flagged, and the import blocks are re-sorted into standard library, third-party and first-party groups.

> **Box: Put tool configuration in the repository.**
> A linter reads its rules from configuration. If the rules come from a file on one machine, the same command gives different results on another. Add a `[tool.ruff]` section to `pyproject.toml` when you choose rules that differ from the defaults, and decide whether notebooks follow the same rules, for example with `per-file-ignores`.

*Suggested commit:* `Fix ruff findings`

## Step 9: Check the finished project

From a clean clone, run:

```powershell
uv sync
uv run pytest -v
uv run ruff check
```

All four tests should pass. The reserves for the 5×5 triangle should match the table in `conftest.py`, to the precision the tests check.

## Step 10: A frontend, built from a spec

The library is finished and tested, so the next piece is a small web page where someone can upload a loss triangle, pick a method and download the completed triangle. The page is a [Streamlit](https://streamlit.io/) app, and it is built with an AI coding assistant, Claude Code.

The approach is **spec-driven development**. You write down what the feature must do, and the assistant builds to that document. The spec is the contract: when the code and the spec disagree, you find out which one is wrong before you change either.

The order matters:

1. Write the spec, and commit it.
2. Write the rules the assistant must follow, in `CLAUDE.md`.
3. Create the app skeleton.
4. Ask the assistant to implement the spec, one piece at a time.

### 10.1 Write the spec

Create `docs/specs/streamlit_frontend.md`. A spec has the same headings every time, so the assistant and you know where to look:

```markdown
# Streamlit frontend

## Goal

A light Streamlit frontend for the reservingt package.

Has to have one simple interface where a loss triangle can be loaded in from a csv file. Then converted to a `Triangle class from src/reservingt/reserving.py` and then either CL or BF can be used to find the reserve.

## Non-goals

More then a one page simple reserve app.

## Inputs

Loss triangle, method and additional arguments for each method in `src/reservingt/reserving.py`.

## Outputs

A fully developed triangle, that should be downloadable.

## Layout

One page with a upload/download option, method selection and triangle display.

## Structure

Entry point is `app/streamlit_app.py`. Non-UI logic can be found in `src/reservingt/`.

## Constraints

- Python 3.13
- Use the existing dependencies
- `src/reservingt/reserving.py` is not modified
- Use logic in `src/reservingt/reserving.py` to perform any calculations used for the reserves.

## Acceptance criteria

When you can upload a loss triangle, develop it using a method and download a developed triangle that is coherent with the method.
```

What each section does:

- **Goal and non-goals** say what the feature is, and, just as important, what it is not. "More than a one page simple reserve app" is the line that stops the page from growing into a dashboard.
- **Inputs and outputs** name the data going in and coming out. Here the input is a CSV triangle and the output is a completed triangle you can download.
- **Constraints** are the rules the implementation must respect. Two of them protect the library: the calculations stay in `reserving.py`, and that file is not edited.
- **Acceptance criteria** say how you know the feature is done. Write them as something you can check by trying the app.

> **Box: Write the spec as if the reader has never seen the project.**
> The assistant starts each session without your memory of the discussion. Anything it needs (file names, the method names, the constraints) has to be in the spec or in `CLAUDE.md`. Vague words such as "nice" or "simple" are fine as a summary, but the constraints and acceptance criteria must be specific.

> **Box: Non-goals are part of the spec.**
> Without them, an assistant will add features that look helpful, such as charts, login or multiple file types. Each one is more code to review. Write the things you are *not* building.

*Suggested commit:* `Add Streamlit frontend spec`

### 10.2 Write the project rules: `CLAUDE.md`

Claude Code reads a file called `CLAUDE.md` in the project root at the start of every session. It holds what is true about the project and how to work in it. Create `CLAUDE.md`:

```markdown
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

- Do not change the code in `src/reservingt/reserving.py` for any reason.
- You can touch anything in `app/`
```

Each part has a job:

- **Layout** tells the assistant where things live, so it does not search the whole repository.
- **Commands** are the exact commands to test, lint and run the app. The assistant can run them to check its own work.
- **Rules** are the hard limits. "Do not change ... for any reason" is deliberate. The first draft said "for UI reasons", which left room for the assistant to decide that a change was not a UI reason. Review of the file tightened the wording, and a rule that is clear is easier to follow than one that needs interpreting.

> **Box: A rule with a reason is easier to keep.**
> If a rule matters, say why in one line, for example "the library is tested against hand-checked values, so a silent edit would break the trust in those tests". The assistant then knows what to protect when a situation comes up that the rule did not cover.

*Suggested commit:* `Add CLAUDE.md with project layout, commands and rules`

### 10.3 Create the app skeleton

Create `app/streamlit_app.py`:

```python
import streamlit as st

st.title("reservingT")
```

This is deliberately small. It proves that Streamlit is installed and that the page loads. Streamlit was added as a dev dependency in Step 2.1, so no new install is needed.

Run it:

```powershell
uv run streamlit run app/streamlit_app.py
```

Streamlit opens a page in your browser at `http://localhost:8501`. Stop it with `Ctrl+C` in the terminal.

> **Box: Start small, then let the assistant grow it.**
> A skeleton that runs gives both you and the assistant a working starting point. Each later change is then a small step you can see in the browser, rather than one large block of untested code.

*Suggested commit:* `Add Streamlit app skeleton`

### 10.4 Implement the spec

Ask Claude Code to implement `docs/specs/streamlit_frontend.md`. Ask for one part at a time, for example "read the spec and implement the upload and CSV parsing first". After each part:

1. Run the app and try the acceptance criteria by hand.
2. Run `uv run pytest -v` and `uv run ruff check`.
3. Check the diff. `src/reservingt/reserving.py` must be unchanged. Run `git diff -- src/reservingt/reserving.py` and expect no output.
4. Commit when the part works.

Keep the calculation logic in `src/reservingt/`, so the app only handles the page. The spec asks for this, and it means the calculations can be tested without starting Streamlit.

> **Box: Review the diff, not the summary.**
> An assistant's summary says what it intended. The diff says what it did. Read the diff before each commit, and check the constraints from the spec against it.

*Suggested commit:* one commit per part, for example `Add CSV upload to Streamlit app`.

## Next steps

Once the build is working, the following are natural extensions, in no particular order:

- Tighten the test tolerances to match the four-decimal expected values.
- Add tests for development factors, reserves and the total reserve.
- Add a test for the `"Triangle must be 2d"` check.
- Check the BF formula against the textbook definition with exact values for a chosen prior.
- Decide on a tail factor before comparing with other packages.
- Fill in the `README.md`.
- Finish the Streamlit frontend by working through the acceptance criteria in `docs/specs/streamlit_frontend.md`.
