import streamlit as st

def audit_expander(audit_data):
    """
    Shows summarized audit with expandable full trace.
    audit_data: dict with keys 'summary' and 'full_trace'
    """
    st.subheader("Audit Summary")
    st.write(audit_data.get("summary", "No summary available"))

    with st.expander("View Full Audit Trace"):
        st.json(audit_data.get("full_trace", {}))
