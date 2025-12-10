import json
import os
from typing import Any, Dict, List

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import requests

st.set_page_config(page_title="Route Dashboard", layout="wide")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001")

if "entered" not in st.session_state:
    st.session_state.entered = False
if "recommendations" not in st.session_state:
    st.session_state.recommendations: List[Dict[str, Any]] = []
if "gpx_recommendations" not in st.session_state:
    st.session_state.gpx_recommendations: List[Dict[str, Any]] = []
if "curveball_result" not in st.session_state:
    st.session_state.curveball_result: Dict[str, Any] | None = None

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
                                    st.metric("Flat Section", f"{generated.get('Flat Section', 0):.0f}%")
                                    st.metric("Paved Road", f"{generated.get('Paved_Road', 0):.0f}%")
                                with col3:
                                    st.metric("Cycleway", f"{generated.get('Cycleway', 0):.0f}%")
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

    # Show curveball recommendation if available
    if st.session_state.curveball_result and st.session_state.curveball_result.get("curveball"):
        st.divider()
        st.subheader("🎲 Try Something Different!")

        curveball = st.session_state.curveball_result["curveball"]
        curveball_cluster = st.session_state.curveball_result.get("curveball_cluster_label", "Unknown")

        st.caption(f"From cluster: {curveball_cluster}")
        st.markdown(f"**{curveball['route_name']}**")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Distance", f"{curveball['distance_m']/1000:.1f} km")
        with col2:
            st.metric("Ascent", f"{curveball['ascent_m']:.0f} m")

with map_area:
    st.subheader("Route Map")
    if selected:
        route_id = selected['route_id']
        map_url = f"{API_BASE_URL}/visualize-route/{route_id}"

        try:
            # Fetch map HTML from backend
            response = requests.get(map_url, timeout=30)
            if response.status_code == 200:
                # Display Folium map HTML
                components.html(response.text, height=600, scrolling=True)
                st.caption(f"📍 Showing: {selected_route}")
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
