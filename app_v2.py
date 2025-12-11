import os
import base64
from typing import Any, Dict, List

import streamlit as st
import streamlit.components.v1 as components
import requests

st.set_page_config(page_title="FAF - Find A Friend", layout="wide", initial_sidebar_state="collapsed")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Embed hero image as base64 for CSS background to ensure it loads
HERO_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "assets", "marin-journal-piece-lead-2-1920x900.jpg")
try:
    with open(HERO_IMAGE_PATH, "rb") as _f:
        HERO_BG_BASE64 = base64.b64encode(_f.read()).decode("ascii")
except FileNotFoundError:
    HERO_BG_BASE64 = None
API_BASE_URL = 'https://cyclemore-backend-696636878944.europe-west2.run.app/'
# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "recommendations" not in st.session_state:
    st.session_state.recommendations: List[Dict[str, Any]] = []
if "curveball_result" not in st.session_state:
    st.session_state.curveball_result: Dict[str, Any] | None = None
if "selected_route" not in st.session_state:
    st.session_state.selected_route = None
if "input_source" not in st.session_state:
    st.session_state.input_source = None  # "gpx" or "prompt"
if "show_results" not in st.session_state:
    st.session_state.show_results = False
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "similar"  # "similar" or "curveball"

st.markdown(
    """
    <style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Global styling */
    .stApp {
        background: #F8F8F8;
    }

    /* Remove ALL default Streamlit padding */
    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }

    /* FAF Logo styling */
    .faf-logo {
        font-family: "Impact", "Arial Black", sans-serif;
        font-size: 72px;
        font-weight: 900;
        letter-spacing: 2px;
        color: #0F1826;
        text-align: center;
        margin: 0 !important;
        padding-top: 10px;
        font-style: italic;
    }

    /* Landing page styling */
    .landing-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 20px;
        text-align: center;
    }

    .hero-section {
        position: relative;
        width: 100%;
        margin: 40px 0;
        min-height: 65vh;
        display: flex;
        align-items: center;
        justify-content: center;
        background:
            linear-gradient(120deg, rgba(0,0,0,0.38), rgba(0,0,0,0.20)),
            url('assets/marin-journal-piece-lead-2-1920x900.jpg');
        background-size: cover;
        background-position: center;
        border-radius: 18px;
        overflow: hidden;
        box-shadow: 0 16px 38px rgba(0,0,0,0.22);
    }

    .hero-overlay {
        position: relative;
        z-index: 1;
        text-align: center;
        width: 100%;
        max-width: 900px;
        padding: 60px 24px;
        color: #ffffff;
    }

    .hero-text {
        font-size: 52px;
        font-weight: 900;
        color: #ffffff;
        margin-bottom: 12px;
        letter-spacing: 1px;
        text-shadow: 0 8px 22px rgba(0,0,0,0.35);
    }

    .hero-subtext {
        font-size: 28px;
        font-weight: 800;
        color: #f0f4fb;
        margin-bottom: 12px;
        text-shadow: 0 6px 18px rgba(0,0,0,0.32);
    }

    .hero-body {
        font-size: 18px;
        font-weight: 500;
        color: #e6ebf5;
        margin: 0 auto;
        max-width: 640px;
        line-height: 1.6;
        text-shadow: 0 4px 12px rgba(0,0,0,0.28);
    }

    /* Input page header */
    .input-header {
        background: transparent;
        color: #0F1826;
        padding: 10px 0 12px 0;
        text-align: center;
        margin-bottom: 30px;
    }

    .input-header h1 {
        margin: 0;
        font-size: 36px;
        font-weight: 900;
        letter-spacing: 1.5px;
        color: inherit;
    }

    /* Input cards */
    .input-card {
        background: white;
        border: 3px solid #0F1826;
        border-radius: 12px;
        padding: 30px;
        min-height: 50px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        text-align: left;
    }
    .input-card h3 {
        margin-top: 0;
        color: #0F1826;
        font-weight: 800;
    }
    .input-card p {
        margin-bottom: 0;
        color: #0F1826;
    }

    /* Remove default column padding to make room for our boxes */
    .element-container {
        padding: 0 !important;
    }

    /* Results section */
    .results-divider {
        background: #d4d9e1;
        height: 2px;
        width: 100%;
        margin: 40px 0 30px 0;
        border-radius: 999px;
    }

    /* Output page sidebar */
    .output-sidebar {
        padding: 20px;
    }

    .stats-header {
        font-size: 18px;
        font-weight: 800;
        margin: 24px 0 16px 0;
        color: #0F1826;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Map container */
    .map-container {
        padding: 20px;
        height: 100%;
    }

    /* Button styling */
    /* Pill buttons in a blue Apple-like style */
    .stButton > button,
    .stDownloadButton > button,
    [data-testid="baseButton-primary"],
    [data-testid="baseButton-secondary"] {
        width: 100%;
        border-radius: 999px !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        padding: 14px 28px !important;
        cursor: pointer;
        transition: transform 120ms ease, box-shadow 120ms ease, filter 120ms ease;
    }

    /* Filled primary */
    [data-testid="baseButton-primary"] {
        background: #ff5fa2 !important;
        border: 2px solid #ff5fa2 !important;
        color: #ffffff !important;
        box-shadow: 0 8px 22px rgba(255, 95, 162, 0.25);
    }
    [data-testid="baseButton-primary"]:hover {
        filter: brightness(1.05);
        transform: translateY(-1px);
        box-shadow: 0 10px 26px rgba(255, 95, 162, 0.28);
    }
    [data-testid="baseButton-primary"]:active {
        filter: brightness(0.97);
        transform: translateY(0);
        box-shadow: 0 6px 18px rgba(255, 95, 162, 0.22);
    }

    /* Outline / secondary */
    [data-testid="baseButton-secondary"] {
        background: #ffffff !important;
        color: #ff5fa2 !important;
        border: 2px solid #ff5fa2 !important;
        box-shadow: 0 6px 18px rgba(255, 95, 162, 0.12);
    }
    [data-testid="baseButton-secondary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 10px 24px rgba(255, 95, 162, 0.18);
    }
    [data-testid="baseButton-secondary"]:active {
        transform: translateY(0);
        box-shadow: 0 6px 16px rgba(255, 95, 162, 0.15);
    }

    /* Download button matches primary filled style */
    .stDownloadButton > button {
        background: #ff5fa2 !important;
        border: 2px solid #ff5fa2 !important;
        color: #ffffff !important;
        box-shadow: 0 8px 22px rgba(255, 95, 162, 0.25);
    }
    .stDownloadButton > button:hover {
        filter: brightness(1.05);
        transform: translateY(-1px);
        box-shadow: 0 10px 26px rgba(255, 95, 162, 0.28);
    }
    .stDownloadButton > button:active {
        filter: brightness(0.97);
        transform: translateY(0);
        box-shadow: 0 6px 18px rgba(255, 95, 162, 0.22);
    }

    /* Tab styling - increase font size */
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 18px;
        font-weight: 600;
        padding: 12px 20px;
    }

    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        font-weight: 700;
    }

    /* Radio button styling - double font size */
    .stRadio > div {
        font-size: 32px !important;
        font-weight: 700 !important;
    }

    .stRadio label {
        font-size: 32px !important;
        font-weight: 700 !important;
    }

    /* Dark mode */
    @media (prefers-color-scheme: dark) {
        .stApp {
            background: #0b0f16;
            color: #f4f6fb;
        }
        .landing-container {
            color: #f4f6fb;
        }
        .input-header {
            color: #f4f6fb;
        }
        .input-card {
            background: #121926;
            border-color: #2b3a52;
            box-shadow: 0 6px 18px rgba(0,0,0,0.35);
        }
        .input-card h3,
        .input-card p {
            color: #f4f6fb;
        }
        .results-divider {
            background: #2b3a52;
        }
        .stats-header {
            color: #f4f6fb;
        }
        .map-container {
            background: #0f1620;
            border-radius: 12px;
        }
        .output-sidebar {
            color: #f4f6fb;
        }
        .hero-text, .hero-subtext, .hero-body {
            color: #f4f6fb;
        }

        /* General text */
        .stMarkdown, .stText, .stCaption, .stMetric {
            color: #f4f6fb !important;
        }

        /* Form controls */
        input, textarea, select {
            background-color: #121926 !important;
            color: #f4f6fb !important;
            border: 2px solid #1f2a3c !important;
        }
        input:focus, textarea:focus, select:focus {
            border-color: #ff5fa2 !important;
            box-shadow: 0 0 0 2px rgba(255, 95, 162, 0.35) !important;
        }
        input::placeholder,
        textarea::placeholder {
            color: #cfd5e3 !important;
        }

        /* File uploader */
        [data-testid="stFileUploader"] section {
            background: #121926 !important;
            border: 2px dashed #2b3a52 !important;
            color: #f4f6fb !important;
        }
        [data-testid="stFileUploader"] label,
        [data-testid="stFileUploader"] p,
        [data-testid="stFileUploader"] small,
        [data-testid="stFileUploader"] span,
        [data-testid="stFileUploader"] div {
            color: #f4f6fb !important;
        }
        [data-testid="stFileUploader"] * {
            color: #f4f6fb !important;
        }
        [data-testid="stFileUploaderDropzone"],
        [data-testid="stFileUploaderDropzone"] * {
            color: #f4f6fb !important;
        }
        [data-testid="stFileUploader"] button {
            background: #1b2433 !important;
            color: #f4f6fb !important;
            border: 1px solid #2b3a52 !important;
        }
        [data-testid="stFileUploader"] button:hover {
            background: #222d3f !important;
            border-color: #ff5fa2 !important;
        }

        /* Checkboxes and radio labels */
        .stCheckbox label, .stRadio label,
        [data-testid="stCheckbox"] label,
        [data-testid="stCheckbox"] p,
        [data-testid="stCheckbox"] span,
        [data-testid="stCheckbox"] * {
            color: #f4f6fb !important;
        }

        /* Selectbox text */
        [data-baseweb="select"] {
            background: #121926 !important;
            color: #f4f6fb !important;
            border: 2px solid #1f2a3c !important;
        }
        [data-baseweb="select"] * {
            color: #f4f6fb !important;
        }
        [data-testid="stSelectbox"] div[role="combobox"] {
            background: #121926 !important;
            color: #f4f6fb !important;
            border: 2px solid #1f2a3c !important;
        }
        [data-testid="stSelectbox"] svg {
            fill: #f4f6fb !important;
            color: #f4f6fb !important;
        }
        [data-testid="stSelectbox"] * {
            color: #f4f6fb !important;
        }

        /* Logo */
        .faf-logo {
            color: #f4f6fb !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def format_duration(seconds: float) -> str:
    """Format duration from seconds to readable string."""
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
    """Upload GPX file to API and get recommendations with curveball."""
    files = {"file": (file.name, file.getvalue(), "application/gpx+xml")}
    try:
        resp = requests.post(f"{API_BASE_URL}/recommend-from-gpx", files=files, timeout=60)
    except Exception as exc:
        return False, f"Request failed: {exc}", None

    if resp.status_code != 200:
        try:
            detail = resp.json().get("detail")
        except Exception:
            detail = resp.text
        return False, f"API error {resp.status_code}: {detail}", None

    try:
        data = resp.json()
    except Exception:
        return False, "Invalid JSON response from API.", None

    if not isinstance(data, dict) or "similar" not in data or "curveball" not in data:
        return False, "Unexpected response format from API.", None

    return True, "Recommendations with curveball ready.", data


def fetch_prompt_recommendations(prompt: str, n_similar: int) -> tuple[bool, str, Dict[str, Any] | None]:
    """Generate route recommendations from a natural language prompt."""
    payload = {"prompt": prompt, "n_similar": n_similar}
    try:
        resp = requests.post(f"{API_BASE_URL}/recommend-from-prompt", json=payload, timeout=60)
    except Exception as exc:
        return False, f"Request failed: {exc}", None

    if resp.status_code != 200:
        try:
            detail = resp.json().get("detail")
        except Exception:
            detail = resp.text
        return False, f"API error {resp.status_code}: {detail}", None

    try:
        data = resp.json()
    except Exception:
        return False, "Invalid JSON response from API.", None

    if not isinstance(data, dict) or "similar" not in data or "curveball" not in data:
        return False, "Unexpected response format from API.", None

    return True, "Recommendations from prompt ready.", data


# ============================================================================
# LANDING PAGE
# ============================================================================
if st.session_state.page == "landing":
    st.markdown('<div class="faf-logo">FAF</div>', unsafe_allow_html=True)
    st.markdown('<div class="landing-container">', unsafe_allow_html=True)

    # Build inline background style to ensure the image loads in CSS
    if HERO_BG_BASE64:
        hero_bg_style = f"background: linear-gradient(120deg, rgba(0,0,0,0.38), rgba(0,0,0,0.20)), url('data:image/jpeg;base64,{HERO_BG_BASE64}');"
    else:
        hero_bg_style = "background: linear-gradient(120deg, rgba(0,0,0,0.38), rgba(0,0,0,0.20));"

    # Hero section with background image and centered overlay
    st.markdown(f"""
        <div class="hero-section" style="{hero_bg_style}">
            <div class="hero-overlay">
                <div class="hero-text">Explore faster.</div>
                <div class="hero-subtext">Fast as f***</div>
                <div class="hero-body">"Discovery should be fun, not complicated."</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Get Started button below image
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Let it whip !", type="primary", use_container_width=True):
            st.session_state.page = "input"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================================
# MAIN PAGE (INPUT + OUTPUT)
# ============================================================================
elif st.session_state.page == "input":
    # Header
    st.markdown(
        '<div class="input-header"><h1>What are you looking for?</h1></div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="results-divider"></div>', unsafe_allow_html=True)

    # Main input area - two columns with styled containers
    col1, col2 = st.columns(2, gap="large")

    with col1:
        # Create a visual box using HTML
        st.markdown("""
            <div class="input-card">
                <h3>📤 UPLOAD</h3>
                <p>Upload your GPX file to find similar routes</p>
            </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Choose GPX file",
            type=["gpx"],
            help="Upload a GPX file from your cycling computer or app",
            label_visibility="collapsed"
        )

        use_gpx = st.checkbox("Use GPX", value=bool(uploaded_file), disabled=not uploaded_file)

        if uploaded_file and use_gpx:
            st.success(f"✓ {uploaded_file.name} ready")

    with col2:
        # Create a visual box using HTML
        st.markdown("""
            <div class="input-card">
                <h3>💬 TELL US</h3>
                <p>Describe your ideal route in your own words</p>
            </div>
        """, unsafe_allow_html=True)

        prompt_text = st.text_area(
            "Describe your route",
            placeholder="e.g., A flat 20km loop around Richmond Park, mostly paved, low traffic",
            height=100,
            label_visibility="collapsed"
        )

        use_llm = st.checkbox("Use LLM", value=bool(prompt_text), disabled=not prompt_text)

        if prompt_text and use_llm:
            st.success(f"✓ Prompt ready ({len(prompt_text)} chars)")

    # GO button
    st.markdown("###")
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn2:
        if st.button("GO!", type="primary", use_container_width=True):
            # Validate input
            if use_gpx and uploaded_file:
                with st.spinner("Processing GPX file..."):
                    success, message, data = upload_gpx_to_api(uploaded_file)
                    if success:
                        st.session_state.curveball_result = data
                        st.session_state.recommendations = data.get("similar", [])
                        st.session_state.input_source = "gpx"
                        st.session_state.show_results = True
                        st.rerun()
                    else:
                        st.error(message)

            elif use_llm and prompt_text:
                with st.spinner("Generating recommendations from your prompt..."):
                    success, message, data = fetch_prompt_recommendations(prompt_text, n_similar=5)
                    if success:
                        st.session_state.curveball_result = data
                        st.session_state.recommendations = data.get("similar", [])
                        st.session_state.input_source = "prompt"
                        st.session_state.show_results = True
                        st.rerun()
                    else:
                        st.error(message)

            else:
                st.warning("Please select either GPX or LLM input and provide the required data.")

    # ========================================================================
    # RESULTS SECTION (shown below input when results are ready)
    # ========================================================================
    if st.session_state.show_results:
        # Results divider
        st.markdown('<div class="results-divider"></div>', unsafe_allow_html=True)
        st.markdown("## 📊 RESULTS")

        # Show input features if available
        if st.session_state.curveball_result:
            # Show GPX features if from GPX upload
            if st.session_state.input_source == "gpx" and "gpx_features" in st.session_state.curveball_result:
                with st.expander("📂 View Your GPX File Features", expanded=False):
                    features = st.session_state.curveball_result["gpx_features"]
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Distance", f"{features.get('distance_m', 0)/1000:.0f} km")
                        st.metric("Ascent", f"{features.get('ascent_m', 0):.0f} m")
                    with col2:
                        st.metric("Flat Section", f"{features.get('Flat Section', 0):.0f}%")
                        st.metric("Paved Road", f"{features.get('Paved_Road', 0):.0f}%")
                    with col3:
                        st.metric("Cycleway", f"{features.get('Cycleway', 0):.0f}%")
                        st.metric("On Road", f"{features.get('on_road', 0):.0f}%")

            # Show generated features if from LLM prompt
            elif st.session_state.input_source == "prompt" and "generated_features" in st.session_state.curveball_result:
                with st.expander("🤖 View Generated Route Features", expanded=False):
                    features = st.session_state.curveball_result["generated_features"]
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Distance", f"{features.get('distance_m', 0)/1000:.0f} km")
                        st.metric("Ascent", f"{features.get('ascent_m', 0):.0f} m")
                    with col2:
                        st.metric("Flat Section", f"{features.get('Flat Section', 0):.0f}%")
                        st.metric("Paved Road", f"{features.get('Paved_Road', 0):.0f}%")
                    with col3:
                        st.metric("Cycleway", f"{features.get('Cycleway', 0):.0f}%")
                        st.metric("Region", features.get('region', 'N/A'))

        # Two-column layout
        sidebar_col, map_col = st.columns([1, 2])

        with sidebar_col:
            st.markdown('<div class="output-sidebar">', unsafe_allow_html=True)

            # Route selection with tabs
            has_curveball = st.session_state.curveball_result and st.session_state.curveball_result.get("curveball")

            # Initialize selected at higher scope
            selected = None

            if has_curveball:
                # Use radio buttons to track which view is active
                view_choice = st.radio(
                    "View",
                    ["🎯 Best Routes", "🎲 Something Different"],
                    horizontal=True,
                    label_visibility="collapsed"
                )

                # Update session state based on selection
                if view_choice == "🎯 Best Routes":
                    st.session_state.active_tab = "similar"
                else:
                    st.session_state.active_tab = "curveball"
            else:
                st.session_state.active_tab = "similar"

            # Show appropriate content based on active tab
            if st.session_state.active_tab == "similar":
                # Similar routes view
                st.markdown("### Select Route")
                active_recs = st.session_state.recommendations
                route_names = [rec["route_name"] for rec in active_recs][:5]

                selected_route_name = st.selectbox(
                    "Route",
                    route_names,
                    index=0 if route_names else None,
                    label_visibility="collapsed",
                    key="route_selector_v2"
                )

                selected = next((rec for rec in active_recs if rec["route_name"] == selected_route_name), None)

            elif st.session_state.active_tab == "curveball" and has_curveball:
                # Curveball view
                curveball = st.session_state.curveball_result["curveball"]
                curveball_cluster = st.session_state.curveball_result.get("curveball_cluster_label", "Unknown")
                user_cluster = st.session_state.curveball_result.get("user_cluster_label", "Unknown")

                st.caption(f"Your routes: **{user_cluster}**")
                st.caption(f"This route: **{curveball_cluster}**")
                st.markdown(f"#### {curveball['route_name']}")

                # Set selected to be the curveball
                selected = curveball

            # Stats section
            st.markdown('<div class="stats-header">STATS</div>', unsafe_allow_html=True)

            if selected:
                st.metric("Distance", f"{selected['distance_m']/1000:.1f} km")
                st.metric("Ascent", f"{selected['ascent_m']:.0f} m")
                st.metric("Surface", selected.get("primary_surface", "Unknown"))

                # Download button
                st.markdown("###")
                if st.button("📥 DOWNLOAD GPX", use_container_width=True):
                    route_id = selected['route_id']
                    gpx_url = f"{API_BASE_URL}/download-gpx/{route_id}"

                    with st.spinner("📦 Generating GPX file..."):
                        try:
                            response = requests.get(gpx_url, timeout=30)
                            if response.status_code == 200:
                                st.download_button(
                                    label="💾 Save GPX File",
                                    data=response.content,
                                    file_name=f"route_{route_id}.gpx",
                                    mime="application/gpx+xml",
                                    use_container_width=True
                                )
                                st.success("✓ Ready to download")
                            else:
                                try:
                                    error_detail = response.json().get('detail', 'Unknown error')
                                except Exception:
                                    error_detail = response.text
                                st.error(f"Error: {error_detail}")
                        except Exception as e:
                            st.error(f"Failed: {str(e)}")
            else:
                st.info("No route selected")

            st.markdown('</div>', unsafe_allow_html=True)

        with map_col:
            st.markdown('<div class="map-container">', unsafe_allow_html=True)

            if selected:
                route_id = selected['route_id']
                route_name = selected['route_name']
                map_url = f"{API_BASE_URL}/visualize-route/{route_id}"

                with st.spinner("🗺️ Loading map..."):
                    try:
                        response = requests.get(map_url, timeout=30)
                        if response.status_code == 200:
                            # Display the map HTML
                            components.html(response.text, height=600, scrolling=True)
                            st.caption(f"📍 {route_name}")
                        else:
                            st.error(f"Could not load map: {response.status_code}")
                            st.info("Map unavailable")
                    except Exception as e:
                        st.error(f"Error loading map: {str(e)}")
            else:
                st.info("Select a route to view map")

            st.markdown('</div>', unsafe_allow_html=True)
# bye 
