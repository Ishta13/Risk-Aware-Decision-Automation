import streamlit as st

def render_stress_bar(affordability_ratio: float):
    st.subheader("Financial Stress Level")

    stress = min(affordability_ratio / 10, 1.0)
    st.progress(stress)

    if affordability_ratio <= 5:
        st.success("Low financial stress")
    elif affordability_ratio <= 7:
        st.warning("Moderate financial stress")
    else:
        st.error("High financial stress – risky applicant")


    