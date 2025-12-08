import json
from typing import Any, Dict, List

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Route Dashboard", layout="wide")

if "entered" not in st.session_state:
    st.session_state.entered = False

st.markdown(
    """
    <style>
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
        "Unknown_Surface": 0.0,
        "Paved_Road": 0.4,
        "Pedestrian": 0.0,
        "Unknown_Way": 0.0,
        "Cycle_Track": 0.15,
    }
}

# Placeholder recommendations copied from the API response body screenshot.
recommendations_sample: List[Dict[str, Any]] = [
    {
        "route_id": 14349467,
        "route_name": "Ciclovia Pedemontana Alpina",
        "distance_m": 89292.3,
        "ascent_m": 1354,
        "duration_s": 18702.4,
        "turn_density": 2.01585130807315,
        "similarity_score": 0.0349585319495986,
    },
    {
        "route_id": 16478126,
        "route_name": "Dal Lago di Garda a Venezia (Alternative, escursioni e collegamenti)",
        "distance_m": 156841.6,
        "ascent_m": 1554.8,
        "duration_s": 32059.8,
        "turn_density": 1.6449717421908474,
        "similarity_score": 0.0379780633594286,
    },
    {
        "route_id": 12688705,
        "route_name": "Unnamed route",
        "distance_m": 106648.6,
        "ascent_m": 1012.4,
        "duration_s": 21740.6,
        "turn_density": 1.622215331102909,
        "similarity_score": 0.0321011709186368,
    },
    {
        "route_id": 9876543,
        "route_name": "Scenic River Loop",
        "distance_m": 45678.0,
        "ascent_m": 780.0,
        "duration_s": 13200.0,
        "turn_density": 1.1,
        "similarity_score": 0.028,
    },
    {
        "route_id": 1928374,
        "route_name": "Coastal Explorer",
        "distance_m": 80200.5,
        "ascent_m": 930.2,
        "duration_s": 16840.3,
        "turn_density": 1.42,
        "similarity_score": 0.0314,
    },
]


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


header = st.container()
with header:
    route_col, count_col, action_col = st.columns([3, 1, 1])
    raw_features = route_col.text_area(
        "Enter route (JSON request body)",
        value=json.dumps(default_features, indent=2),
        height=220,
        help="Paste the features JSON you send to /recommend.",
    )
    n_recs = count_col.number_input(
        "Number of recommendations",
        min_value=1,
        max_value=10,
        value=5,
        step=1,
    )
    run_query = action_col.button("Get recommendations", use_container_width=True)

st.divider()

# Normally you would POST raw_features to the API; here we use the sample data.
parsed_features: Dict[str, Any] | None = None
if run_query:
    try:
        parsed_features = json.loads(raw_features)
        st.success("Parsed features JSON. (Sample data shown below.)")
    except json.JSONDecodeError as exc:
        st.error(f"Invalid JSON: {exc}")

sidebar, map_area = st.columns([1, 2], gap="large")

with sidebar:
    st.subheader("Recommended Routes")
    route_names = [rec["route_name"] for rec in recommendations_sample][: n_recs or 5]
    selected_route = st.selectbox("Route", route_names, index=0 if route_names else None)

    selected = next((rec for rec in recommendations_sample if rec["route_name"] == selected_route), None)

    st.subheader("KPIs")
    if selected:
        st.metric("Distance (m)", f"{selected['distance_m']:.0f}")
        st.metric("Ascent (m)", f"{selected['ascent_m']:.0f}")
        st.metric("Duration", format_duration(selected["duration_s"]))
        st.metric("Turn Density", f"{selected['turn_density']:.2f}")
        st.metric("Similarity Score", f"{selected['similarity_score']:.4f}")
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
with st.expander("Raw recommendations (sample)"):
    st.json(recommendations_sample)
