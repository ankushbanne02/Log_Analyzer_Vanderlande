import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

def parcel_search_view(df):
    search_mode = st.radio("Search by", ["Host ID", "Barcode"], horizontal=True)
    search_input = st.text_input(f"Enter {search_mode}")
    if not search_input:
        return

    try:
        if search_mode == "Host ID":
            result = df[df.hostId == search_input]
        elif search_mode == "Barcode":
            result = df[df.barcodes.apply(lambda barcodes: search_input in barcodes)]

        if result.empty:
            st.warning(f"{search_mode} not found.")
            return

        for idx, parcel in result.iterrows():
            # Calculate Box Volume if dimensions exist
            length = getattr(parcel, "length", None)
            width  = getattr(parcel, "width", None)
            height = getattr(parcel, "height", None)

            box_volume = None
            if all(isinstance(x, (int, float)) for x in [length, width, height]):
                box_volume = length * width * height

            # Combine parcel details into a dictionary
            parcel_summary = {
                "PIC": parcel.pic,
                "Host ID": parcel.hostId,
                "Barcodes": parcel.barcodes,
                "Location": parcel.location,
                "Destination": parcel.destination,
                "Length (cm)": length if length else "—",
                "Width (cm)": width if width else "—",
                "Height (cm)": height if height else "—",
                "Box Volume (cm³)": round(box_volume, 2) if box_volume else "—",
                "Lifecycle": parcel.lifeCycle,
                "Barcode Error": parcel.barcodeErr,
            }

            st.subheader("📦 Parcel Information")
            st.json(parcel_summary)

            # ── Event timeline ──
            ev = pd.DataFrame(parcel.events)
            ev["ts"] = pd.to_datetime(ev.ts)
            ev = ev.sort_values("ts")
            close_time = pd.to_datetime(parcel.lifeCycle.get("closedAt") or datetime.now())
            ev["finish"] = ev["ts"].shift(-1).fillna(close_time)
            ev["duration_s"] = (ev["finish"] - ev["ts"]).dt.total_seconds()
            ev["time"] = ev["ts"].dt.strftime("%H:%M:%S")

            st.subheader("📋 Event Log")
            st.dataframe(
                ev[["time", "type", "duration_s"]].rename(columns={
                    "time": "Time",
                    "type": "Type",
                    "duration_s": "Duration (s)"
                }),
                use_container_width=True,
                hide_index=True,
            )

            fig = px.timeline(
                ev,
                x_start="ts",
                x_end="finish",
                y=["Parcel"] * len(ev),
                color="type",
                hover_data=["type", "ts", "duration_s"]
            )
            

    except Exception as e:
        st.error(f"Error: {e}")
