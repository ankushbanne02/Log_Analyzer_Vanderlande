import streamlit as st

def all_parcels_view(df):
    tbl = df[["pic"]].copy()
    tbl["registeredAt"] = df.lifeCycle.apply(lambda x: x["registeredAt"])
    st.dataframe(tbl, use_container_width=True)
