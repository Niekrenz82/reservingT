# building Journal

This will be a journal to capture the steps along the way building this small project.

## Plan

## Setup

First create github repo, and select the `python` option for the `.gitignor` file. This will create a repo with only a `.gitignore` file, this file handles the file types that git will track.

To set up the project run the following `uv init` command, this will build the project structure for us. We will create are reserving engine in [../src/reservingT/](../src/reservingT/), as it will then be portable as a package.
```powershell
uv init --app --package
```

Then add the first relevant dependencies, this will also create a virtual env to run python code, in the `.venv` folder. 
```powershell
uv add numpy pandas 
uv add --dev pytest ruff
```

Create a folder `notebooks` for interactive `.py` files that i will use for testing along the way.