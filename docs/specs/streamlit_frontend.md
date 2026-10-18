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

