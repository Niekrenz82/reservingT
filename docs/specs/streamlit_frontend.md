# Streamlit frontend

## Goal

A light Streamlit frontend for the reservingt package.

Has to have one simple interface where a loss triangle can be loaded in from a csv file. Then converted to a `Triangle class from src/reservingt/reserving.py` and then either CL or BF can be used to find the reserve.

## Non-goals

More then a one page simple reserve app.

## Inputs

All inputs are in the sidebar:

- Loss triangle CSV file.
- Triangle type: cumulative or incremental.
- Method: Chain Ladder or Bornhuetter-Ferguson.
- For Bornhuetter-Ferguson only: prior ultimate loss per accident year. Defaults to the Chain Ladder ultimates and can be edited.
- How to show the triangle: cumulative or incremental. This applies to both the loaded and the developed triangle.
- A **Develop** button.

## Outputs

A fully developed triangle, that should be downloadable. Also the ultimate loss and reserve per accident year, the total reserve, and the development factors.

## Layout

Sidebar: all inputs listed above.

Main area, in this order:

1. The loaded triangle. Observed cells are filled in. The unobserved lower part of the triangle is empty.
2. After **Develop** is pressed, the empty cells are filled in with the projection from the chosen method. Below the triangle: total reserve, ultimate and reserve per accident year, development factors, and a download button for the developed triangle.

Develop behaviour:

- Nothing is projected until **Develop** is pressed.
- Changing the file, triangle type, method or any prior ultimate clears the developed result. The triangle goes back to the empty lower half until **Develop** is pressed again.
- Changing only the display choice (cumulative or incremental) does not clear the result. It changes how the triangle is shown, not what is calculated.

## Structure

Entry point is `app/streamlit_app.py`. Non-UI logic can be found in `src/reservingt/`.

## Constraints

- Python 3.13
- Use the existing dependencies
- `src/reservingt/reserving.py` is not modified
- Use logic in `src/reservingt/reserving.py` to perform any calculations used for the reserves.
- Sample data lives in `testdata/`: 5x5 and 10x10 triangles, each in cumulative and incremental form, plus one invalid file.

## Acceptance criteria

- Uploading a loss triangle shows it in the main area with the lower part empty, and all inputs are in the sidebar.
- Pressing **Develop** fills in the empty lower part using the chosen method.
- For `testdata/cumulative_5x5.csv` with Chain Ladder, the total reserve is about 2382.35.
- The cumulative and incremental versions of the same triangle give the same developed result.
- The developed triangle can be downloaded as CSV, and uploading the download again gives the same triangle.
- An invalid file shows a readable error message, not a traceback.
