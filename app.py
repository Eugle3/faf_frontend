import json
import os
from typing import Any, Dict, List

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import requests

st.set_page_config(page_title="Route Dashboard", layout="wide")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

if "entered" not in st.session_state:
    st.session_state.entered = False
if "recommendations" not in st.session_state:
    st.session_state.recommendations: List[Dict[str, Any]] = []
if "gpx_recommendations" not in st.session_state:
    st.session_state.gpx_recommendations: List[Dict[str, Any]] = []
if "curveball_result" not in st.session_state:
    st.session_state.curveball_result: Dict[str, Any] | None = None
if "curveball_view" not in st.session_state:
    st.session_state.curveball_view = None

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
        padding: 60px 0 100px 0;
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

    /* Dashboard Section Headers - Subtitle level */
    .section-header {
        background: #B06CFF;
        color: white;
        padding: 18px 28px;
        border-radius: 12px;
        margin-bottom: 24px;
        font-weight: 800;
        font-size: 18px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .section-header-green {
        background: #4F6844;
        color: white;
        padding: 18px 28px;
        border-radius: 12px;
        margin-bottom: 24px;
        font-weight: 800;
        font-size: 18px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* Typography Hierarchy Summary:
       - Big Title (42px): ROUTE RECOMMENDATIONS
       - Subtitle (16-18px, uppercase, bold): Section headers, labels, buttons
       - Body Text (14px, normal): Descriptive text, inputs
    */

    /* Card Styling */
    div[data-testid="stMetric"] {
        background: white;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #B06CFF;
    }

    /* Make all three sections equal size */
    div[data-testid="stFileUploader"],
    div[data-testid="stNumberInput"],
    div[data-testid="stButton"] {
        height: 140px !important;
    }

    /* File uploader styling */
    div[data-testid="stFileUploader"] section {
        height: 100px !important;
        min-height: 100px !important;
    }
    div[data-testid="stFileUploader"] section > div {
        height: 100px !important;
        min-height: 100px !important;
    }

    /* Number input styling */
    div[data-testid="stNumberInput"] > div > div {
        height: 100px !important;
        min-height: 100px !important;
    }

    /* Subtitle styling - Upload and Number labels */
    div[data-testid="stFileUploader"] label,
    div[data-testid="stNumberInput"] label {
        font-weight: 800 !important;
        font-size: 16px !important;
        color: #0F1826 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 12px !important;
    }

    /* Body text styling - smaller descriptive text */
    div[data-testid="stFileUploader"] section small,
    div[data-testid="stFileUploader"] section p {
        font-size: 14px !important;
        font-weight: 400 !important;
        color: #666666 !important;
    }

    /* Make number input controls thinner */
    div[data-testid="stNumberInput"] button {
        width: 32px !important;
        min-width: 32px !important;
        padding: 4px !important;
    }

    /* Button Styling - Subtitle level action */
    .stButton > button {
        border-radius: 10px;
        font-weight: 900 !important;
        transition: all 0.3s ease;
        font-size: 16px !important;
        padding: 0 24px !important;
        height: 100px !important;
        min-height: 100px !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(176, 108, 255, 0.3);
    }

    /* Add spacing around main button */
    .stButton {
        margin: 0;
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

        /* Labels (subtitles) in dark mode */
        div[data-testid="stFileUploader"] label,
        div[data-testid="stNumberInput"] label {
            color: #FFFFFF !important;
        }

        /* Body text in dark mode */
        div[data-testid="stFileUploader"] section small,
        div[data-testid="stFileUploader"] section p {
            color: #C8C9CE !important;
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
    col1, col2, col3 = st.columns([3, 1, 3])
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
    """
    Upload GPX file to API and get recommendations with curveball.

    Returns:
        (success, message, result_dict) where result_dict contains:
        - "similar": List of similar routes
        - "curveball": Single route from different cluster
        - "user_cluster_label": User's cluster label
        - "curveball_cluster_label": Curveball cluster label
    """
    files = {"file": (file.name, file.getvalue(), "application/gpx+xml")}
    try:
        # Increased timeout to 60s for ORS API call
        resp = requests.post(f"{API_BASE_URL}/recommend-from-gpx", files=files, timeout=60)
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

    if not isinstance(data, dict) or "similar" not in data or "curveball" not in data:
        return False, "Unexpected response format from API.", None

    return True, "Recommendations with curveball ready.", data


def fetch_curveball_recommendations(features: Dict[str, Any], n_similar: int) -> tuple[bool, str, Dict[str, Any] | None]:
    """
    Fetch recommendations with a curveball from a different cluster.

    Returns:
        (success, message, result_dict) where result_dict contains:
        - "similar": List of n_similar routes
        - "curveball": Single route from different cluster
        - "user_cluster_label": User's cluster label
        - "curveball_cluster_label": Curveball cluster label
    """
    payload = {"features": features, "n_similar": n_similar}
    try:
        resp = requests.post(f"{API_BASE_URL}/recommend-with-curveball", json=payload, timeout=30)
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

    if not isinstance(data, dict) or "similar" not in data or "curveball" not in data:
        return False, "Unexpected response format from API.", None

    return True, "Recommendations with curveball loaded.", data


def fetch_prompt_recommendations(prompt: str, n_similar: int) -> tuple[bool, str, Dict[str, Any] | None]:
    """
    Generate route recommendations from a natural language prompt.

    Returns:
        (success, message, result_dict) where result_dict contains:
        - "similar": List of n_similar routes
        - "curveball": Single route from different cluster
        - "user_cluster_label": User's cluster label
        - "curveball_cluster_label": Curveball cluster label
        - "generated_features": Features generated from the prompt
    """
    payload = {"prompt": prompt, "n_similar": n_similar}
    try:
        resp = requests.post(f"{API_BASE_URL}/recommend-from-prompt", json=payload, timeout=60)
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

    if not isinstance(data, dict) or "similar" not in data or "curveball" not in data:
        return False, "Unexpected response format from API.", None

    return True, "Recommendations from prompt ready.", data


header = st.container()
with header:
    st.subheader("🚴 Find Similar Routes")

    tab1, tab2 = st.tabs(["Upload GPX File", "Describe Your Route"])

    with tab1:
        uploaded_gpx = st.file_uploader(
            "Upload a GPX file from your bike computer or tracking app",
            type=["gpx"],
            help="Upload a .gpx file to find routes with similar characteristics.",
        )
        if uploaded_gpx:
            st.caption(f"✓ Selected: {uploaded_gpx.name} ({len(uploaded_gpx.getvalue())/1024:.1f} KB)")

            if st.button("🔍 Find Similar Routes", use_container_width=True, type="primary", key="gpx_find"):
                with st.spinner("Processing your GPX file..."):
                    ok, msg, data = upload_gpx_to_api(uploaded_gpx)
                    if ok and data is not None:
                        st.success(f"✓ Found {len(data['similar'])} similar routes + 1 curveball!")
                        st.session_state.curveball_result = data
                        st.session_state.gpx_recommendations = data["similar"]
                        st.rerun()  # Refresh to show recommendations
                    else:
                        st.error(msg)

        # Display GPX file details if available
        if uploaded_gpx and st.session_state.gpx_recommendations:
            with st.expander("📊 GPX File Details"):
                first_rec = st.session_state.gpx_recommendations[0] if st.session_state.gpx_recommendations else None
                if first_rec:
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Your Route Distance", f"{first_rec['distance_m']/1000:.1f} km")
                    col2.metric("Your Route Ascent", f"{first_rec['ascent_m']:.0f} m")
                    # Note: Primary surface type would require backend to return surface breakdown
                    surface_type = first_rec.get('primary_surface', 'N/A')
                    col3.metric("Primary Surface", surface_type)

    with tab2:
        st.markdown("**Describe your ideal route in natural language and let AI find similar routes!**")

        st.markdown("""
        **Examples:**
        - "A flat 10 km loop around Richmond Park, mostly paved, low traffic"
        - "A challenging 20km mountain route with steep climbs and gravel sections"
        - "An easy 5km urban cycle path suitable for beginners"
        """)

        user_prompt = st.text_area(
            "Describe your ideal route:",
            placeholder="e.g., A flat 10 km loop around a park, mostly paved, low traffic",
            height=120,
            help="Describe the route you're looking for in natural language"
        )

        n_recs_prompt = st.number_input(
            "Number of recommendations",
            min_value=1,
            max_value=10,
            value=5,
            step=1,
            key="prompt_n_recs"
        )

        if st.button("🔍 Find Routes", use_container_width=True, type="primary", key="prompt_find"):
            if not user_prompt.strip():
                st.warning("⚠️ Please describe your ideal route first!")
            else:
                with st.spinner("Generating route features and finding matches..."):
                    ok, msg, data = fetch_prompt_recommendations(user_prompt, n_recs_prompt)
                    if ok and data is not None:
                        st.success(f"✓ Found {len(data['similar'])} similar routes + 1 curveball!")
                        st.session_state.curveball_result = data
                        st.session_state.recommendations = data["similar"]

                        # Show generated features in an expander
                        if "generated_features" in data:
                            with st.expander("🤖 View Generated Route Features"):
                                generated = data["generated_features"]
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Distance", f"{generated.get('distance_m', 0)/1000:.1f} km")
                                    st.metric("Ascent", f"{generated.get('ascent_m', 0):.0f} m")
                                with col2:
                                    st.metric("Flat Section", f"{generated.get('Flat Section', 0)*100:.0f}%")
                                    st.metric("Paved Road", f"{generated.get('Paved_Road', 0)*100:.0f}%")
                                with col3:
                                    st.metric("Cycleway", f"{generated.get('Cycleway', 0)*100:.0f}%")
                                    st.metric("Region", generated.get('region', 'N/A'))

                        st.rerun()  # Refresh to show recommendations
                    else:
                        st.error(msg)
                        if "OPENKEY" in msg:
                            st.info("💡 Make sure your OPENKEY environment variable is set for OpenAI API access")

st.divider()

sidebar, map_area = st.columns([1, 2], gap="large")

with sidebar:
    # Show cluster classification if curveball result is available
    if st.session_state.curveball_result:
        cluster_label = st.session_state.curveball_result.get("user_cluster_label", "Unknown")
        st.info(f"🏷️ Your Route Type: **{cluster_label}**")

    # Let user choose which recommendation source to view
    rec_source = st.radio(
        "Recommendation Source",
        ["LLM Prompt", "Uploaded GPX"],
        index=1 if st.session_state.gpx_recommendations else 0
    )

    # Choose which recommendations to display
    if rec_source == "Uploaded GPX" and st.session_state.gpx_recommendations:
        active_recs = st.session_state.gpx_recommendations
        st.caption(f"📍 Showing {len(active_recs)} routes similar to your GPX file")
    else:
        active_recs = st.session_state.recommendations
        st.caption(f"📍 Showing routes based on your prompt")

    # Create tabs for recommended routes and curveball
    has_curveball = st.session_state.curveball_result and st.session_state.curveball_result.get("curveball")

    if has_curveball:
        tab1, tab2 = st.tabs(["🎯 Recommended Routes", "🎲 Why not try..."])
    else:
        # If no curveball, just show recommended routes without tabs
        tab1 = st.container()
        tab2 = None

    # Tab 1: Recommended Routes
    with tab1:
        st.subheader("Recommended Routes")
        route_names = [rec["route_name"] for rec in active_recs][:5]
        selected_route = st.selectbox("Route", route_names, index=0 if route_names else None, key="rec_selectbox")
        selected = next((rec for rec in active_recs if rec["route_name"] == selected_route), None)

    # Tab 2: Curveball (if available)
    if tab2 is not None:
        with tab2:
            curveball = st.session_state.curveball_result["curveball"]
            curveball_cluster = st.session_state.curveball_result.get("curveball_cluster_label", "Unknown")
            user_cluster = st.session_state.curveball_result.get("user_cluster_label", "Unknown")

            st.caption(f"Your routes are typically: **{user_cluster}**")
            st.caption(f"This route is: **{curveball_cluster}**")
            st.markdown(f"### {curveball['route_name']}")

            # Override selected to be the curveball
            selected = curveball

    # Route Stats section (displays for whatever is selected in either tab)
    st.markdown('<div style="font-size: 18px; font-weight: 800; margin: 24px 0 16px 0; color: #0F1826; text-transform: uppercase; letter-spacing: 1px;">Route Stats</div>', unsafe_allow_html=True)
    if selected:
        st.metric("Distance", f"{selected['distance_m']/1000:.1f} km")
        st.metric("Ascent", f"{selected['ascent_m']:.0f} m")
        st.metric("Estimated Duration", format_duration(selected["duration_s"]))
        st.metric("Surface Type", selected.get("primary_surface", "Unknown"))

        # Add GPX download button
        st.divider()
        if st.button("📥 Download GPX", use_container_width=True, type="primary"):
            route_id = selected['route_id']
            gpx_url = f"{API_BASE_URL}/download-gpx/{route_id}"

            try:
                response = requests.get(gpx_url, timeout=30)
                if response.status_code == 200:
                    # Trigger download using Streamlit's download_button
                    st.download_button(
                        label="💾 Click to Save GPX File",
                        data=response.content,
                        file_name=f"route_{route_id}.gpx",
                        mime="application/gpx+xml",
                        use_container_width=True
                    )
                    st.success("✓ GPX file ready! Click above to save.")
                else:
                    try:
                        error_detail = response.json().get('detail', 'Unknown error')
                    except Exception:  # noqa: BLE001
                        error_detail = response.text
                    st.error(f"Error: {error_detail}")
            except Exception as e:  # noqa: BLE001
                st.error(f"Failed to fetch GPX: {str(e)}")
    else:
        st.info("Select a route to view Route Stats.")

with map_area:
    st.subheader("Route Map")

    # Display whichever route is currently selected (from either tab)
    if selected:
        route_id = selected['route_id']
        route_name = selected['route_name']
        map_url = f"{API_BASE_URL}/visualize-route/{route_id}"

        try:
            # Fetch map HTML from backend
            response = requests.get(map_url, timeout=30)
            if response.status_code == 200:
                # Display Folium map HTML
                components.html(response.text, height=600, scrolling=True)
                st.caption(f"📍 Showing: {route_name}")
            else:
                st.error(f"Could not load map: {response.status_code}")
                # Fallback to placeholder
                st.info("Map visualization unavailable for this route")
        except Exception as e:  # noqa: BLE001
            st.error(f"Error loading map: {str(e)}")
            st.info("Unable to display route map")
    else:
        st.info("Select a route to view its map")

st.divider()
with st.expander("🔍 Raw Data (Debug View)"):
    tab_a, tab_b = st.tabs(["GPX Recommendations", "Prompt Recommendations"])
    with tab_a:
        st.json(st.session_state.gpx_recommendations or {"info": "No GPX uploaded yet."})
    with tab_b:
        st.json(st.session_state.recommendations or {"info": "No prompt recommendations yet."})
