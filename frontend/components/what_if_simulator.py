import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/evaluate"

def what_if_simulator(current_input, base_result):
    st.subheader("What-If Impact Analysis")

    st.caption(
        "This simulation re-runs the full decision pipeline with modified inputs. "
        "Every slider change triggers a fresh backend evaluation."
    )

    # =============================
    # SLIDERS
    # =============================
    col1, col2, col3 = st.columns(3)

    income_delta = col1.slider(
        "Income change (%)",
        -30, 30, 0, step=5
    )

    credit_delta = col2.slider(
        "Credit score change",
        -100, 100, 0, step=20
    )

    value_delta = col3.slider(
        "Property value change (%)",
        -30, 30, 0, step=5
    )

    # =============================
    # BUILD MODIFIED INPUT
    # =============================
    modified_input = {
        "income": round(
            max(0, current_input["income"] * (1 + income_delta / 100)), 2
        ),
        "age": current_input["age"],
        "credit_score": max(
            300,
            min(900, current_input["credit_score"] + credit_delta)
        ),
        "property_value": round(
            max(0, current_input["property_value"] * (1 + value_delta / 100)), 2
        ),
        "property_age": current_input["property_age"],
    }

    # =============================
    # SHOW MODIFIED INPUTS
    # =============================
    with st.expander("Modified Inputs Used"):
        st.json(modified_input)

    # =============================
    # CALL BACKEND
    # =============================
    with st.spinner("Re-evaluating decision with modified inputs..."):
        try:
            response = requests.post(API_URL, json=modified_input, timeout=10)
            response.raise_for_status()
            alt = response.json()
        except Exception as e:
            st.error("What-if simulation failed")
            st.code(str(e))
            return

    # =============================
    # DISPLAY RESULTS
    # =============================
    st.markdown("---")
    c1, c2 = st.columns(2)

    # -------- BASE CASE --------
    with c1:
        st.markdown("### Base Case")

        st.metric("Decision", base_result["decision"]["decision"])
        st.metric(
            "Confidence",
            f"{base_result['decision']['confidence']:.2f}"
        )
        st.metric(
            "Risk Level",
            base_result["prediction"]["risk_level"]
        )
        st.metric(
            "Affordability Ratio",
            f"{base_result['prediction']['affordability_ratio']:.2f}"
        )

    # -------- MODIFIED CASE --------
    with c2:
        st.markdown("### Modified Case")

        st.metric("Decision", alt["decision"]["decision"])
        st.metric(
            "Confidence",
            f"{alt['decision']['confidence']:.2f}"
        )
        st.metric(
            "Risk Level",
            alt["prediction"]["risk_level"]
        )
        st.metric(
            "Affordability Ratio",
            f"{alt['prediction']['affordability_ratio']:.2f}"
        )

    # =============================
    # DELTA ANALYSIS (VERY IMPORTANT)
    # =============================
    st.markdown("---")

    conf_delta = alt["decision"]["confidence"] - base_result["decision"]["confidence"]

    st.metric(
        "Confidence Change (Δ)",
        f"{conf_delta:+.2f}"
    )

    # =============================
    # STABILITY CHECK
    # =============================
    if (
        base_result["decision"]["decision"] != alt["decision"]["decision"]
        or abs(conf_delta) >= 0.05
    ):
        st.warning(
            "⚠️ Decision is sensitive to input changes. "
            "Human review recommended."
        )
    else:
        st.success(
            "✅ Decision remains stable under this variation."
        )
