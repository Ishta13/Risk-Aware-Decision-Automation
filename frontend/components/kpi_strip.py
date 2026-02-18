import streamlit as st

def kpi_strip(confidence=0.0, data_quality=0.0, missing_ratio=0.0, decision_type="N/A"):
    """
    Displays a colorful horizontal KPI strip
    """
    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f"<div style='text-align:center;color:#2563EB;font-weight:600'>Model Confidence<br>{confidence*100:.1f}%</div>", unsafe_allow_html=True)
    col2.markdown(f"<div style='text-align:center;color:#10B981;font-weight:600'>Data Quality<br>{data_quality*100:.1f}%</div>", unsafe_allow_html=True)
    col3.markdown(f"<div style='text-align:center;color:#F59E0B;font-weight:600'>Missing Ratio<br>{missing_ratio*100:.1f}%</div>", unsafe_allow_html=True)
    col4.markdown(f"<div style='text-align:center;color:#8B5CF6;font-weight:600'>Decision Type<br>{decision_type}</div>", unsafe_allow_html=True)
