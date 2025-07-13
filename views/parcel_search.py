import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

def parcel_search_view(df):
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
                
                # Parse event data
                ev = pd.DataFrame(parcel.events)
                ev["ts"] = pd.to_datetime(ev.ts)
                ev = ev.sort_values("ts")

                # Calculate duration to next event
                lifecycle = parcel.lifeCycle
                close_time = pd.to_datetime(lifecycle.get("closedAt") or datetime.now())
                ev["finish"] = ev["ts"].shift(-1).fillna(close_time)
                ev["duration_s"] = (ev["finish"] - ev["ts"]).dt.total_seconds()

                # Add station column (dummy or real if it exists)
                
                # ── UI: event table ──────────────────────────────────────
                st.subheader("Event log")
                st.dataframe(
                    ev[["type", "ts", "duration_s"]],
                    use_container_width=True,
                    hide_index=True,
                )

                # ── Timeline ─────────────────────────────────────────────
                fig = px.timeline(
                    ev,
                    x_start="ts",
                    x_end="finish",
                    y=["PIC"] * len(ev),
                    color="type",
                    hover_data=["type", "ts", "duration_s"]
                )
                

        except Exception as e:
            st.error("PIC must be an integer")
