from pathlib import Path
import csv
from datetime import datetime

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "balcony_crops.csv"
FEEDBACK_PATH = BASE_DIR / "data" / "sample_feedback.csv"

st.set_page_config(
    page_title="Balcony Crop Advisor",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
    :root { --ink:#17342a; --muted:#60746b; --leaf:#237a4b; --mint:#e6f2e8; --sun:#f5b83d; --paper:#fbfaf6; }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background: var(--paper); color: var(--ink); }
    [data-testid="stSidebar"] { background:#17342a; }
    [data-testid="stSidebar"] * { color:#f2f6ed !important; }
    [data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div { background-color:#8ac79a; }
    h1, h2, h3 { font-family:'Playfair Display', serif; color:var(--ink); }
    .hero { padding: 2.2rem 0 1.3rem; border-bottom:1px solid #d9e4d8; }
    .eyebrow { color:var(--leaf); font-size:.78rem; font-weight:700; letter-spacing:.14em; text-transform:uppercase; }
    .hero h1 { font-size:clamp(2.3rem, 5vw, 4.5rem); line-height:1.03; margin:.4rem 0 .8rem; max-width:800px; }
    .hero p { color:var(--muted); font-size:1.08rem; max-width:680px; line-height:1.6; }
    .stat { background:white; border:1px solid #dde8dc; border-radius:8px; padding:1rem 1.1rem; height:100%; }
    .stat strong { display:block; color:var(--leaf); font-size:1.45rem; }
    .stat span { color:var(--muted); font-size:.82rem; }
    .crop-card { background:white; border:1px solid #dce8dc; border-radius:8px; padding:1.2rem; margin-bottom:.8rem; box-shadow:0 4px 16px rgba(23,52,42,.04); }
    .crop-top { display:flex; justify-content:space-between; align-items:start; gap:1rem; }
    .crop-name { font-family:'Playfair Display', serif; font-size:1.45rem; color:var(--ink); }
    .crop-meta { color:var(--muted); font-size:.88rem; margin:.2rem 0 .9rem; }
    .score { background:var(--mint); color:var(--leaf); font-weight:700; padding:.42rem .7rem; border-radius:20px; white-space:nowrap; }
    .reason { color:#3f5a4d; font-size:.92rem; line-height:1.5; border-left:3px solid var(--sun); padding-left:.75rem; }
    .tag { display:inline-block; background:#f1f5ed; color:#41634d; border-radius:4px; padding:.3rem .5rem; margin:.2rem .25rem .1rem 0; font-size:.76rem; }
    .stButton > button { background:var(--sun); color:#17342a; border:0; border-radius:5px; font-weight:700; min-height:2.7rem; }
    .stButton > button:hover { background:#e8a92c; color:#17342a; }
    </style>
    """,
    unsafe_allow_html=True,
)


def range_score(value: float, minimum: float, maximum: float) -> float:
    if minimum <= value <= maximum:
        return 100.0
    distance = minimum - value if value < minimum else value - maximum
    return max(0.0, min(100.0, 100 - (distance / max(maximum - minimum, 1)) * 100))


def categorical_score(user_value: str, crop_value: str) -> float:
    if crop_value == "All" or user_value.lower() == crop_value.lower():
        return 100.0
    return 45.0


def rank_crops(inputs: dict, crops: pd.DataFrame) -> pd.DataFrame:
    weights = {"sun": .25, "temp": .20, "pot": .15, "space": .10, "water": .10, "season": .10, "wind": .05, "experience": .05}
    results = []
    for _, crop in crops.iterrows():
        scores = {
            "sun": range_score(inputs["sunlight"], crop.min_sunlight, crop.max_sunlight),
            "temp": range_score(inputs["temperature"], crop.min_temp, crop.max_temp),
            "pot": range_score(inputs["pot_liters"], crop.min_pot_liters, crop.min_pot_liters * 3),
            "space": range_score(inputs["space_sqft"], crop.min_space_sqft, crop.min_space_sqft * 5),
            "water": 100 if inputs["water"] == crop.water_need or (inputs["water"] == "High" and crop.water_need != "High") else (75 if inputs["water"] == "Medium" else (100 if crop.water_need == "Low" else 35)),
            "season": categorical_score(inputs["season"], crop.season),
            "wind": 100 if inputs["wind"] == crop.wind_tolerance else (55 if inputs["wind"] == "Low" else 70),
            "experience": 100 if inputs["experience"] == crop.difficulty or (inputs["experience"] == "Advanced") else (65 if crop.difficulty == "Medium" else 90),
        }
        final_score = sum(scores[key] * weight for key, weight in weights.items())
        reasons = []
        if scores["sun"] >= 90: reasons.append("your sunlight is a strong match")
        elif scores["sun"] < 60: reasons.append("it may need a brighter or shadier spot")
        if scores["temp"] >= 90: reasons.append("the temperature suits it")
        if scores["pot"] >= 90: reasons.append("your pot size gives its roots room")
        if scores["water"] >= 90: reasons.append(f"its {crop.water_need.lower()} water needs fit your routine")
        results.append({**crop.to_dict(), "score": round(final_score), "reason": "; ".join(reasons[:3]).capitalize() + "."})
    return pd.DataFrame(results).sort_values("score", ascending=False).head(5)


@st.cache_data
def load_crops() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


def save_feedback(inputs: dict, crop_name: str, success: str) -> None:
    row = {"timestamp": datetime.now().isoformat(timespec="seconds"), "crop_name": crop_name, "success": success, **inputs}
    file_exists = FEEDBACK_PATH.exists()
    with FEEDBACK_PATH.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=row.keys())
        if not file_exists: writer.writeheader()
        writer.writerow(row)


crops = load_crops()
st.markdown('<div class="hero"><div class="eyebrow">Container gardening, made personal</div><h1>Find the right crops for your balcony.</h1><p>Tell us what your growing space is like. We will rank crops that fit your light, climate, container, water, and experience.</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Your balcony")
    st.caption("Tune the conditions below, then run the advisor.")
    sunlight = st.slider("Direct sunlight per day", 1, 10, 5, help="Count the hours of direct sun reaching your pots.")
    temperature = st.slider("Average temperature (°C)", 5, 40, 28)
    pot_liters = st.slider("Largest pot size (litres)", 3, 60, 15)
    space_sqft = st.slider("Available growing space (sq ft)", 1, 50, 8)
    season = st.selectbox("Growing season", ["All", "Summer", "Winter"])
    water = st.selectbox("Water availability", ["High", "Medium", "Low"], index=1)
    wind = st.selectbox("Wind level", ["Low", "Medium", "High"], index=1)
    experience = st.selectbox("Gardening experience", ["Beginner", "Medium", "Advanced"])
    preferred_type = st.selectbox("What would you like to grow?", ["Any", "Vegetable", "Herb", "Leafy", "Root", "Fruit"])
    recommend = st.button("Recommend crops", use_container_width=True, type="primary")

inputs = {"sunlight": sunlight, "temperature": temperature, "pot_liters": pot_liters, "space_sqft": space_sqft, "season": season, "water": water, "wind": wind, "experience": experience}
if "results" not in st.session_state or recommend:
    filtered = crops if preferred_type == "Any" else crops[crops.crop_type == preferred_type]
    st.session_state.results = rank_crops(inputs, filtered if not filtered.empty else crops)
    st.session_state.inputs = inputs
results = st.session_state.results

cols = st.columns(4)
for col, value, label in zip(cols, [f"{sunlight} hrs", f"{temperature}°C", f"{pot_liters} L", f"{space_sqft} sq ft"], ["Direct light", "Temperature", "Largest pot", "Growing room"]):
    with col: st.markdown(f'<div class="stat"><strong>{value}</strong><span>{label}</span></div>', unsafe_allow_html=True)

st.markdown("## Your top matches")
st.caption("Transparent scores based on the weighted conditions in the project blueprint. Treat these as a helpful starting point, not a guarantee.")
for _, crop in results.iterrows():
    st.markdown(f'''<div class="crop-card"><div class="crop-top"><div><div class="crop-name">{crop.crop_name.replace("_", " ")}</div><div class="crop-meta">{crop.crop_type} · {crop.difficulty} · {crop.growth_days} days</div></div><div class="score">{crop.score}% match</div></div><span class="tag">☀ {crop.min_sunlight}-{crop.max_sunlight} hrs sun</span><span class="tag">◉ {crop.min_pot_liters} L+ pot</span><span class="tag">💧 {crop.water_need} water</span><span class="tag">◇ {crop.season} season</span><p class="reason">{crop.reason}</p><small>{crop.care}</small></div>''', unsafe_allow_html=True)

st.markdown("## What should we improve?")
tab1, tab2 = st.tabs(["Save growing feedback", "About this model"])
with tab1:
    selected = st.selectbox("Crop you tried", results.crop_name.tolist())
    outcome = st.radio("How did it perform?", ["Growing well", "Struggled or failed"], horizontal=True)
    if st.button("Save feedback"):
        save_feedback(st.session_state.inputs, selected, "1" if outcome == "Growing well" else "0")
        st.success("Feedback saved locally. It can become training data for the future ML upgrade.")
with tab2:
    st.write("This version uses a hybrid, rule-based ranking because the starter dataset describes crop requirements but does not contain enough real success and failure examples for a reliable supervised model.")
    st.write("Weights: sunlight 25%, temperature 20%, pot 15%, space 10%, water 10%, season 10%, wind 5%, experience 5%.")
    st.write(f"Loaded {len(crops)} balcony-friendly crops from the local dataset.")
