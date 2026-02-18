import streamlit as st

def risk_gauge(risk: str):
    colors = {
        "Low": "#4CAF50",
        "Medium": "#FF9800",
        "High": "#F44336"
    }
    bg_colors = {
        "Low": "#E8F5E9",
        "Medium": "#FFF3E0",
        "High": "#FFEBEE"
    }

    st.markdown(f"""
    <div style="
        margin-top:1rem;
        padding:1rem;
        border-radius:12px;
        background:{bg_colors.get(risk, "#F5F5F5")};
        border:2px solid {colors.get(risk, "#999999")};
    ">
        <strong style="color:#1A1A1A;">Risk Assessment:</strong>
        <span style="color:{colors.get(risk)};font-weight:600;">
            {risk}
        </span>
    </div>
    """, unsafe_allow_html=True)
