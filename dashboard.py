import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from hlc_parser import parse_log


from views.parcel_search import parcel_search_view
from views.all_parcels import all_parcels_view
from views.sorted_parcels import sorted_parcels_view
from views.deregistered_parcels import deregistered_parcels_view

st.set_page_config(page_title="Vanderlande Parcel Dashboard", layout="wide")
st.title("📦 Vanderlande Parcel Dashboard")

uploaded = st.file_uploader("Upload raw Log File in .txt format", type="txt")

if not uploaded:
    st.info("up.")
    st.stop()

text = uploaded.read().decode("utf-8")
with st.spinner("Parsing log…"):
    lifecycles = parse_log(text)
    df = pd.DataFrame(lifecycles)


total = len(df)
sorted_cnt = (df.lifeCycle.apply(lambda x: x["status"]) == "sorted").sum()
dereg_cnt  = (df.lifeCycle.apply(lambda x: x["status"]) == "deregistered").sum()
barcode_err= df.barcodeErr.sum()

def cycle_s(lc):
    if lc["registeredAt"] and lc["closedAt"]:
        return (datetime.fromisoformat(lc["closedAt"]) -
                datetime.fromisoformat(lc["registeredAt"])).total_seconds()
    return None

cycle_vals = df.lifeCycle.map(cycle_s).dropna()
avg_cycle = sum(cycle_vals)/len(cycle_vals) if len(cycle_vals) else 0

if total:
    first_ts = min(datetime.fromisoformat(l["registeredAt"]) for l in df.lifeCycle)
    last_ts  = max(datetime.fromisoformat(l["closedAt"] or l["registeredAt"]) for l in df.lifeCycle)
    tph = total / ((last_ts - first_ts).total_seconds()/3600 or 1)
else:
    tph = 0


c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Total Parcels", total)
    st.metric("% Sorted", f"{sorted_cnt/total*100:.1f}%" if total else "0%")
with c2:
    st.metric("% Barcode Err", f"{barcode_err/total*100:.1f}%" if total else "0%")
    st.metric("% Deregistered", f"{dereg_cnt/total*100:.1f}%" if total else "0%")
with c3:
    st.metric("Avg Cycle (s)", f"{avg_cycle:.1f}")
    

st.divider()


tab1, tab2, tab3, tab4 = st.tabs(
    ["🔍 Parcel Search", "📋 All Parcels", "✅ Sorted", "🚫 Deregistered"]
)

with tab1:
    parcel_search_view(df)
with tab2:
    all_parcels_view(df)
with tab3:
    sorted_parcels_view(df)
with tab4:
    deregistered_parcels_view(df)
