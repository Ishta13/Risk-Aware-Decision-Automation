import streamlit as st

def save_history(result):
    if "history" not in st.session_state:
        st.session_state.history = []

    st.session_state.history.insert(0, result)

def show_history():
    if "history" not in st.session_state or not st.session_state.history:
        st.info("No previous decisions")
        return

    for h in st.session_state.history[:5]:
        st.markdown(f"""
        <div style="padding:0.75rem;border-bottom:1px solid #E5E7EB;">
            <strong>Price:</strong> ₹{h['prediction']['predicted_price']:,.0f}<br>
            <strong>Risk:</strong> {h['prediction']['risk_level']}<br>
            <strong>Decision:</strong> {h['decision']['decision']}
        </div>
        """, unsafe_allow_html=True)
