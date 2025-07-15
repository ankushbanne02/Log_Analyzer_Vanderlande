import streamlit as st
import pandas as pd

def all_parcels_view(df: pd.DataFrame) -> None:
    # ── 1. Build the table data ────────────────────────────────────────
    ts_col = (
        pd.to_datetime(
            df.lifeCycle.apply(lambda x: x["registeredAt"]),
            errors="coerce",
            format="mixed"
        ).dt.strftime("%H:%M:%S")
    )

    tbl = pd.DataFrame({
        "Time":        ts_col,
        "status":        df.lifeCycle.apply(lambda x: x["status"]),
        "HOSTID":      df["hostId"],
        "BARCODES":    df["barcodes"].apply(lambda lst: ", ".join(lst) if lst else "—"),
        "LOCATION":    df["location"],
        "DESTINATION": df["destination"],
    }).fillna("—")

    # ── 2. Header‑aligned filter strip ─────────────────────────────────
    col_objs = st.columns(len(tbl.columns))

    # Store each selection in a dict for later filtering
    selections = {"status": "All", "LOCATION": "All", "DESTINATION": "All"}

    for name, col in zip(tbl.columns, col_objs):
        with col:
            if name in selections:                           # columns to filter
                options = ["All"] + sorted(tbl[name].unique())
                selections[name] = st.selectbox(
                    f"{name} filter",                        # label (hidden)
                    options,
                    index=0,
                    label_visibility="collapsed",
                    key=f"{name.lower()}_filter"
                )
            else:
                st.markdown("&nbsp;", unsafe_allow_html=True)

    # ── 3. Apply the filters ───────────────────────────────────────────
    for col_name, choice in selections.items():
        if choice != "All":
            tbl = tbl[tbl[col_name] == choice]

    # ── 4. Show the filtered table ─────────────────────────────────────
    st.dataframe(tbl, use_container_width=True)

    # ── 5. (Optional) CSS tweaks: narrower boxes & smaller font ────────
    st.markdown(
        """
        <style>
        div[data-baseweb="select"] {
            width: 60%;           /* reduce width of every in‑header select */
            font-size: 0.8rem;    /* smaller text */
        }
        </style>
        """,
        unsafe_allow_html=True
    )
