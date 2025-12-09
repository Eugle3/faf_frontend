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
    .faf-logo {
        position: fixed;
        top: 16px;
        left: 24px;
        font-family: "Impact", "Anton", "Arial Black", sans-serif;
        font-size: 44px;
        font-style: italic;
        font-weight: 900;
        letter-spacing: 1px;
        color: #0f1116;
        padding: 8px 14px;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.92);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
        z-index: 9999;
    }
    /* Match number input height with uploader */
    div[data-testid="stNumberInput"] {
        min-height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    header[data-testid="stHeader"] {
        background: transparent;
        box-shadow: none;
    }
    header[data-testid="stHeader"] > div {
        background: transparent;
    }
    .hero {
        background: linear-gradient(180deg, #e8c8c8 0%, #c77874 100%);
        padding: 140px 32px;
        text-align: center;
        margin-bottom: 32px;
        width: 100vw;
        margin-left: calc(-50vw + 50%);
    }
    .hero h1 {
        font-size: 120px;
        font-weight: 900;
        letter-spacing: -3px;
        margin: 0;
        color: #0f1116;
    }
    .hero h2 {
        font-size: 36px;
        font-weight: 700;
        margin-top: 16px;
        margin-bottom: 40px;
        color: #0f1116;
    }
    .enter-btn {
        font-size: 20px;
        padding: 14px 24px;
        border-radius: 12px;
        border: none;
        background: #0f1116;
        color: white;
        cursor: pointer;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="faf-logo">FAF</div>', unsafe_allow_html=True)

if not st.session_state.entered:
    st.markdown(
        """
        <div class="hero">
            <h1>FAF</h1>
            <h2>Cycle More</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Click here to enter", use_container_width=True, type="primary"):
        st.session_state.entered = True
    st.stop()

st.title("Route Overview")

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
    st.subheader("🚴 Find Similar Routes")

    tab1, tab2 = st.tabs(["Upload GPX File", "Use Default Features"])

    with tab1:
        uploaded_gpx = st.file_uploader(
            "Upload a GPX file from your bike computer or tracking app",
            type=["gpx"],
            help="Upload a .gpx file to find routes with similar characteristics.",
        )
        if uploaded_gpx:
            st.caption(f"✓ Selected: {uploaded_gpx.name} ({len(uploaded_gpx.getvalue())/1024:.1f} KB)")

            if st.button("🔍 Find Similar Routes", use_container_width=True, type="primary"):
                with st.spinner("Processing your GPX file..."):
                    ok, msg, data = upload_gpx_to_api(uploaded_gpx)
                    if ok:
                        st.success(f"✓ Found {len(data)} similar routes!")
                        st.session_state.gpx_recommendations = data
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
        n_recs = st.number_input(
            "Number of recommendations",
            min_value=1,
            max_value=10,
            value=5,
            step=1,
        )
        if st.button("Get Recommendations", use_container_width=True):
            with st.spinner("Fetching recommendations..."):
                ok, msg, data = fetch_recommendations(default_features["features"], n_recs)
                if ok and data is not None:
                    st.session_state.recommendations = data
                    st.success(msg)
                else:
                    st.error(msg)

st.divider()

sidebar, map_area = st.columns([1, 2], gap="large")

with sidebar:
    # Let user choose which recommendation source to view
    rec_source = st.radio(
        "Recommendation Source",
        ["Default Features", "Uploaded GPX"],
        index=1 if st.session_state.gpx_recommendations else 0
    )

    # Choose which recommendations to display
    if rec_source == "Uploaded GPX" and st.session_state.gpx_recommendations:
        active_recs = st.session_state.gpx_recommendations
        st.caption(f"📍 Showing {len(active_recs)} routes similar to your GPX file")
    else:
        active_recs = st.session_state.recommendations
        st.caption(f"📍 Showing routes based on default features")

    st.subheader("Recommended Routes")
    route_names = [rec["route_name"] for rec in active_recs][:5]
    selected_route = st.selectbox("Route", route_names, index=0 if route_names else None)

    selected = next((rec for rec in active_recs if rec["route_name"] == selected_route), None)

    st.subheader("KPIs")
    if selected:
        st.metric("Distance", f"{selected['distance_m']/1000:.1f} km")
        st.metric("Ascent", f"{selected['ascent_m']:.0f} m")
        st.metric("Duration", format_duration(selected["duration_s"]))
        st.metric("Turn Density", f"{selected['turn_density']:.4f}")
        st.metric("Similarity Score", f"{selected['similarity_score']:.4f}")

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
        st.info("Select a route to view KPIs.")

with map_area:
    st.subheader("Route Map")
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
with st.expander("🔍 Raw Data (Debug View)"):
    tab_a, tab_b = st.tabs(["GPX Recommendations", "Default Recommendations"])
    with tab_a:
        st.json(st.session_state.gpx_recommendations or {"info": "No GPX uploaded yet."})
    with tab_b:
        st.json(st.session_state.recommendations or {"info": "No recommendations fetched yet."})
