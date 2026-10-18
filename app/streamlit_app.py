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
}
FORMS = ["Cumulative", "Incremental"]


def triangle_frame(values: np.ndarray) -> pd.DataFrame:
    n = values.shape[0]
    return pd.DataFrame(
        values,
        index=[f"AY {i + 1}" for i in range(n)],
        columns=[f"Dev {j + 1}" for j in range(n)],
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
    method_label = st.selectbox("Method", list(METHODS))
    method = METHODS[method_label]
    incremental = file_form == "Incremental"

    prior = None
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

    develop_clicked = st.button(
        "Develop",
        type="primary",
        icon=":material/play_arrow:",
        width="stretch",
        disabled=not prior_ok,
    )

    # Develop stores the inputs it ran on. Results show only while the inputs still match.
    request = (
        uploaded.file_id,
        file_form,
        method,
        None if prior is None else tuple(float(x) for x in prior),
    )
    if develop_clicked:
        st.session_state["developed_request"] = request
    developed = st.session_state.get("developed_request") == request
    stale = "developed_request" in st.session_state and not developed

st.caption(f"{uploaded.name} · {n} accident years · {show_form.lower()} view")

if developed:
    result = run_method(data, incremental, method, prior=prior)
    shown = (
        result["full_triangle"]
        if show_form == "Cumulative"
        else result["full_incremental_triangle"]
    )
else:
    shown = as_form(data, incremental, show_form == "Incremental")
    if stale:
        st.info("The inputs changed. Press Develop to update the triangle.")
    else:
        st.info(
            "Press Develop in the sidebar to fill in the empty lower part of the triangle."
        )

triangle = triangle_frame(shown).map(lambda x: "" if pd.isna(x) else f"{x:,.0f}")
st.dataframe(
    triangle,
    column_config={
        column: st.column_config.TextColumn(alignment="right") for column in triangle.columns
    },
    alt="Loss triangle, by accident year and development year",
)

if developed:
    total_reserve = float(np.sum(result["reserves"]))
    total_ultimate = float(np.sum(result["ultimates"]))
    left, right = st.columns(2)
    left.metric("Total reserve", f"{total_reserve:,.0f}")
    right.metric("Total ultimate", f"{total_ultimate:,.0f}")

    st.download_button(
        "Download developed triangle (CSV)",
        data=triangle_to_csv(shown),
        file_name=f"developed_{method}_{show_form.lower()}.csv",
        mime="text/csv",
    )

    st.subheader("Ultimates and reserves")
    summary = pd.DataFrame(
        {"Ultimate": result["ultimates"], "Reserve": result["reserves"]},
        index=[f"AY {i + 1}" for i in range(n)],
    )
    summary.loc["Total"] = summary.sum()
    st.dataframe(
        summary.round(0),
        column_config={
            "Ultimate": st.column_config.NumberColumn(format="%.0f"),
            "Reserve": st.column_config.NumberColumn(format="%.0f"),
        },
        alt="Ultimate loss and reserve for each accident year, with totals",
    )

    st.subheader("Development factors")
    factors = pd.DataFrame(
        {"Factor": result["development_factor"]},
        index=[f"Dev {j + 1} to {j + 2}" for j in range(n - 1)],
    )
    st.dataframe(
        factors.round(4),
        alt="Development factor from each development year to the next",
    )
