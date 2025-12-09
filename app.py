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

    /* Route Recommendations Title - Top Center */
    .route-recommendations-title {
        text-align: center;
        font-family: "Impact", "Arial Black", sans-serif;
        font-size: 42px;
        font-weight: 900;
        letter-spacing: 1.5px;
        color: #0F1826;
        padding: 48px 0 48px 0;
        text-transform: uppercase;
        margin: 0;
    }

    /* Header Transparency */
    header[data-testid="stHeader"] {
        background: transparent;
        box-shadow: none;
    }
    header[data-testid="stHeader"] > div {
        background: transparent;
    }

    /* Hero Section - Clean Rapha Style */
    .hero-text-section {
        background: #FFFFFF;
        padding: 120px 60px 80px;
        text-align: center;
        width: 100vw;
        margin-left: calc(-50vw + 50%);
    }
    .hero-text-section h1 {
        font-size: 72px;
        font-weight: 900;
        letter-spacing: -2px;
        margin: 0 0 24px 0;
        color: #0F1826;
        font-family: "Impact", "Arial Black", sans-serif;
        text-transform: uppercase;
    }
    .hero-text-section h2 {
        font-size: 22px;
        font-weight: 400;
        margin: 0 auto 40px;
        color: #0F1826;
        font-style: italic;
        max-width: 600px;
        letter-spacing: 0.3px;
    }

    /* Hero CTA Links */
    .hero-cta-section {
        background: #FFFFFF;
        text-align: center;
        margin: 0;
        padding: 0 0 60px 0;
        width: 100vw;
        margin-left: calc(-50vw + 50%);
    }
    .hero-cta-section a {
        text-decoration: underline;
        color: #0F1826;
        font-weight: 600;
        font-size: 15px;
        letter-spacing: 0.5px;
        transition: color 0.2s ease;
        margin: 0 20px;
    }
    .hero-cta-section a:hover {
        color: #B06CFF;
    }

    /* Hero Image Section */
    .hero-image-section {
        width: 100vw;
        margin-left: calc(-50vw + 50%);
        margin-bottom: 60px;
        margin-top: 0;
        background: #FFFFFF;
        padding-bottom: 40px;
    }
    .hero-image-section img {
        width: 100%;
        height: auto;
        display: block;
        object-fit: cover;
        max-height: 65vh;
    }
    /* Override Streamlit image container */
    .hero-image-section [data-testid="stImage"] {
        width: 100%;
    }

    /* Feature Cards Section - Minimal Design */
    .features-section {
        background: #FFFFFF;
        padding: 100px 40px;
        width: 100vw;
        margin-left: calc(-50vw + 50%);
        margin-bottom: 60px;
        border-top: 1px solid #E5E5E5;
    }
    .features-title {
        text-align: center;
        font-size: 36px;
        font-weight: 700;
        color: #0F1826;
        margin-bottom: 70px;
        letter-spacing: -1px;
    }
    .feature-card {
        background: transparent;
        padding: 24px 16px;
        border-radius: 0;
        margin-bottom: 20px;
        transition: transform 0.2s ease;
    }
    .feature-card:hover {
        transform: translateY(-2px);
    }
    .feature-title {
        font-size: 18px;
        font-weight: 700;
        color: #0F1826;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 14px;
    }
    .feature-desc {
        font-size: 15px;
        color: #666666;
        line-height: 1.7;
        font-weight: 400;
    }

    /* Dashboard Section Headers */
    .section-header {
        background: #B06CFF;
        color: white;
        padding: 18px 28px;
        border-radius: 12px;
        margin-bottom: 28px;
        font-weight: 800;
        font-size: 20px;
        letter-spacing: 0.3px;
    }
    .section-header-green {
        background: #4F6844;
        color: white;
        padding: 18px 28px;
        border-radius: 12px;
        margin-bottom: 28px;
        font-weight: 800;
        font-size: 20px;
        letter-spacing: 0.3px;
    }

    /* Card Styling */
    div[data-testid="stMetric"] {
        background: white;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #B06CFF;
    }

    /* Align upload and number input to same height and size */
    div[data-testid="stFileUploader"],
    div[data-testid="stNumberInput"] {
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }

    /* Make the inner containers the same height */
    div[data-testid="stFileUploader"] section,
    div[data-testid="stNumberInput"] > div > div {
        min-height: 100px !important;
        height: 100px !important;
    }

    /* Labels styling */
    div[data-testid="stFileUploader"] label,
    div[data-testid="stNumberInput"] label {
        font-weight: 800 !important;
        font-size: 18px !important;
        color: #0F1826 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px !important;
    }

    /* Make number input controls thinner */
    div[data-testid="stNumberInput"] button {
        width: 32px !important;
        min-width: 32px !important;
        padding: 4px !important;
    }

    /* Fix the file uploader height */
    div[data-testid="stFileUploader"] section > div {
        min-height: 100px !important;
    }

    /* Button Styling - Compact and Bold */
    .stButton > button {
        border-radius: 10px;
        font-weight: 700;
        transition: all 0.3s ease;
        font-size: 18px !important;
        padding: 14px 28px !important;
        min-height: 52px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(176, 108, 255, 0.3);
    }

    /* Add spacing around main button */
    .stButton {
        margin: 24px 0;
    }

    /* Map Rounded Corners */
    [data-testid="stMap"] {
        border-radius: 16px;
        overflow: hidden;
    }
    [data-testid="stMap"] > div {
        border-radius: 16px;
    }

    /* Expander Styling */
    [data-testid="stExpander"] {
        border-radius: 12px;
        border: 2px solid #B06CFF;
        background: white;
    }
    [data-testid="stExpander"] summary {
        font-weight: 700;
        font-size: 18px;
        padding: 16px 20px;
        color: #B06CFF;
    }
    [data-testid="stExpander"] summary:hover {
        color: #FF5C7A;
    }

    /* Dividers */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #C8C9CE, transparent);
        margin: 40px 0;
    }

    /* Dark Mode Support */
    @media (prefers-color-scheme: dark) {
        /* Overall page background */
        .stApp {
            background-color: #0F1826;
        }

        /* Hero sections */
        .hero-text-section {
            background: #0F1826;
        }
        .hero-text-section h1,
        .hero-text-section h2 {
            color: #FFFFFF;
        }
        .hero-cta-section {
            background: #0F1826;
        }
        .hero-cta-section a {
            color: #FFFFFF;
        }
        .hero-cta-section a:hover {
            color: #B06CFF;
        }

        /* Hero image section */
        .hero-image-section {
            background: #0F1826;
            padding-bottom: 40px;
        }

        /* Button section in dark mode */
        .stButton > button {
            box-shadow: 0 4px 12px rgba(176, 108, 255, 0.2);
        }

        /* Features section */
        .features-section {
            background: #0F1826;
            border-top: 1px solid #2A2F3A;
        }
        .features-title {
            color: #FFFFFF;
        }
        .feature-title {
            color: #FFFFFF;
        }
        .feature-desc {
            color: #C8C9CE;
        }

        /* FAF Logo in dark mode */
        .faf-logo {
            background: rgba(15, 24, 38, 0.95);
            color: #FFFFFF;
        }

        /* Route Recommendations title in dark mode */
        .route-recommendations-title {
            color: #FFFFFF !important;
        }

        /* Labels in dark mode */
        div[data-testid="stFileUploader"] label,
        div[data-testid="stNumberInput"] label {
            color: #FFFFFF !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="faf-logo">FAF</div>', unsafe_allow_html=True)

if not st.session_state.entered:
    # Hero Text Section - Title at Top
    st.markdown(
        """
        <div class="hero-text-section">
            <h1>Explore faster.</h1>
            <h2>Discovery should be fun, not complicated.</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # CTA Links
    st.markdown(
        """
        <div class="hero-cta-section">
            <a href="#discover">Start exploring</a>
            <a href="#how">How it works</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Hero Image - Full Width Below
    st.markdown('<div class="hero-image-section">', unsafe_allow_html=True)
    st.image("assets/marin-journal-piece-lead-2-1920x900.jpg", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Enter Button - Below Image
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("Enter Dashboard", use_container_width=True, type="primary"):
            st.session_state.entered = True
            st.rerun()

    # Features Section
    st.markdown(
        """
        <div class="features-section">
            <div class="features-title">Ride smarter, explore further</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    feat1, feat2, feat3 = st.columns(3, gap="large")

    with feat1:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-title">Your Preferences</div>
                <div class="feature-desc">Upload a GPX file or specify route characteristics. Distance, elevation, terrain—tell us what you're looking for.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with feat2:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-title">Smart Matching</div>
                <div class="feature-desc">Our AI analyzes thousands of routes to find perfect matches based on your riding style and preferences.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with feat3:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-title">Discover Routes</div>
                <div class="feature-desc">Get curated recommendations with detailed metrics, maps, and insights to plan your next ride.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.stop()

# Dashboard Title
st.markdown('<h1 class="route-recommendations-title">ROUTE RECOMMENDATIONS</h1>', unsafe_allow_html=True)

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
        "UPLOAD HERE!",
        type=["gpx"],
        help="Choose a .gpx file to send to the backend.",
    )
    if uploaded_gpx:
        st.caption(f"Selected file: {uploaded_gpx.name} ({len(uploaded_gpx.getvalue())} bytes)")
        if st.button("Send GPX to backend", use_container_width=True, type="primary"):
            ok, msg, data = upload_gpx_to_api(uploaded_gpx)
            if ok:
                st.success(msg)
                st.session_state.gpx_recommendations = data
            else:
                st.error(msg)

    n_recs = count_col.number_input(
        "HOW MANY ROUTES?",
        min_value=1,
        max_value=10,
        value=5,
        step=1,
    )

# Full-width "GET YOUR RECOMMENDATIONS" button
if st.button("GET YOUR RECOMMENDATIONS", use_container_width=True, type="primary"):
    ok, msg, data = fetch_recommendations(default_features["features"], n_recs)
    if ok and data is not None:
        st.session_state.recommendations = data
        st.success(msg)
    else:
        st.error(msg)

st.divider()

sidebar, map_area = st.columns([1, 2], gap="large")

with sidebar:
    st.markdown('<div class="section-header-green">Recommended Routes</div>', unsafe_allow_html=True)
    route_names = [rec["route_name"] for rec in st.session_state.recommendations][: n_recs or 5]
    selected_route = st.selectbox("Route", route_names, index=0 if route_names else None)

    selected = next((rec for rec in st.session_state.recommendations if rec["route_name"] == selected_route), None)

    st.markdown('<div style="font-size: 20px; font-weight: 800; margin: 24px 0 16px 0; color: #0F1826;">Route Metrics</div>', unsafe_allow_html=True)
    if selected:
        st.metric("Distance (m)", f"{selected['distance_m']:.0f}")
        st.metric("Ascent (m)", f"{selected['ascent_m']:.0f}")
        st.metric("Duration", format_duration(selected["duration_s"]))
        st.metric("Turn Density", f"{selected['turn_density']:.2f}")
        st.metric("Similarity Score", f"{selected['similarity_score']:.4f}")
    else:
        st.info("Select a route to view KPIs.")

with map_area:
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
