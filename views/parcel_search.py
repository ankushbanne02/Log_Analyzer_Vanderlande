import streamlit as st
import pandas as pd
import plotly.express as px

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
                ev = pd.DataFrame(parcel.events)
                ev["ts"] = pd.to_datetime(ev.ts)
                st.dataframe(ev, use_container_width=True)
                fig = px.timeline(ev, x_start="ts", x_end="ts",
                                  y=["PIC"]*len(ev), color="type")
                fig.update_yaxes(visible=False)
                fig.update_layout(height=250)
                st.plotly_chart(fig, use_container_width=True)
        except:
            st.error("PIC must be integer")
