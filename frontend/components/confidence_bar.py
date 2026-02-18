import streamlit as st

def render_confidence_bar(label: str, value: float):
    percent = int(value * 100)

    if percent >= 85:
        color = "#4CAF50"  # green
    elif percent >= 60:
        color = "#FF9800"  # orange
    else:
        color = "#F44336"  # red

    st.markdown(f"""
    <div style="margin-bottom:1rem;">
        <div style="font-size:0.85rem;color:#333333;">{label}</div>
        <div style="background:#E0E0E0;height:10px;border-radius:8px;overflow:hidden;">
            <div style="width:{percent}%;background:{color};height:100%;"></div>
        </div>
        <div style="font-size:0.75rem;color:#666666;">{percent}%</div>
    </div>
    """, unsafe_allow_html=True)
