import numpy as np
import pandas as pd
import streamlit as st

from reservingt.triangle_io import (
    as_form,
    read_triangle_csv,
    run_method,
    triangle_to_csv,
)

st.set_page_config(page_title="reservingT", layout="wide")

METHODS = {
    "Chain Ladder": "chain_ladder",
    "Bornhuetter-Ferguson": "bornhuetter_ferguson",
    "Cape Cod": "cape_cod",
}
FORMS = ["Cumulative", "Incremental"]

# Cell regions in the triangle table
EMPTY, OBSERVED, DEVELOPED, SUMMARY, OUTSIDE = 0, 1, 2, -2, -1
INK = "#0F172A"
STRONG = "2px solid #0F172A"
LIGHT = "1px solid #E2E8F0"
TINT = {EMPTY: "#FFFFFF", OBSERVED: "#FFFFFF", DEVELOPED: "#F1F5F9", SUMMARY: "#F8FAFC"}


def heat_color(t: float) -> str:
    """Blend from pale blue (t=0) to the accent blue (t=1)."""
    low, high = (239, 246, 255), (37, 99, 235)
    red, green, blue = (round(a + (b - a) * t) for a, b in zip(low, high))
    return f"#{red:02x}{green:02x}{blue:02x}"


def border_between(region: int, other: int) -> str:
    """A strong line where observed or developed cells meet a different region."""
    if region != other and max(region, other) > 0:
        return STRONG
    return LIGHT


def cell_style(top, right, bottom, left, background, color=INK, weight=400) -> str:
    return (
        f"border-top:{top};border-right:{right};border-bottom:{bottom};border-left:{left};"
        f"background:{background};color:{color};font-weight:{weight};"
        "padding:6px 10px;text-align:right;white-space:nowrap;"
    )


def triangle_html(
    shown, observed, ultimates, reserves, heatmap: bool, factors=None, percent=None
) -> str:
    """
    The triangle as an HTML table, with the observed and developed blocks outlined.

    `shown` holds the triangle in the chosen form, with NaN for empty cells.
    `ultimates` and `reserves` are None until the triangle is developed.
    `factors` (one per development year, except the last) adds a row under the
    Dev columns. `percent` (one per accident year) adds a column after Reserve.
    """
    n = shown.shape[0]
    region = np.where(observed, OBSERVED, np.where(np.isnan(shown), EMPTY, DEVELOPED))
    filled = shown[region > 0]
    low, high = float(filled.min()), float(filled.max())
    span = (high - low) or 1.0
    extra = 3 if percent is not None else 2

    def at(i: int, j: int) -> int:
        if i < 0 or i >= n or j < 0 or j >= n + extra:
            return OUTSIDE
        return SUMMARY if j >= n else int(region[i, j])

    head = "padding:8px 10px;text-align:right;font-weight:600;font-size:12px;color:#64748B;border-bottom:1px solid #CBD5E1;white-space:nowrap;"
    headers = ["", *[f"Dev {j + 1}" for j in range(n)], "Ultimate", "Reserve"]
    if percent is not None:
        headers.append("% developed")
    header_row = "".join(f'<th style="{head}">{label}</th>' for label in headers)

    rows = []
    for i in range(n):
        row_label = (
            '<th style="padding:6px 10px;text-align:left;font-weight:600;font-size:12px;'
            f'color:#64748B;white-space:nowrap;">AY {i + 1}</th>'
        )
        cells = [row_label]
        for j in range(n + extra):
            r = at(i, j)
            text, background, color, weight = "", TINT[r], INK, 400
            if j < n:
                value = shown[i, j]
                if not np.isnan(value):
                    text = f"{value:,.0f}"
                    if heatmap:
                        t = (value - low) / span
                        background = heat_color(t)
                        color = "#FFFFFF" if t > 0.55 else INK
            elif ultimates is not None:
                if j == n:
                    text = f"{ultimates[i]:,.0f}"
                elif j == n + 1:
                    text = f"{reserves[i]:,.0f}"
                else:
                    text = f"{percent[i]:.1%}"
                weight = 600 if j <= n + 1 else 400
            style = cell_style(
                top=border_between(r, at(i - 1, j)),
                right=border_between(r, at(i, j + 1)),
                bottom=border_between(r, at(i + 1, j)),
                left=border_between(r, at(i, j - 1)),
                background=background,
                color=color,
                weight=weight,
            )
            cells.append(f'<td style="{style}">{text}</td>')
        rows.append(f"<tr>{''.join(cells)}</tr>")

    if factors is not None:
        footer_style = (
            "padding:6px 10px;text-align:right;white-space:nowrap;font-size:13px;"
            "color:#475569;border-top:1px solid #CBD5E1;"
        )
        footer = [
            (
                '<th style="padding:6px 10px;text-align:left;font-weight:600;font-size:12px;'
                'color:#64748B;white-space:nowrap;border-top:1px solid #CBD5E1;">Dev factor</th>'
            )
        ]
        for j in range(n + extra):
            text = f"{factors[j]:.4f}" if j < len(factors) else ""
            footer.append(f'<td style="{footer_style}">{text}</td>')
        rows.append(f"<tr>{''.join(footer)}</tr>")

    return (
        '<div style="overflow-x:auto">'
        '<table role="table" aria-label="Loss triangle" style="border-collapse:collapse;'
        'width:100%;font-size:14px;font-variant-numeric:tabular-nums;">'
        f"<thead><tr>{header_row}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
    )


st.title("reservingT")

with st.sidebar:
    st.header("Inputs")
    uploaded = st.file_uploader(
        "Loss triangle (CSV)",
        type="csv",
        help="Rows are accident years, columns are development years. Leave unobserved cells blank.",
    )

    if uploaded is None:
        st.caption("Sample files are in the `testdata/` folder.")
        st.info("Upload a loss triangle to start.")
        st.stop()

    try:
        data = read_triangle_csv(uploaded)
    except ValueError as error:
        st.error(str(error))
        st.stop()

    n = data.shape[0]
    file_form = st.segmented_control(
        "File contains", FORMS, default="Cumulative", required=True
    )
    show_form = st.segmented_control(
        "Show triangle as", FORMS, default="Cumulative", required=True
    )
    heatmap = st.checkbox("Heatmap", value=False, help="Shade each amount by its size.")
    method_label = st.selectbox("Method", list(METHODS))
    method = METHODS[method_label]
    incremental = file_form == "Incremental"

    prior = None
    exposure = None
    if method == "cape_cod":
        st.caption(
            "Exposure per accident year, such as premium. Starts equal for every year and can be edited."
        )
        exposure_table = st.data_editor(
            pd.DataFrame(
                {"Accident year": range(1, n + 1), "Exposure": np.full(n, 10000.0)}
            ),
            disabled=["Accident year"],
            hide_index=True,
            column_config={
                "Exposure": st.column_config.NumberColumn(format="%.0f", min_value=0)
            },
            key=f"exposure_{uploaded.file_id}",
        )
        exposure = exposure_table["Exposure"].to_numpy(dtype=float)

    if method == "bornhuetter_ferguson":
        cl_ultimates = run_method(data, incremental, "chain_ladder")["ultimates"]
        st.caption(
            "Prior ultimate loss per accident year. Starts at the Chain Ladder ultimates."
        )
        prior_table = st.data_editor(
            pd.DataFrame(
                {"Accident year": range(1, n + 1), "Prior ultimate": cl_ultimates}
            ),
            disabled=["Accident year"],
            hide_index=True,
            column_config={
                "Prior ultimate": st.column_config.NumberColumn(
                    format="%.0f", min_value=0
                )
            },
            alt="Prior ultimate loss for each accident year",
            key=f"prior_{uploaded.file_id}",
        )
        prior = prior_table["Prior ultimate"].to_numpy(dtype=float)

    prior_ok = prior is None or not np.isnan(prior).any()
    if not prior_ok:
        st.error("Every accident year needs a prior ultimate.")

    exposure_ok = exposure is None or (
        not np.isnan(exposure).any() and bool((exposure > 0).all())
    )
    if not exposure_ok:
        st.error("Every accident year needs a positive exposure.")

    inputs_ok = prior_ok and exposure_ok
    develop_clicked = st.button(
        "Develop",
        type="primary",
        icon=":material/play_arrow:",
        width="stretch",
        disabled=not inputs_ok,
    )

    # Develop stores the inputs it ran on. Results show only while the inputs still match.
    request = (
        uploaded.file_id,
        file_form,
        method,
        None if prior is None else tuple(float(x) for x in prior),
        None if exposure is None else tuple(float(x) for x in exposure),
    )
    if develop_clicked:
        st.session_state["developed_request"] = request
    developed = st.session_state.get("developed_request") == request
    stale = "developed_request" in st.session_state and not developed

st.caption(f"{uploaded.name} · {n} accident years · {show_form.lower()} view")

if developed:
    result = run_method(data, incremental, method, prior=prior, exposure=exposure)
    shown = (
        result["full_triangle"]
        if show_form == "Cumulative"
        else result["full_incremental_triangle"]
    )
    ultimates, reserves = result["ultimates"], result["reserves"]
    factors = result["development_factor"]
    # Share of each accident year's ultimate that is reported so far, from the factors.
    cdf_by_column = np.append(np.cumprod(factors[::-1])[::-1], 1.0)
    percent = 1 / cdf_by_column[::-1]
    metrics = [
        ("Total reserve", f"{float(np.sum(reserves)):,.0f}"),
        ("Total ultimate", f"{float(np.sum(ultimates)):,.0f}"),
    ]
    if "elr" in result:
        metrics.append(("Expected loss ratio", f"{float(result['elr']):.1%}"))
    for column, (label, value) in zip(st.columns(len(metrics)), metrics):
        column.metric(label, value)
else:
    shown = as_form(data, incremental, show_form == "Incremental")
    ultimates = reserves = factors = percent = None
    if stale:
        st.info("The inputs changed. Press Develop to update the triangle.")
    else:
        st.info(
            "Press Develop in the sidebar to fill in the empty lower part of the triangle."
        )

with st.container(border=True):
    st.html(
        triangle_html(
            shown, ~np.isnan(data), ultimates, reserves, heatmap, factors, percent
        ),
    )
    st.caption(
        "Outlined blocks: observed data and developed cells. Shaded cells are projected."
    )

if developed:
    st.download_button(
        "Download developed triangle (CSV)",
        data=triangle_to_csv(shown),
        file_name=f"developed_{method}_{show_form.lower()}.csv",
        mime="text/csv",
    )
