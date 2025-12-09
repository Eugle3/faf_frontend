import json
from typing import Any, Dict, List

import pandas as pd
import streamlit as st
import requests

st.set_page_config(page_title="Route Dashboard", layout="wide")
API_BASE_URL = "http://localhost:8000"

if "entered" not in st.session_state:
    st.session_state.entered = False
if "recommendations" not in st.session_state:
    st.session_state.recommendations: List[Dict[str, Any]] = []
if "gpx_recommendations" not in st.session_state:
    st.session_state.gpx_recommendations: List[Dict[str, Any]] = []

st.markdown(
    """
    <style>
    /* FAF Logo - Fixed Position */
    .faf-logo {
        position: fixed;
        top: 16px;
        left: 24px;
        font-family: "Impact", "Anton", "Arial Black", sans-serif;
        font-size: 44px;
        font-style: italic;
        font-weight: 900;
        letter-spacing: 1px;
        color: #0F1826;
        padding: 8px 14px;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.95);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        z-index: 9999;
        transition: all 0.3s ease;
    }

    /* Header Transparency */
    header[data-testid="stHeader"] {
        background: transparent;
        box-shadow: none;
    }
    header[data-testid="stHeader"] > div {
        background: transparent;
    }

    /* Hero Section - Modern Design */
    .hero {
        background: linear-gradient(135deg, #B06CFF 0%, #FF5C7A 100%);
        padding: 160px 40px 120px;
        text-align: center;
        margin-bottom: 0;
        width: 100vw;
        margin-left: calc(-50vw + 50%);
        position: relative;
        overflow: hidden;
    }
    .hero::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('https://images.unsplash.com/photo-1541625602330-2277a4c46182?w=1600') center/cover;
        opacity: 0.15;
        z-index: 0;
    }
    .hero-content {
        position: relative;
        z-index: 1;
    }
    .hero h1 {
        font-size: 120px;
        font-weight: 900;
        letter-spacing: -4px;
        margin: 0;
        color: #FFFFFF;
        text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        font-family: "Impact", "Arial Black", sans-serif;
    }
    .hero h2 {
        font-size: 32px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 16px;
        color: #FFFFFF;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }
    .hero p {
        font-size: 18px;
        color: rgba(255, 255, 255, 0.95);
        max-width: 600px;
        margin: 0 auto 40px;
        line-height: 1.6;
    }

    /* Feature Cards Section */
    .features-section {
        background: #F5F5F7;
        padding: 80px 40px;
        width: 100vw;
        margin-left: calc(-50vw + 50%);
        margin-bottom: 40px;
    }
    .features-title {
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        color: #0F1826;
        margin-bottom: 50px;
    }
    .feature-card {
        background: white;
        padding: 32px;
        border-radius: 16px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
        margin-bottom: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(176, 108, 255, 0.15);
    }
    .feature-icon {
        font-size: 48px;
        margin-bottom: 16px;
    }
    .feature-title {
        font-size: 22px;
        font-weight: 700;
        color: #0F1826;
        margin-bottom: 12px;
    }
    .feature-desc {
        font-size: 15px;
        color: #4F6844;
        line-height: 1.6;
    }

    /* Dashboard Section Headers */
    .section-header {
        background: linear-gradient(90deg, #4F6844 0%, #B06CFF 100%);
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        margin-bottom: 24px;
        font-weight: 700;
        font-size: 20px;
    }

    /* Card Styling */
    div[data-testid="stMetric"] {
        background: white;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #B06CFF;
    }

    /* Match input heights */
    div[data-testid="stNumberInput"] {
        min-height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    /* Button Styling */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(176, 108, 255, 0.3);
    }

    /* Dividers */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #C8C9CE, transparent);
        margin: 40px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="faf-logo">FAF</div>', unsafe_allow_html=True)

if not st.session_state.entered:
    # Hero Section
    st.markdown(
        """
        <div class="hero">
            <div class="hero-content">
                <h1>FAF</h1>
                <h2>Fast As Fuck</h2>
                <p>Discover epic cycling routes powered by AI. Find scenic paths, challenging climbs, and hidden gems tailored to your riding style.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # CTA Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚴 Start Discovering Routes", use_container_width=True, type="primary"):
            st.session_state.entered = True
            st.rerun()

    # Features Section
    st.markdown(
        """
        <div class="features-section">
            <div class="features-title">How It Works</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    feat1, feat2, feat3 = st.columns(3, gap="large")

    with feat1:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🗺️</div>
                <div class="feature-title">Upload or Describe</div>
                <div class="feature-desc">Share your favorite GPX file or describe your ideal ride preferences.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with feat2:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <div class="feature-title">AI-Powered Matching</div>
                <div class="feature-desc">Our algorithm finds routes with similar terrain, distance, and scenic quality.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with feat3:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🚴</div>
                <div class="feature-title">Ride & Enjoy</div>
                <div class="feature-desc">Get personalized recommendations and explore new cycling adventures.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.stop()

st.markdown('<div class="section-header">🗺️ Route Discovery Dashboard</div>', unsafe_allow_html=True)

# Example payload matching the API request body the user showed.
default_features = {
    "features": {
        "distance_m": 25000,
        "duration_s": 5400,
        "ascent_m": 320,
        "descent_m": 320,
        "steps": 40,
        "turns": 55,
        "Cycleway": 0.2,
        "Turn_Density": 0.0022,
        "on_road": 0.6,
        "off_road": 0.4,
        "Gravel_Tracks": 0.1,
        "Paved_Paths": 0.3,
        "Other": 0.05,
        "Unknown Surface": 0.0,
        "Paved_Road": 0.4,
        "Pedestrian": 0.0,
        "Unknown_Way": 0.0,
        "Cycle Track": 0.15,
        "Main Road": 0.0,
        "Steep Section": 0.0,
        "Moderate Section": 0.0,
        "Flat Section": 0.0,
        "Downhill Section": 0.0,
        "Steep Downhill Section": 0.0,
    }
}

def format_duration(seconds: float) -> str:
    minutes, sec = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if sec or not parts:
        parts.append(f"{sec}s")
    return " ".join(parts)


def upload_gpx_to_api(file) -> tuple[bool, str, Dict[str, Any] | None]:
    files = {"file": (file.name, file.getvalue(), "application/gpx+xml")}
    try:
        resp = requests.post(f"{API_BASE_URL}/recommend-from-gpx", files=files, timeout=30)
    except Exception as exc:  # noqa: BLE001
        return False, f"Request failed: {exc}", None

    if resp.status_code != 200:
        try:
            detail = resp.json().get("detail")
        except Exception:  # noqa: BLE001
            detail = resp.text
        return False, f"API error {resp.status_code}: {detail}", None

    try:
        data = resp.json()
    except Exception:  # noqa: BLE001
        return False, "Invalid JSON response from API.", None

    if not isinstance(data, list):
        return False, "Unexpected response format from API.", None

    return True, "Recommendations ready.", data


def fetch_recommendations(features: Dict[str, Any], n_recs: int) -> tuple[bool, str, List[Dict[str, Any]] | None]:
    payload = {"features": features, "n_recommendations": n_recs}
    try:
        resp = requests.post(f"{API_BASE_URL}/recommend", json=payload, timeout=30)
    except Exception as exc:  # noqa: BLE001
        return False, f"Request failed: {exc}", None

    if resp.status_code != 200:
        try:
            detail = resp.json().get("detail")
        except Exception:  # noqa: BLE001
            detail = resp.text
        return False, f"API error {resp.status_code}: {detail}", None

    try:
        data = resp.json()
    except Exception:  # noqa: BLE001
        return False, "Invalid JSON response from API.", None

    if not isinstance(data, list):
        return False, "Unexpected response format from API.", None

    return True, "Recommendations loaded.", data


header = st.container()
with header:
    route_col, count_col = st.columns(2)
    uploaded_gpx = route_col.file_uploader(
        "Upload a GPX file",
        type=["gpx"],
        help="Choose a .gpx file to send to the backend.",
    )
    if uploaded_gpx:
        st.caption(f"Selected file: {uploaded_gpx.name} ({len(uploaded_gpx.getvalue())} bytes)")
        if st.button("Send GPX to backend", use_container_width=True):
            ok, msg, data = upload_gpx_to_api(uploaded_gpx)
            if ok:
                st.success(msg)
                st.session_state.gpx_recommendations = data
            else:
                st.error(msg)

    n_recs = count_col.number_input(
        "Number of recommendations",
        min_value=1,
        max_value=10,
        value=5,
        step=1,
    )
    if st.button("Get recommendations", use_container_width=True):
        ok, msg, data = fetch_recommendations(default_features["features"], n_recs)
        if ok and data is not None:
            st.session_state.recommendations = data
            st.success(msg)
        else:
            st.error(msg)

st.divider()

sidebar, map_area = st.columns([1, 2], gap="large")

with sidebar:
    st.markdown('<div class="section-header">📍 Recommended Routes</div>', unsafe_allow_html=True)
    route_names = [rec["route_name"] for rec in st.session_state.recommendations][: n_recs or 5]
    selected_route = st.selectbox("Route", route_names, index=0 if route_names else None)

    selected = next((rec for rec in st.session_state.recommendations if rec["route_name"] == selected_route), None)

    st.markdown("### 📊 Route Metrics")
    if selected:
        st.metric("Distance (m)", f"{selected['distance_m']:.0f}")
        st.metric("Ascent (m)", f"{selected['ascent_m']:.0f}")
        st.metric("Duration", format_duration(selected["duration_s"]))
        st.metric("Turn Density", f"{selected['turn_density']:.2f}")
        st.metric("Similarity Score", f"{selected['similarity_score']:.4f}")
    else:
        st.info("Select a route to view KPIs.")

with map_area:
    st.markdown('<div class="section-header">🗺️ Interactive Map</div>', unsafe_allow_html=True)
    # Example data to keep the map from being empty
    sample_map = pd.DataFrame(
        {
            "lat": [51.5074, 51.515, 51.5033],
            "lon": [-0.1278, -0.09, -0.1195],
        }
    )
    st.map(sample_map, size=70)
    if selected_route:
        st.caption(f"Placeholder geometry for: {selected_route}")
    else:
        st.caption("Select a route to label the map view.")

st.divider()
with st.expander("Raw recommendations"):
    st.json(st.session_state.recommendations or {"info": "No recommendations fetched yet."})
