import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from hlc_parser import parse_log   # ← import the parser module

st.set_page_config(page_title="Vanderlande Parcel Dashboard", layout="wide")
st.title("📦 Vanderlande Parcel Dashboard")

uploaded = st.file_uploader("Upload raw HLC log (.txt)", type="txt")

if not uploaded:
    st.info("Upload a raw HLC .txt log to begin.")
    st.stop()

text = uploaded.read().decode("utf-8")
with st.spinner("Parsing log…"):
    lifecycles = parse_log(text)
    df = pd.DataFrame(lifecycles)

# ── KPI cards ------------------------------------------------------
total = len(df)
sorted_cnt = (df.lifeCycle.apply(lambda x: x["status"]) == "sorted").sum()
dereg_cnt  = (df.lifeCycle.apply(lambda x: x["status"]) == "deregistered").sum()
barcode_err= df.barcodeErr.sum()

# average cycle + tph
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
    st.metric("Throughput/hr", f"{tph:.1f}")

st.divider()

# ── Header tabs -----------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["🔍 Parcel Search", "📋 All Parcels", "✅ Sorted", "🚫 Deregistered"]
)

# 1. Parcel search
with tab1:
    pic_text = st.text_input("Enter PIC number")
    if pic_text:
        try:
            pic = int(pic_text)
            row = df[df.pic == pic]
            if row.empty:
                st.warning("PIC not found")
            else:
                parcel = row.iloc[0]
                st.json(parcel.lifeCycle)
                ev = pd.DataFrame(parcel.events)
                ev["ts"] = pd.to_datetime(ev.ts)
                st.dataframe(ev, use_container_width=True)
                fig = px.timeline(ev, x_start="ts", x_end="ts",
                                  y=["PIC"]*len(ev), color="type")
                fig.update_yaxes(visible=False); fig.update_layout(height=250)
                st.plotly_chart(fig, use_container_width=True)
        except:
            st.error("PIC must be integer")

# 2. All parcels
with tab2:
    tbl = df[["pic"]].copy()
    tbl["registeredAt"] = df.lifeCycle.apply(lambda x: x["registeredAt"])
    st.dataframe(tbl, use_container_width=True)

# 3. Sorted
with tab3:
    good = df[df.lifeCycle.apply(lambda x: x["status"]) == "sorted"]
    st.dataframe(good[["pic", "barcodeErr"]], use_container_width=True)

# 4. Deregistered
with tab4:
    bad = df[df.lifeCycle.apply(lambda x: x["status"]) == "deregistered"]
    st.dataframe(bad[["pic", "barcodeErr"]], use_container_width=True)
