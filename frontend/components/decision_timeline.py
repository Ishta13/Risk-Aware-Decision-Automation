import streamlit as st

def decision_timeline(statuses=None):
    """
    Horizontal decision timeline with colored dots
    statuses: list of tuples -> [(step_name, status)]
    status = "green", "amber", "red"
    """
    if statuses is None:
        statuses = [
            ("Input Received", "green"),
            ("Quality Checked", "green"),
            ("Confidence Aggregated", "amber"),
            ("Decision Issued", "green"),
        ]

    timeline_html = ""
    for i, (step, status) in enumerate(statuses):
        color = {"green":"#10B981","amber":"#F59E0B","red":"#EF4444"}.get(status, "#6B7280")
        timeline_html += f"<span style='color:{color};font-weight:600'>● {step}</span>"
        if i < len(statuses)-1:
            timeline_html += "<span style='margin:0 10px;'>→</span>"
    st.markdown(timeline_html, unsafe_allow_html=True)
