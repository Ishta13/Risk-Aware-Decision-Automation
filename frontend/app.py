import streamlit as st
import requests

from components.risk_gauge import risk_gauge
from components.confidence_bar import render_confidence_bar
from components.stress_bar import render_stress_bar
from components.history import save_history, show_history
from components.kpi_strip import kpi_strip
from components.decision_timeline import decision_timeline
from components.audit_expander import audit_expander
from components.what_if_simulator import what_if_simulator

# =================================================
# CONFIG
# =================================================
st.set_page_config(
    page_title="Risk-Aware Property Decision System",
    layout="wide",
)

API_URL = "http://127.0.0.1:8000/evaluate"

# =================================================
# INR FORMATTER
# =================================================
def format_inr(value):
    value = int(value)
    s = str(value)
    if len(s) <= 3:
        return s
    last3 = s[-3:]
    rest = s[:-3]
    rest = ",".join(
        [rest[max(i - 2, 0):i] for i in range(len(rest), 0, -2)][::-1]
    )
    return rest + "," + last3

# =================================================
# GLOBAL CSS
# =================================================
# st.markdown("""
# <style>
# .stApp {
#     background: linear-gradient(135deg, #F8FAFC, #EEF2FF);
#     color: #0F172A;
#     font-family: Inter, system-ui;
# }
# section[data-testid="stSidebar"] {
#     background: #020617;
# }
# section[data-testid="stSidebar"] h1,
# section[data-testid="stSidebar"] h2,
# section[data-testid="stSidebar"] label {
#     color: #E5E7EB;
# }
# div[data-testid="stMetric"] {
#     background: #FFFFFF;
#     border-radius: 14px;
#     padding: 18px;
#     box-shadow: 0 10px 30px rgba(2,6,23,0.08);
# }
# [data-testid="stMetricValue"] {
#     color: #4F46E5;
#     font-weight: 600;
# }
# button[kind="primary"] {
#     background: linear-gradient(90deg, #4F46E5, #6366F1);
#     border-radius: 10px;
#     border: none;
# }
# pre {
#     background: #020617;
#     color: #E5E7EB;
#     border-radius: 12px;
#     padding: 14px;
# }
# </style>
# """, unsafe_allow_html=True)
# =================================================
# GLOBAL CSS (Modern Professional Theme)
# =================================================
st.markdown("""
<style>
/* Overall app background and text */
.stApp {
    background: linear-gradient(135deg, #F8FAFB 0%, #FFFFFF 100%);
    color: #1F2937;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
}

/* Sidebar background and text */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] label {
    color: #E2E8F0;
    font-weight: 600;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #FFFFFF 0%, #F9FAFB 100%);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 20px rgba(15, 23, 42, 0.08);
    border: 1px solid #E2E8F0;
    transition: all 0.3s ease;
}
[data-testid="stMetricValue"] {
    color: #2563EB;
    font-weight: 700;
    font-size: 1.8em;
}
[data-testid="stMetricLabel"] {
    color: #64748B;
    font-weight: 500;
}

/* Buttons */
button[kind="primary"] {
    background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
    border-radius: 12px;
    border: none;
    color: #FFFFFF;
    font-weight: 600;
    font-size: 1em;
    box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
    transition: all 0.3s ease;
}
button[kind="primary"]:hover {
    box-shadow: 0 8px 25px rgba(37, 99, 235, 0.4);
    transform: translateY(-2px);
}

/* Code blocks */
pre {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    color: #E2E8F0;
    border-radius: 12px;
    padding: 16px;
    border: 1px solid #334155;
}

/* Sidebar horizontal lines */
hr {
    border-top: 1px solid #334155;
    margin: 1.5rem 0;
}

/* Markdown headers */
h1 {
    color: #0F172A;
    font-weight: 700;
    font-size: 2.2em;
    margin-bottom: 0.5rem;
}
h2 {
    color: #1E293B;
    font-weight: 600;
    font-size: 1.8em;
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
}
h3 {
    color: #334155;
    font-weight: 600;
    font-size: 1.4em;
}
h4, h5, h6 {
    color: #475569;
    font-weight: 500;
}

/* Streamlit expander headers */
.stExpanderHeader {
    background-color: #F1F5F9;
    color: #1E293B;
    border-radius: 12px;
    border: 1px solid #E2E8F0;
    font-weight: 600;
}

/* Progress bars */
div[style*="background:#E8E8E8"] {
    background: #E2E8F0 !important;
}

/* Input fields */
input, select, textarea {
    border-radius: 8px !important;
    border: 2px solid #E2E8F0 !important;
    background: #FFFFFF !important;
}
input:focus, select:focus, textarea:focus {
    border: 2px solid #2563EB !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
}

/* Radio buttons for navigation */
div[role="radiogroup"] label {
    color: #6B21A8 !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    padding: 14px 18px !important;
    margin-bottom: 12px !important;
    border-radius: 10px !important;
    background: #F3E8FF !important;
    transition: all 0.3s ease !important;
    border: 1px solid transparent !important;
}

div[role="radiogroup"] label:hover {
    background: #E9D5FF !important;
    color: #7C3AED !important;
    border: 1px solid rgba(168, 85, 247, 0.3) !important;
}

div[role="radiogroup"] input[type="radio"] {
    accent-color: #A855F7 !important;
}

div[role="radiogroup"] label:has(input:checked) {
    color: #FFFFFF !important;
    background: #A855F7 !important;
    box-shadow: 0 8px 24px rgba(168, 85, 247, 0.4) !important;
    border: 1px solid rgba(168, 85, 247, 0.6) !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
}
div[role="radiogroup"] label:has(input:checked) span {
    color: #FFFFFF !important;
}

/* Page section headers with accent */
h2 {
    border-left: 4px solid #2563EB !important;
    padding-left: 16px !important;
}
            /* ========================= */

</style>
""", unsafe_allow_html=True)

# =================================================
# SESSION STATE
# =================================================
if "result" not in st.session_state:
    st.session_state.result = None

# =================================================
# SIDEBAR INPUTS
# =================================================
with st.sidebar:
    st.markdown("<h2 style='margin-top: 0; margin-bottom: 1.5rem;'>Property Inputs</h2>", unsafe_allow_html=True)
    
    st.markdown("<div style='font-weight: 600; color: #CBD5E1; margin-bottom: 0.5rem; font-size: 0.9em;'>Applicant Information</div>", unsafe_allow_html=True)
    income = st.number_input("Annual Income (₹)", min_value=0.0, value=600000.0, key="income_input")
    age = st.number_input("Applicant Age", min_value=18, value=30, key="age_input")
    credit_score = st.number_input("Credit Score", 300, 900, 720, key="credit_input")
    
    st.markdown("<div style='font-weight: 600; color: #CBD5E1; margin-top: 1.5rem; margin-bottom: 0.5rem; font-size: 0.9em;'>Property Details</div>", unsafe_allow_html=True)
    property_value = st.number_input("Property Value (₹)", min_value=0.0, value=7500000.0, key="property_value_input")
    property_age = st.number_input("Property Age (years)", min_value=0, value=10, key="property_age_input")

    st.markdown("")
    run = st.button("Evaluate Decision", use_container_width=True, key="eval_button")

# =================================================
# API CALL
# =================================================
if run:
    with st.spinner("Evaluating risk-aware decision pipeline..."):
        try:
            response = requests.post(
                API_URL,
                json={
                    "income": income,
                    "age": age,
                    "credit_score": credit_score,
                    "property_value": property_value,
                    "property_age": property_age,
                },
                timeout=10,
            )
            response.raise_for_status()
            st.session_state.result = response.json()
            save_history(st.session_state.result)

        except Exception as e:
            st.error("Backend error occurred")
            st.code(str(e))
            st.session_state.result = None

result = st.session_state.result

current_input = {
    "income": income,
    "age": age,
    "credit_score": credit_score,
    "property_value": property_value,
    "property_age": property_age,
}

# =================================================
# HERO SECTION
# =================================================
st.markdown("""
<div style="
    background: linear-gradient(135deg, #2563EB 0%, #1E40AF 100%);
    color: white;
    padding: 40px 30px;
    border-radius: 16px;
    margin-bottom: 30px;
    box-shadow: 0 8px 32px rgba(37, 99, 235, 0.2);
">
    <h1 style="margin: 0; color: white; font-size: 2.4em;">Risk-Aware Property Decision System</h1>
    <p style="margin: 8px 0 0 0; color: #E0E7FF; font-size: 1.1em;">Intelligent lending decisions powered by advanced analytics</p>
</div>
""", unsafe_allow_html=True)

# =================================================
# NAVIGATION
# =================================================
page = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Decision Details", "Audit & Explainability"],
)

# =================================================
# DASHBOARD
# =================================================
if page == "Dashboard":
    st.markdown("""
    <div style="
        border-left: 4px solid #6366F1;
        padding: 12px 16px;
        margin-bottom: 20px;
    ">
        <h3 style="margin: 0; color: #1F2937; font-size: 1.5em; font-weight: 700;">Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    if not result:
        st.markdown("""
        <div style="
            text-align: center;
            padding: 60px 20px;
            color: #64748B;
        ">
            <p style="font-size: 1.1em; margin-bottom: 10px;">No evaluation results yet</p>
            <p style="font-size: 0.95em;">Enter applicant information in the sidebar and click "Evaluate Decision" to begin</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        decision = result["decision"]["decision"]
        decision_color = "#10B981" if "Approve" in decision else ("#F59E0B" if "Review" in decision else "#F97316")

        # Decision Badge
        st.markdown(f"""
        <div style="
            background: {decision_color};
            color: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 30px;
            font-size: 1.3em;
            font-weight: 700;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        ">
            {decision}
        </div>
        """, unsafe_allow_html=True)

        # KPI Strip
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #E0E7FF 0%, #F0F4FF 100%); padding: 20px; border-radius: 12px; text-align: center; border: 1px solid #C7D2FE;">
                <div style="color: #64748B; font-size: 0.9em; font-weight: 600; margin-bottom: 8px;">Model Confidence</div>
                <div style="color: #2563EB; font-size: 1.8em; font-weight: 700;">""" + f"{result['decision']['confidence']:.0%}" + """</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #DCFCE7 0%, #F0FDF4 100%); padding: 20px; border-radius: 12px; text-align: center; border: 1px solid #BBF7D0;">
                <div style="color: #64748B; font-size: 0.9em; font-weight: 600; margin-bottom: 8px;">Data Quality</div>
                <div style="color: #10B981; font-size: 1.8em; font-weight: 700;">""" + f"{result['decision']['data_quality_score']:.0%}" + """</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #FEF3C7 0%, #FFFBEB 100%); padding: 20px; border-radius: 12px; text-align: center; border: 1px solid #FCD34D;">
                <div style="color: #64748B; font-size: 0.9em; font-weight: 600; margin-bottom: 8px;">Missing Data</div>
                <div style="color: #F59E0B; font-size: 1.8em; font-weight: 700;">""" + f"{result['decision']['missing_ratio']:.0%}" + """</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #EDE9FE 0%, #F5F3FF 100%); padding: 20px; border-radius: 12px; text-align: center; border: 1px solid #DDD6FE;">
                <div style="color: #64748B; font-size: 0.9em; font-weight: 600; margin-bottom: 8px;">Risk Level</div>
                <div style="color: #7C3AED; font-size: 1.8em; font-weight: 700;">""" + result['prediction']['risk_level'] + """</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")
        st.divider()
        st.markdown("")

        # Key Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Predicted Property Price", f"₹{format_inr(result['prediction']['predicted_price'])}")
        col2.metric("Affordability Ratio", f"{result['prediction']['affordability_ratio']:.2f}x")
        col3.metric("Final Confidence Score", f"{result['decision']['confidence']:.2f}")

        st.markdown("")
        st.divider()
        st.markdown("")

        # Visual Indicators
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<h4 style='margin-bottom: 1rem;'>Confidence Assessment</h4>", unsafe_allow_html=True)
            render_confidence_bar("Final Confidence", result["decision"]["confidence"])
        with col2:
            st.markdown("<h4 style='margin-bottom: 1rem;'>Financial Stress Analysis</h4>", unsafe_allow_html=True)
            render_stress_bar(result["prediction"]["affordability_ratio"])

        st.markdown("")
        st.divider()
        st.markdown("")

        # Risk Assessment
        st.markdown("<h4 style='margin-bottom: 1rem;'>Risk Classification</h4>", unsafe_allow_html=True)
        risk_gauge(result["prediction"]["risk_level"])

        st.markdown("")
        st.divider()
        st.markdown("")

        # Decision Timeline
        st.markdown("<h4 style='margin-bottom: 1rem;'>Decision Process</h4>", unsafe_allow_html=True)
        decision_timeline([
            ("Input Received", "green"),
            ("Quality Checked", "green" if result["decision"]["data_quality_score"] > 0.7 else "red"),
            ("Confidence Aggregated", "green" if result["decision"]["confidence"] > 0.7 else "amber"),
            ("Decision Issued", "green"),
        ])

        st.markdown("")
        st.divider()
        st.markdown("")

        # Recent Decisions
        st.markdown("<h4 style='margin-bottom: 1rem;'>Recent Decisions</h4>", unsafe_allow_html=True)
        show_history()

        st.markdown("")
        st.divider()
        st.markdown("")

        # Scenario Analysis
        st.markdown("<h4 style='margin-bottom: 1rem;'>Scenario Analysis</h4>", unsafe_allow_html=True)
        what_if_simulator(current_input, result)

# =================================================
# DECISION DETAILS
# =================================================
elif page == "Decision Details":
    st.markdown("""
    <div style="
        border-left: 4px solid #7C3AED;
        padding: 12px 16px;
        margin-bottom: 20px;
    ">
        <h3 style="margin: 0; color: #1F2937; font-size: 1.5em; font-weight: 700;">Decision Details</h3>
    </div>
    """, unsafe_allow_html=True)

    if not result:
        st.info("No decision available. Run an evaluation first.")
    else:
        trace = result["decision"]["trace"]

        st.markdown("<h4 style='margin-bottom: 1.5rem;'>Confidence Metrics</h4>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            render_confidence_bar("Model Confidence", trace.get("model_confidence", 0.8))
        with col2:
            render_confidence_bar("Data Quality", result["decision"]["data_quality_score"])
        with col3:
            render_confidence_bar("Final Confidence", result["decision"]["confidence"])

        st.markdown("")
        st.divider()
        st.markdown("")
        
        audit_expander({
            "summary": result["decision"]["explanation"]["summary"],
            "full_trace": trace,
        })

# =================================================
# AUDIT & EXPLAINABILITY
# =================================================
elif page == "Audit & Explainability":
    st.markdown("""
    <div style="
        border-left: 4px solid #A855F7;
        padding: 12px 16px;
        margin-bottom: 20px;
    ">
        <h3 style="margin: 0; color: #1F2937; font-size: 1.5em; font-weight: 700;">Audit & Explainability</h3>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")

    if not result:
        st.info("Nothing to audit yet. Run an evaluation first.")
    else:
        with st.expander("Full Decision Trace", expanded=True):
            st.json(result["decision"]["trace"])

        st.divider()

        # HUMAN READABLE SUMMARY
        st.subheader(" What Does This Mean?")
        
        trace = result["decision"]["trace"]
        explanation = trace.get("explanation", [])
        decision = result["decision"]["decision"]
        signals = trace.get("signals", {})
        
        # Summary explanation
        summary_text = f"""
        ### Decision: **{decision}**
        
        The system analyzed the applicant's information and made a **{decision}** decision.
        
        
        """
        
        if explanation:
            for reason in explanation:
                summary_text += f"\n- {reason}"
        
        summary_text += f"""
        
        **Confidence Levels:**
        - Model Confidence: {signals.get('model_confidence', 0):.0%}
        - Data Quality: {signals.get('data_quality_score', 0):.0%}
        - Final Decision Confidence: {signals.get('final_confidence', 0):.0%}
        
        This means the system is {int(signals.get('final_confidence', 0) * 100)}% confident in this decision based on the applicant's data.
        """
        
        st.markdown(summary_text)
