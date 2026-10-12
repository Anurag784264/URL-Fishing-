"""
PhishShield: Enterprise Phishing URL Detector & Web Threat Intelligence
Course: AI Systems and Applications (AISA) - Mini Project

Master Application Controller.
Coordinates the machine learning pipeline, feature extraction, session telemetry,
and delegates all UI presentation and styling to `ui.py`.
"""

import os
import json
import joblib
from datetime import datetime
import streamlit as st

from feature_extractor import (
    extract_url_features,
    analyze_url_risk_reasons,
    FEATURE_NAMES
)
import ui

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & ENTERPRISE THEME
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="PhishShield — URL Threat Intelligence",
    page_icon="⛨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject SaaS CSS design system tokens
ui.apply_custom_css()

# -----------------------------------------------------------------------------
# 2. STATE MANAGEMENT & SESSION TELEMETRY
# -----------------------------------------------------------------------------
if "nav_tab" not in st.session_state:
    st.session_state["nav_tab"] = "Overview"

if "scan_history" not in st.session_state:
    st.session_state["scan_history"] = []

if "session_stats" not in st.session_state:
    st.session_state["session_stats"] = {
        "total": 0,
        "phishing": 0,
        "safe": 0
    }

if "active_url_input" not in st.session_state:
    st.session_state["active_url_input"] = ""

if "last_scan_result" not in st.session_state:
    st.session_state["last_scan_result"] = None

# -----------------------------------------------------------------------------
# 3. MODEL ARTIFACT & EVALUATION METRICS LOADER
# -----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_artifact_path(filename):
    """Resolve artifact path with fallback to p1 subdirectory."""
    primary = os.path.join(BASE_DIR, filename)
    if os.path.exists(primary):
        return primary
    fallback = os.path.join(BASE_DIR, "p1", filename)
    if os.path.exists(fallback):
        return fallback
    return primary


MODEL_PATH = get_artifact_path("phishing_model.joblib")
METRICS_PATH = get_artifact_path("model_metrics.json")


@st.cache_resource
def load_detection_model():
    """Load serialized Random Forest Classifier artifact."""
    if os.path.exists(MODEL_PATH):
        try:
            return joblib.load(MODEL_PATH)
        except Exception as e:
            st.error(f"Error loading model artifact: {e}")
            return None
    return None


@st.cache_data
def load_metrics_data():
    """Load verified evaluation metrics from JSON file."""
    if os.path.exists(METRICS_PATH):
        try:
            with open(METRICS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


model = load_detection_model()
metrics_data = load_metrics_data()

# -----------------------------------------------------------------------------
# 4. TOPBAR & HORIZONTAL WEBSITE NAVIGATION
# -----------------------------------------------------------------------------
ui.render_navbar()

nav_choice = ui.render_navigation(current_selection=st.session_state.get("nav_tab", "Overview"))
st.session_state["nav_tab"] = nav_choice

# -----------------------------------------------------------------------------
# 5. SECTION 7: OVERVIEW (LANDING PAGE)
# -----------------------------------------------------------------------------
if nav_choice == "Overview":
    def switch_to_scanner():
        st.session_state["nav_tab"] = "Scanner"
        st.session_state["nav_selection"] = "Scanner"
        st.rerun()

    ui.render_overview_page(
        session_stats=st.session_state["session_stats"],
        recent_scans=st.session_state["scan_history"],
        on_scan_cta=switch_to_scanner
    )

# -----------------------------------------------------------------------------
# 6. SECTIONS 8 & 9: URL SCANNER (CORE DETECTOR)
# -----------------------------------------------------------------------------
elif nav_choice == "Scanner":
    st.markdown('<div class="ps-eyebrow">URL ANALYSIS</div>', unsafe_allow_html=True)
    st.markdown("# URL Scanner")
    st.markdown(
        '<div class="ps-lead">Analyze a link and inspect the machine-learning signals and lexical '
        'threat indicators associated with it.</div>',
        unsafe_allow_html=True
    )

    mode_tabs = st.radio(
        "Scanning Mode",
        ["Single URL", "Batch Scan"],
        horizontal=True,
        label_visibility="collapsed"
    )

    # --- SINGLE URL SCANNING ---
    if mode_tabs == "Single URL":
        samples = {
            "Select a pre-loaded test link or paste your own...": "",
            "Google (Legitimate - Search Portal)": "https://www.google.com",
            "Wikipedia (Legitimate - Knowledge Base)": "https://www.wikipedia.org",
            "Suspicious PayPal Security Verification (Phishing)": "http://paypal-security-update.account-verification.xyz/login.php?user=alert",
            "Raw IPv4 Host Banking Portal (Phishing)": "http://192.168.1.105/bank-of-america/login.htm",
            "Apple ID Multi-Subdomain Credential Lure (Phishing)": "http://secure.login.apple.id-verification.service.online-support.cc/auth",
            "Brand Cloak Redirection via '@' Symbol (Phishing)": "http://www.microsoft.com@attacker-portal.net/update/security"
        }

        col_sample, _ = st.columns([2.5, 1])
        with col_sample:
            picked_sample = st.selectbox(
                "Sample Link:",
                list(samples.keys()),
                index=0,
                label_visibility="collapsed"
            )

        if samples[picked_sample]:
            st.session_state["active_url_input"] = samples[picked_sample]

        col_inp, col_act = st.columns([4.5, 1])
        with col_inp:
            target_url = st.text_input(
                "Target URL Input",
                value=st.session_state.get("active_url_input", ""),
                placeholder="https://example.com/path",
                label_visibility="collapsed"
            )
        with col_act:
            analyze_pressed = st.button("Analyze URL", type="primary", use_container_width=True)

        if analyze_pressed:
            clean_url = target_url.strip()
            if not clean_url:
                st.warning("Please provide a valid website URL to analyze.")
            elif model is None:
                st.error("Model artifact `phishing_model.joblib` not found. Please train the model first.")
            else:
                with st.spinner("Extracting lexical features and executing model inference..."):
                    features_dict, metadata = extract_url_features(clean_url)
                    feature_vector = [[features_dict[name] for name in FEATURE_NAMES]]

                    pred = model.predict(feature_vector)[0]
                    probs = model.predict_proba(feature_vector)[0]

                    prob_phish = float(probs[0] * 100)
                    prob_legit = float(probs[1] * 100)
                    is_legit = bool(pred == 1)

                    fraud_reasons, safety_factors, risk_summary = analyze_url_risk_reasons(
                        features_dict, metadata, is_legit=is_legit
                    )

                    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    scan_record = {
                        "timestamp": timestamp_str,
                        "url": clean_url,
                        "is_legit": is_legit,
                        "verdict": "SAFE" if is_legit else "PHISHING",
                        "confidence": prob_legit if is_legit else prob_phish,
                        "prob_phish": prob_phish,
                        "prob_legit": prob_legit,
                        "risk_summary": risk_summary,
                        "features": features_dict,
                        "metadata": metadata,
                        "fraud_reasons": fraud_reasons,
                        "safety_factors": safety_factors
                    }

                    st.session_state["last_scan_result"] = scan_record
                    st.session_state["scan_history"].insert(0, scan_record)
                    st.session_state["session_stats"]["total"] += 1
                    if is_legit:
                        st.session_state["session_stats"]["safe"] += 1
                    else:
                        st.session_state["session_stats"]["phishing"] += 1

        res = st.session_state.get("last_scan_result")
        if res:
            ui.render_single_scan_report(res)

    # --- BATCH SCANNING ---
    elif mode_tabs == "Batch Scan":
        st.write("Scan a collection of target URLs simultaneously to audit security risk across multiple targets.")

        default_batch = (
            "https://www.google.com\n"
            "https://www.wikipedia.org\n"
            "http://paypal-security-update.account-verification.xyz/login.php?user=alert\n"
            "http://192.168.1.105/bank-of-america/login.htm\n"
            "http://www.microsoft.com@attacker-portal.net/update/security\n"
            "http://secure.login.apple.id-verification.service.online-support.cc/auth"
        )

        batch_raw = st.text_area(
            "URLs to Audit (one per line):",
            value=default_batch,
            height=150
        )

        col_b_act, _ = st.columns([1.5, 4])
        with col_b_act:
            batch_btn = st.button("Scan Batch", type="primary", use_container_width=True)

        if batch_btn:
            lines = [l.strip() for l in batch_raw.splitlines() if l.strip()]
            if not lines:
                st.warning("Please provide at least one URL to scan.")
            elif model is None:
                st.error("Model artifact not found.")
            else:
                with st.spinner(f"Analyzing {len(lines)} URLs in batch pipeline..."):
                    batch_results = []
                    batch_details = {}

                    for u in lines:
                        f_dict, meta = extract_url_features(u)
                        vec = [[f_dict[n] for n in FEATURE_NAMES]]
                        p = model.predict(vec)[0]
                        pb = model.predict_proba(vec)[0]
                        legit = (p == 1)

                        f_reas, s_fact, summ = analyze_url_risk_reasons(f_dict, meta, is_legit=legit)
                        batch_details[u] = (f_reas, s_fact, legit)

                        top_flag = "Clean (Verified Safe)" if legit else ", ".join([r["factor"] for r in f_reas[:2]])

                        record = {
                            "URL": u,
                            "Verdict": "SAFE" if legit else "PHISHING",
                            "Confidence": f"{pb[1]*100:.1f}%" if legit else f"{pb[0]*100:.1f}%",
                            "Primary Threat Signals": top_flag,
                            "Protocol": "HTTPS" if meta["is_https"] else "HTTP (Unencrypted)",
                            "Host Type": "IP Address" if meta["is_ip"] else "Domain"
                        }
                        batch_results.append(record)

                        st.session_state["session_stats"]["total"] += 1
                        if legit:
                            st.session_state["session_stats"]["safe"] += 1
                        else:
                            st.session_state["session_stats"]["phishing"] += 1

                    ui.render_batch_report(batch_results, batch_details, lines)

# -----------------------------------------------------------------------------
# 7. SECTION 10: URL INTELLIGENCE WORKSPACE
# -----------------------------------------------------------------------------
elif nav_choice == "Intelligence":
    ui.render_url_intelligence_page(default_url=st.session_state.get("active_url_input", ""))

# -----------------------------------------------------------------------------
# 8. SECTION 11: SCAN HISTORY
# -----------------------------------------------------------------------------
elif nav_choice == "History":
    ui.render_history_page(st.session_state.get("scan_history", []))

# -----------------------------------------------------------------------------
# 9. SECTION 12: MODEL INSIGHTS
# -----------------------------------------------------------------------------
elif nav_choice == "Model Insights":
    ui.render_model_insights_page(metrics_data, model, BASE_DIR)

# -----------------------------------------------------------------------------
# 10. CONSISTENT FOOTER
# -----------------------------------------------------------------------------
ui.render_footer()
