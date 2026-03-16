import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import os

API = os.getenv("API_URL", "http://localhost:8000/api/v1")

st.set_page_config(
    page_title="RecommenDISH",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}
.stApp {
    background-color: #f4f6f9;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #37607a 100%);
    border-right: 3px solid #e6820a;
}
[data-testid="stSidebar"] * {
    color: #ffffff !important;
}
.dish-card {
    background: #ffffff;
    border: 1px solid #e0e4ed;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.dish-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(55,96,122,0.15);
    border-color: #37607a;
}
.metric-card {
    background: #ffffff;
    border-top: 4px solid #e6820a;
    border-radius: 14px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.metric-value {
    font-size: 2.2rem;
    font-weight: 700;
    color: #37607a;
}
.metric-label {
    font-size: 0.8rem;
    color: #888;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.score-badge {
    display: inline-block;
    background: #e6820a;
    color: white;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
}
.tag-rule {
    background: rgba(55,96,122,0.1);
    color: #37607a;
    border: 1px solid rgba(55,96,122,0.3);
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    margin-right: 6px;
    font-weight: 500;
}
.tag-peer {
    background: rgba(46,125,50,0.1);
    color: #2e7d32;
    border: 1px solid rgba(46,125,50,0.3);
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
}
.section-header {
    font-size: 1.2rem;
    font-weight: 600;
    color: #1a1a2e;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 3px solid #e6820a;
    display: inline-block;
}
.goal-lose     { background: rgba(173,20,87,0.1);  color: #ad1457; border: 1px solid rgba(173,20,87,0.3);  padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight:500; }
.goal-gain     { background: rgba(46,125,50,0.1);  color: #2e7d32; border: 1px solid rgba(46,125,50,0.3);  padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight:500; }
.goal-maintain { background: rgba(230,130,10,0.1); color: #e6820a; border: 1px solid rgba(230,130,10,0.3); padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight:500; }
.llm-box {
    background: linear-gradient(135deg, #fff8f0, #fff3e6);
    border-left: 5px solid #e6820a;
    border-radius: 0 14px 14px 0;
    padding: 20px 24px;
    font-size: 1.05rem;
    line-height: 1.8;
    color: #2a2a2a;
    box-shadow: 0 2px 8px rgba(230,130,10,0.1);
}
.gap-bar-container {
    background: #eef0f8;
    border-radius: 8px;
    height: 8px;
    margin-top: 8px;
    overflow: hidden;
}
.gap-bar-fill {
    height: 100%;
    border-radius: 8px;
    background: linear-gradient(90deg, #37607a, #e6820a);
}
.stButton > button {
    background: linear-gradient(135deg, #37607a, #2e7d32) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 32px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    width: 100% !important;
    transition: opacity 0.2s !important;
    box-shadow: 0 4px 12px rgba(55,96,122,0.3) !important;
}
.stButton > button:hover { opacity: 0.88 !important; }
h1 { color: #1a1a2e !important; font-weight: 700 !important; }
#MainMenu {visibility: hidden;}
footer    {visibility: hidden;}
header    {visibility: hidden;}
hr { border-color: #e0e4ed !important; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────
def get_users():
    try:
        r = requests.get(f"{API}/users/")
        return r.json() if r.status_code == 200 else []
    except:
        return []

def get_foods():
    try:
        r = requests.get(f"{API}/recommend/foods/all")
        return r.json() if r.status_code == 200 else []
    except:
        return []

def goal_badge(goal):
    cls   = {"lose_weight": "goal-lose", "gain_muscle": "goal-gain", "maintain": "goal-maintain"}
    label = goal.replace("_", " ").title()
    return f'<span class="{cls.get(goal, "goal-maintain")}">{label}</span>'

def activity_stars(level):
    return "★" * level + "☆" * (5 - level)


# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 20px 0 10px;'>
        <div style='font-size:3rem;'>🍽️</div>
        <div style='font-size:1.5rem; font-weight:700; color:#e6820a;'>RecommenDISH</div>
        <div style='font-size:0.8rem; color:rgba(255,255,255,0.6); margin-top:4px;'>
            Smart Food & Nutrition
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    page = st.radio(
    "",
    ["🏠  Dashboard",
     "🤖  Recommendations",
     "🗓️  Meal Plan",
     "📊  Nutrition Dashboard",
     "👨‍🍳  Recipe Suggestions",
     "📝  Log a Meal",
     "👤  Add User",
     "🥦  Browse Foods"],
    label_visibility="collapsed"
)
    st.divider()
    st.markdown("""
    <div style='font-size:0.75rem; color:rgba(255,255,255,0.3); text-align:center;'>
        v0.1.0 — FastAPI + ML + Claude
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# PAGE: Dashboard
# ════════════════════════════════════════════════════════════
if "Dashboard" in page and "Nutrition" not in page:
    st.markdown("<h1>Welcome to RecommenDISH 🍽️</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#666; font-size:1.05rem;'>Your AI-powered personal nutrition engine</p>", unsafe_allow_html=True)
    st.divider()

    users = get_users()
    foods = get_foods()

    c1, c2, c3, c4 = st.columns(4)
    for col, val, label in [
        (c1, len(users),  "Total Users"),
        (c2, len(foods),  "Foods in DB"),
        (c3, "K-Means",   "Clustering"),
        (c4, "Apriori",   "Assoc. Rules"),
    ]:
        col.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{val}</div>
            <div class='metric-label'>{label}</div>
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("<div class='section-header'>Registered Users</div>", unsafe_allow_html=True)
    st.write("")

    if users:
        for u in users:
            st.markdown(f"""
            <div class='dish-card'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <div>
                        <div style='font-size:1.1rem; font-weight:600; color:#1a1a2e;'>{u['name']}</div>
                        <div style='color:#888; font-size:0.85rem; margin-top:4px;'>
                            {u['age']} yrs &nbsp;·&nbsp; {u['weight_kg']} kg &nbsp;·&nbsp;
                            {u['height_cm']} cm &nbsp;·&nbsp; {activity_stars(u['activity_level'])}
                        </div>
                    </div>
                    <div style='text-align:right;'>
                        {goal_badge(u['goal'])}
                        <div style='color:#aaa; font-size:0.8rem; margin-top:6px;'>Cluster {u['cluster_id']}</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.warning("No users yet. Add one from the sidebar.")


# ════════════════════════════════════════════════════════════
# PAGE: Recommendations
# ════════════════════════════════════════════════════════════
elif "Recommendations" in page:
    st.markdown("<h1>🤖 Get Recommendations</h1>", unsafe_allow_html=True)
    st.divider()

    users = get_users()
    if not users:
        st.warning("No users found. Add a user first.")
        st.stop()

    user_map = {u["name"]: u["id"] for u in users}
    selected = st.selectbox("Select User", list(user_map.keys()))
    user_id  = user_map[selected]
    user_obj = next(u for u in users if u["id"] == user_id)

    c1, c2, c3 = st.columns(3)
    c1.markdown(f"""
    <div class='dish-card' style='text-align:center;'>
        <div style='font-size:0.75rem; color:#888; text-transform:uppercase;'>Goal</div>
        <div style='margin-top:8px;'>{goal_badge(user_obj['goal'])}</div>
    </div>""", unsafe_allow_html=True)
    c2.markdown(f"""
    <div class='dish-card' style='text-align:center;'>
        <div style='font-size:0.75rem; color:#888; text-transform:uppercase;'>Activity</div>
        <div style='font-size:1.3rem; color:#e6820a; margin-top:6px;'>{activity_stars(user_obj['activity_level'])}</div>
    </div>""", unsafe_allow_html=True)
    c3.markdown(f"""
    <div class='dish-card' style='text-align:center;'>
        <div style='font-size:0.75rem; color:#888; text-transform:uppercase;'>Cluster</div>
        <div style='font-size:1.8rem; font-weight:700; color:#37607a; margin-top:4px;'>{user_obj['cluster_id']}</div>
    </div>""", unsafe_allow_html=True)

    st.divider()

    if st.button("✨ Generate My Recommendations"):
        with st.spinner("Running ML engine..."):
            r = requests.get(f"{API}/recommend/{user_id}")

        if r.status_code == 200:
            data = r.json()

            st.markdown("<div class='section-header'>🧠 AI Meal Suggestion</div>", unsafe_allow_html=True)
            st.write("")
            st.markdown(f"<div class='llm-box'>{data['llm_suggestion']}</div>", unsafe_allow_html=True)
            st.divider()

            st.markdown("<div class='section-header'>📊 Today's Nutrient Gaps</div>", unsafe_allow_html=True)
            st.write("")
            gaps = data["gaps"]
            nutrients = [
                ("Calories", gaps["calories_gap"], 2500, "kcal"),
                ("Protein",  gaps["protein_gap"],  150,  "g"),
                ("Carbs",    gaps["carbs_gap"],     300,  "g"),
                ("Fat",      gaps["fat_gap"],       80,   "g"),
                ("Fiber",    gaps["fiber_gap"],     30,   "g"),
            ]
            cols = st.columns(5)
            for col, (name, val, maxv, unit) in zip(cols, nutrients):
                pct   = min(max(val / maxv, 0), 1) * 100
                color = "#ad1457" if val < 0 else "#2e7d32"
                col.markdown(f"""
                <div class='dish-card' style='text-align:center; padding:16px;'>
                    <div style='font-size:0.75rem; color:#888; text-transform:uppercase;'>{name}</div>
                    <div style='font-size:1.5rem; font-weight:700; color:{color}; margin:8px 0;'>{val}</div>
                    <div style='font-size:0.75rem; color:#aaa;'>{unit} remaining</div>
                    <div class='gap-bar-container'>
                        <div class='gap-bar-fill' style='width:{pct}%;'></div>
                    </div>
                </div>""", unsafe_allow_html=True)

            st.divider()
            st.markdown("<div class='section-header'>🥗 Top Recommended Foods</div>", unsafe_allow_html=True)
            st.write("")

            for i, rec in enumerate(data["recommendations"], 1):
                tags = ""
                if rec["rule_match"]: tags += "<span class='tag-rule'>🔗 rule match</span>"
                if rec["peer_match"]: tags += "<span class='tag-peer'>👥 peer match</span>"
                st.markdown(f"""
                <div class='dish-card'>
                    <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
                        <div>
                            <div style='font-size:1.05rem; font-weight:600; color:#1a1a2e;'>
                                {i}. {rec['food_name']}
                                <span style='color:#aaa; font-size:0.85rem; margin-left:8px;'>{rec['category']}</span>
                            </div>
                            <div style='margin-top:8px; color:#666; font-size:0.88rem;'>
                                🔥 {rec['calories']} kcal &nbsp;&nbsp;
                                💪 {rec['protein_g']}g protein &nbsp;&nbsp;
                                🌿 {rec['fiber_g']}g fiber
                            </div>
                            <div style='margin-top:10px;'>{tags}</div>
                        </div>
                        <div><span class='score-badge'>Score {rec['score']}</span></div>
                    </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.error(f"API error: {r.status_code}")


# ════════════════════════════════════════════════════════════
# PAGE: Meal Plan
# ════════════════════════════════════════════════════════════
elif "Meal Plan" in page:
    st.markdown("<h1>🗓️ Daily Meal Plan</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#666;'>AI-generated full day Indian meal plan tailored to your goals</p>", unsafe_allow_html=True)
    st.divider()

    users = get_users()
    if not users:
        st.warning("No users found.")
        st.stop()

    user_map = {u["name"]: u["id"] for u in users}
    selected = st.selectbox("Select User", list(user_map.keys()))
    user_id  = user_map[selected]
    user_obj = next(u for u in users if u["id"] == user_id)

    c1, c2, c3 = st.columns(3)
    c1.markdown(f"""
    <div class='dish-card' style='text-align:center;'>
        <div style='font-size:0.75rem; color:#888; text-transform:uppercase;'>Goal</div>
        <div style='margin-top:8px;'>{goal_badge(user_obj['goal'])}</div>
    </div>""", unsafe_allow_html=True)
    c2.markdown(f"""
    <div class='dish-card' style='text-align:center;'>
        <div style='font-size:0.75rem; color:#888; text-transform:uppercase;'>Activity</div>
        <div style='font-size:1.3rem; color:#e6820a; margin-top:6px;'>{activity_stars(user_obj['activity_level'])}</div>
    </div>""", unsafe_allow_html=True)
    c3.markdown(f"""
    <div class='dish-card' style='text-align:center;'>
        <div style='font-size:0.75rem; color:#888; text-transform:uppercase;'>Allergies</div>
        <div style='font-size:0.95rem; color:#37607a; margin-top:6px; font-weight:500;'>{user_obj['allergies'] or 'None'}</div>
    </div>""", unsafe_allow_html=True)

    st.divider()

    if st.button("🍽️ Generate My Meal Plan"):
        with st.spinner("Crafting your personalized Indian meal plan..."):
            r = requests.get(f"{API}/recommend/mealplan/{user_id}")

        if r.status_code == 200:
            data    = r.json()
            plan    = data["meal_plan"]
            targets = data["targets"]

            st.markdown("<div class='section-header'>🎯 Daily Targets</div>", unsafe_allow_html=True)
            st.write("")
            t1, t2, t3, t4, t5 = st.columns(5)
            for col, label, val, unit in [
                (t1, "Calories", targets["calories"],   "kcal"),
                (t2, "Protein",  targets["protein_g"],  "g"),
                (t3, "Carbs",    targets["carbs_g"],    "g"),
                (t4, "Fat",      targets["fat_g"],      "g"),
                (t5, "Fiber",    targets["fiber_g"],    "g"),
            ]:
                col.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-value' style='font-size:1.5rem;'>{val}</div>
                    <div class='metric-label'>{label} ({unit})</div>
                </div>""", unsafe_allow_html=True)

            st.divider()
            st.markdown("<div class='section-header'>🍛 Your Meal Plan</div>", unsafe_allow_html=True)
            st.write("")

            meal_icons  = {"breakfast":"🌅","lunch":"☀️","snack":"🍎","dinner":"🌙"}
            meal_colors = {"breakfast":"#2e7d32","lunch":"#37607a","snack":"#e6820a","dinner":"#ad1457"}

            col1, col2 = st.columns(2)
            for i, meal in enumerate(["breakfast","lunch","snack","dinner"]):
                if meal not in plan:
                    continue
                m     = plan[meal]
                col   = col1 if i % 2 == 0 else col2
                icon  = meal_icons.get(meal, "🍽️")
                color = meal_colors.get(meal, "#37607a")
                foods_html = "".join([
                    f"<div style='padding:4px 0; border-bottom:1px solid #f0f0f0; color:#444;'>• {f}</div>"
                    for f in m.get("foods", [])
                ])
                col.markdown(f"""
                <div class='dish-card'>
                    <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;'>
                        <div style='font-size:1.1rem; font-weight:600; color:{color};'>{icon} {meal.title()}</div>
                        <span class='score-badge' style='background:{color};'>{m.get('calories',0)} kcal</span>
                    </div>
                    {foods_html}
                    <div style='margin-top:12px; padding:10px; background:#f8f9ff;
                         border-radius:8px; font-size:0.85rem; color:#666; font-style:italic;'>
                        {m.get('notes','')}
                    </div>
                    <div style='margin-top:8px; font-size:0.82rem; color:#37607a; font-weight:500;'>
                        💪 {m.get('protein_g',0)}g protein
                    </div>
                </div>""", unsafe_allow_html=True)

            st.divider()
            if "daily_total" in plan:
                total = plan["daily_total"]
                st.markdown(f"""
                <div class='llm-box'>
                    <div style='font-size:1.1rem; font-weight:600; color:#e6820a; margin-bottom:8px;'>
                        📊 Daily Summary — {total.get('calories',0)} kcal &nbsp;|&nbsp; {total.get('protein_g',0)}g protein
                    </div>
                    <div>{total.get('message','')}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.error(f"Error: {r.status_code} — {r.text}")


# ════════════════════════════════════════════════════════════
# PAGE: Nutrition Dashboard
# ════════════════════════════════════════════════════════════
elif "Nutrition" in page:
    st.markdown("<h1>📊 Nutrition Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#666;'>Your personal nutrition analytics — last 7 days</p>", unsafe_allow_html=True)
    st.divider()

    users = get_users()
    if not users:
        st.warning("No users found.")
        st.stop()

    user_map = {u["name"]: u["id"] for u in users}
    selected = st.selectbox("Select User", list(user_map.keys()))
    user_id  = user_map[selected]

    r = requests.get(f"{API}/recommend/dashboard/{user_id}")

    if r.status_code != 200:
        st.error(f"API error: {r.status_code}")
        st.stop()

    d       = r.json()
    targets = d["targets"]
    avg     = d["avg_intake"]

    st.divider()

    # Health Summary
    st.markdown("<div class='section-header'>👤 Health Summary</div>", unsafe_allow_html=True)
    st.write("")

    bmi_color = {
        "Underweight": "#37607a",
        "Normal":      "#2e7d32",
        "Overweight":  "#e6820a",
        "Obese":       "#ad1457",
    }.get(d["bmi_category"], "#37607a")

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, val, label, color in [
        (c1, d["bmi"],                           "BMI",            bmi_color),
        (c2, d["bmi_category"],                  "BMI Category",   bmi_color),
        (c3, f"{targets['calories']} kcal",      "Calorie Target", "#37607a"),
        (c4, f"{targets['protein_g']}g",         "Protein Target", "#2e7d32"),
        (c5, d["goal"].replace("_"," ").title(), "Goal",           "#e6820a"),
    ]:
        col.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value' style='font-size:1.3rem; color:{color};'>{val}</div>
            <div class='metric-label'>{label}</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # Avg Intake vs Targets
    st.markdown("<div class='section-header'>🎯 Avg Intake vs Target</div>", unsafe_allow_html=True)
    st.write("")

    c1, c2, c3, c4 = st.columns(4)
    for col, label, actual, target, color in [
        (c1, "Calories", avg["calories"], targets["calories"],  "#37607a"),
        (c2, "Protein",  avg["protein"],  targets["protein_g"], "#2e7d32"),
        (c3, "Carbs",    avg["carbs"],    targets["carbs_g"],   "#e6820a"),
        (c4, "Fat",      avg["fat"],      targets["fat_g"],     "#ad1457"),
    ]:
        pct = min(round((actual / target) * 100), 100) if target else 0
        col.markdown(f"""
        <div class='dish-card' style='text-align:center;'>
            <div style='font-size:0.8rem; color:#888; text-transform:uppercase;'>{label}</div>
            <div style='font-size:1.6rem; font-weight:700; color:{color}; margin:8px 0;'>{actual}</div>
            <div style='font-size:0.8rem; color:#aaa;'>Target: {target}</div>
            <div class='gap-bar-container'>
                <div class='gap-bar-fill' style='width:{pct}%; background:{color};'></div>
            </div>
            <div style='font-size:0.75rem; color:{color}; margin-top:4px;'>{pct}% of target</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # Weekly Calories Chart
    st.markdown("<div class='section-header'>📈 Weekly Calories</div>", unsafe_allow_html=True)
    st.write("")

    if d["daily_calories"]:
        dates = list(d["daily_calories"].keys())
        cals  = [d["daily_calories"][date]["calories"] for date in dates]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=dates, y=cals, name="Calories",
            marker_color="#37607a", opacity=0.85
        ))
        fig.add_trace(go.Scatter(
            x=dates,
            y=[targets["calories"]] * len(dates),
            mode="lines", name="Target",
            line=dict(color="#e6820a", width=2, dash="dash")
        ))
        fig.update_layout(
            paper_bgcolor="white", plot_bgcolor="#f8f9ff",
            font=dict(family="Poppins", color="#333"),
            legend=dict(orientation="h", y=1.1),
            margin=dict(l=20, r=20, t=20, b=20),
            height=300,
            xaxis=dict(gridcolor="#eee"),
            yaxis=dict(gridcolor="#eee", title="kcal"),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No meal logs in the last 7 days. Start logging meals to see charts.")

    st.divider()

    # Macro Split + Category Pie
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='section-header'>🥗 Macro Split</div>", unsafe_allow_html=True)
        st.write("")
        fig2 = go.Figure(go.Pie(
            labels=["Protein", "Carbs", "Fat"],
            values=[avg["protein"], avg["carbs"], avg["fat"]],
            hole=0.5,
            marker=dict(colors=["#2e7d32", "#37607a", "#e6820a"]),
            textfont=dict(family="Poppins"),
        ))
        fig2.update_layout(
            paper_bgcolor="white",
            font=dict(family="Poppins", color="#333"),
            margin=dict(l=10, r=10, t=10, b=10),
            height=280,
            legend=dict(orientation="h", y=-0.1)
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown("<div class='section-header'>🍱 Food Categories</div>", unsafe_allow_html=True)
        st.write("")
        if d["category_counts"]:
            cat_colors = ["#2e7d32","#37607a","#e6820a","#ad1457","#555","#888"]
            fig3 = go.Figure(go.Pie(
                labels=list(d["category_counts"].keys()),
                values=list(d["category_counts"].values()),
                hole=0.5,
                marker=dict(colors=cat_colors[:len(d["category_counts"])]),
                textfont=dict(family="Poppins"),
            ))
            fig3.update_layout(
                paper_bgcolor="white",
                font=dict(family="Poppins", color="#333"),
                margin=dict(l=10, r=10, t=10, b=10),
                height=280,
                legend=dict(orientation="h", y=-0.1)
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Log some meals to see category breakdown.")

    st.divider()

    # Top Foods + Meal Types
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='section-header'>⭐ Top 5 Foods</div>", unsafe_allow_html=True)
        st.write("")
        if d["top_foods"]:
            for food, count in d["top_foods"].items():
                st.markdown(f"""
                <div class='dish-card' style='padding:12px 16px; margin-bottom:8px;
                     display:flex; justify-content:space-between; align-items:center;'>
                    <div style='color:#1a1a2e; font-weight:500;'>{food}</div>
                    <span class='score-badge'>{count}x</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No food logs yet.")

    with col2:
        st.markdown("<div class='section-header'>🍴 Meals by Type</div>", unsafe_allow_html=True)
        st.write("")
        if d["meal_type_counts"]:
            mt_labels = list(d["meal_type_counts"].keys())
            mt_vals   = list(d["meal_type_counts"].values())
            mt_colors = ["#2e7d32","#37607a","#e6820a","#ad1457"]
            fig4 = go.Figure(go.Bar(
                x=mt_labels, y=mt_vals,
                marker_color=mt_colors[:len(mt_labels)],
                text=mt_vals, textposition="auto",
            ))
            fig4.update_layout(
                paper_bgcolor="white", plot_bgcolor="#f8f9ff",
                font=dict(family="Poppins", color="#333"),
                margin=dict(l=10, r=10, t=10, b=10),
                height=280,
                xaxis=dict(gridcolor="#eee"),
                yaxis=dict(gridcolor="#eee"),
            )
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("No meal type data yet.")


# ════════════════════════════════════════════════════════════
# PAGE: Recipe Suggestions
# ════════════════════════════════════════════════════════════
elif "Recipe" in page:
    st.markdown("<h1>👨‍🍳 Recipe Suggestions</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#666;'>Personalised Indian recipes based on your recommendations</p>", unsafe_allow_html=True)
    st.divider()

    users = get_users()
    if not users:
        st.warning("No users found.")
        st.stop()

    user_map = {u["name"]: u["id"] for u in users}
    selected = st.selectbox("Select User", list(user_map.keys()))
    user_id  = user_map[selected]
    user_obj = next(u for u in users if u["id"] == user_id)

    c1, c2 = st.columns(2)
    c1.markdown(f"""
    <div class='dish-card' style='text-align:center;'>
        <div style='font-size:0.75rem; color:#888; text-transform:uppercase;'>Goal</div>
        <div style='margin-top:8px;'>{goal_badge(user_obj['goal'])}</div>
    </div>""", unsafe_allow_html=True)
    c2.markdown(f"""
    <div class='dish-card' style='text-align:center;'>
        <div style='font-size:0.75rem; color:#888; text-transform:uppercase;'>Activity</div>
        <div style='font-size:1.3rem; color:#e6820a; margin-top:6px;'>{activity_stars(user_obj['activity_level'])}</div>
    </div>""", unsafe_allow_html=True)

    st.divider()

    if st.button("👨‍🍳 Get My Recipe"):
        with st.spinner("Finding the perfect recipe for you..."):
            r = requests.get(f"{API}/recommend/recipe/{user_id}")

        if r.status_code == 200:
            data   = r.json()
            recipe = data["recipe"]

            # Recipe header
            st.markdown(f"""
            <div class='dish-card' style='border-left: 5px solid #e6820a;'>
                <div style='font-size:1.6rem; font-weight:700; color:#1a1a2e;'>
                    🍛 {recipe['name']}
                </div>
                <div style='color:#666; margin-top:8px; font-size:1rem; line-height:1.6;'>
                    {recipe['description']}
                </div>
                <div style='margin-top:14px; display:flex; gap:16px; flex-wrap:wrap;'>
                    <span style='background:#eef0f8; color:#37607a; padding:6px 14px;
                          border-radius:20px; font-size:0.85rem; font-weight:500;'>
                        ⏱️ Prep: {recipe['prep_time']}
                    </span>
                    <span style='background:#eef0f8; color:#37607a; padding:6px 14px;
                          border-radius:20px; font-size:0.85rem; font-weight:500;'>
                        🔥 Cook: {recipe['cook_time']}
                    </span>
                    <span style='background:rgba(46,125,50,0.1); color:#2e7d32; padding:6px 14px;
                          border-radius:20px; font-size:0.85rem; font-weight:500;'>
                        💪 {recipe['protein_g']}g protein
                    </span>
                    <span style='background:rgba(230,130,10,0.1); color:#e6820a; padding:6px 14px;
                          border-radius:20px; font-size:0.85rem; font-weight:500;'>
                        🔥 {recipe['calories']} kcal
                    </span>
                    <span style='background:rgba(55,96,122,0.1); color:#37607a; padding:6px 14px;
                          border-radius:20px; font-size:0.85rem; font-weight:500;'>
                        🌿 {recipe['fiber_g']}g fiber
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.write("")

            col1, col2 = st.columns(2)

            # Ingredients
            with col1:
                st.markdown("<div class='section-header'>🛒 Ingredients</div>", unsafe_allow_html=True)
                st.write("")
                for item in recipe["ingredients"]:
                    st.markdown(f"""
                    <div style='padding:8px 12px; background:#fff; border:1px solid #e0e4ed;
                         border-radius:8px; margin-bottom:6px; color:#444; font-size:0.9rem;
                         display:flex; align-items:center; gap:8px;'>
                        <span style='color:#e6820a; font-weight:600;'>•</span> {item}
                    </div>""", unsafe_allow_html=True)

            # Steps
            with col2:
                st.markdown("<div class='section-header'>👨‍🍳 Method</div>", unsafe_allow_html=True)
                st.write("")
                for i, step in enumerate(recipe["steps"], 1):
                    st.markdown(f"""
                    <div style='padding:10px 14px; background:#fff; border:1px solid #e0e4ed;
                         border-radius:8px; margin-bottom:8px; font-size:0.9rem; color:#444;
                         display:flex; gap:12px; align-items:flex-start;'>
                        <span style='background:#37607a; color:white; border-radius:50%;
                              width:24px; height:24px; display:flex; align-items:center;
                              justify-content:center; font-size:0.75rem; font-weight:600;
                              flex-shrink:0;'>{i}</span>
                        <span style='line-height:1.6;'>{step}</span>
                    </div>""", unsafe_allow_html=True)

            st.divider()

            # Chef tip + goal tip
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class='dish-card' style='border-left:4px solid #2e7d32;'>
                    <div style='font-size:0.85rem; color:#2e7d32; font-weight:600;
                         margin-bottom:6px;'>👨‍🍳 Chef's Tip</div>
                    <div style='color:#444; font-size:0.9rem;'>{recipe['tip']}</div>
                </div>""", unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class='dish-card' style='border-left:4px solid #e6820a;'>
                    <div style='font-size:0.85rem; color:#e6820a; font-weight:600;
                         margin-bottom:6px;'>🎯 Your Goal Tip</div>
                    <div style='color:#444; font-size:0.9rem;'>{data['goal_tip']}</div>
                </div>""", unsafe_allow_html=True)

            st.divider()

            # Based on foods
            st.markdown(f"""
            <div style='color:#888; font-size:0.85rem; text-align:center;'>
                Recipe suggested based on your top recommended foods:
                <strong style='color:#37607a;'>{', '.join(data['based_on_foods'])}</strong>
            </div>""", unsafe_allow_html=True)

        else:
            st.error(f"Error: {r.status_code} — {r.text}")



# ════════════════════════════════════════════════════════════
# PAGE: Log a Meal
# ════════════════════════════════════════════════════════════
elif "Log" in page:
    st.markdown("<h1>📝 Log a Meal</h1>", unsafe_allow_html=True)
    st.divider()

    users = get_users()
    foods = get_foods()

    if not users or not foods:
        st.warning("Need at least one user and food in database.")
        st.stop()

    user_map = {u["name"]: u["id"] for u in users}
    food_map = {f["name"]: f["id"] for f in foods}

    with st.form("log_meal_form"):
        c1, c2 = st.columns(2)
        with c1:
            selected_user = st.selectbox("👤 User",      list(user_map.keys()))
            selected_food = st.selectbox("🥘 Food",      list(food_map.keys()))
        with c2:
            meal_type = st.selectbox("🍴 Meal Type", ["breakfast","lunch","dinner","snack"])
            portion   = st.number_input("⚖️ Portion (grams)", min_value=10, max_value=1000, value=100, step=10)
        rating = st.select_slider("⭐ Rating", options=[1,2,3,4,5], value=3)
        submit = st.form_submit_button("Log Meal ✓")

    if submit:
        payload = {
            "food_id":   food_map[selected_food],
            "meal_type": meal_type,
            "portion_g": portion,
            "rating":    rating,
        }
        r = requests.post(f"{API}/meals/{user_map[selected_user]}", json=payload)
        if r.status_code == 200:
            st.success(f"✅ Logged **{selected_food}** ({portion}g) for **{selected_user}**!")
            st.balloons()
        else:
            st.error(f"Error: {r.text}")


# ════════════════════════════════════════════════════════════
# PAGE: Add User
# ════════════════════════════════════════════════════════════
elif "Add User" in page:
    st.markdown("<h1>👤 Add New User</h1>", unsafe_allow_html=True)
    st.divider()

    with st.form("add_user_form"):
        c1, c2 = st.columns(2)
        with c1:
            name     = st.text_input("Full Name")
            email    = st.text_input("Email")
            age      = st.number_input("Age", 10, 100, 25)
            sex      = st.selectbox("Sex", ["male","female","other"])
        with c2:
            weight   = st.number_input("Weight (kg)", 30.0, 200.0, 70.0)
            height   = st.number_input("Height (cm)", 100.0, 220.0, 170.0)
            activity = st.select_slider(
                "Activity Level", options=[1,2,3,4,5], value=3,
                format_func=lambda x: {
                    1:"😴 Sedentary", 2:"🚶 Light",
                    3:"🏃 Moderate",  4:"💪 Active",
                    5:"🔥 Very Active"
                }[x]
            )
            goal = st.selectbox(
                "Goal",
                ["lose_weight","maintain","gain_muscle"],
                format_func=lambda x: {
                    "lose_weight": "🎯 Lose Weight",
                    "maintain":    "⚖️ Maintain",
                    "gain_muscle": "💪 Gain Muscle"
                }[x]
            )
        allergies  = st.text_input("Allergies (comma separated)", placeholder="e.g. gluten, dairy")
        conditions = st.text_input("Health Conditions (comma separated)", placeholder="e.g. diabetes")
        submitted  = st.form_submit_button("Create User ✓")

    if submitted:
        if not name or not email:
            st.error("Name and email are required.")
        else:
            payload = {
                "name": name, "email": email, "age": age,
                "weight_kg": weight, "height_cm": height,
                "sex": sex, "activity_level": activity,
                "goal": goal, "allergies": allergies,
                "conditions": conditions,
            }
            r = requests.post(f"{API}/users/", json=payload)
            if r.status_code == 200:
                st.success(f"✅ Welcome to RecommenDISH, **{name}**!")
                st.balloons()
            else:
                st.error(f"Error: {r.json().get('detail', r.text)}")


# ════════════════════════════════════════════════════════════
# PAGE: Browse Foods
# ════════════════════════════════════════════════════════════
elif "Browse" in page:
    st.markdown("<h1>🥦 Browse Foods</h1>", unsafe_allow_html=True)
    st.divider()

    foods = get_foods()
    if not foods:
        st.warning("No foods in database.")
        st.stop()

    df = pd.DataFrame(foods)

    c1, c2 = st.columns(2)
    with c1:
        categories  = ["All"] + sorted(df["category"].unique().tolist())
        cat_filter  = st.selectbox("Category", categories)
    with c2:
        diet_filter = st.selectbox("Diet", ["All","Vegetarian","Vegan","Gluten Free"])

    filtered = df.copy()
    if cat_filter != "All":
        filtered = filtered[filtered["category"] == cat_filter]
    if diet_filter == "Vegetarian":
        filtered = filtered[filtered["is_vegetarian"] == True]
    elif diet_filter == "Vegan":
        filtered = filtered[filtered["is_vegan"] == True]
    elif diet_filter == "Gluten Free":
        filtered = filtered[filtered["is_gluten_free"] == True]

    st.markdown(f"<div style='color:#888; margin-bottom:12px;'>Showing {len(filtered)} foods</div>",
                unsafe_allow_html=True)

    display = filtered[["name","category","calories","protein_g","carbs_g","fat_g","fiber_g"]].copy()
    display.columns = ["Name","Category","Calories","Protein (g)","Carbs (g)","Fat (g)","Fiber (g)"]

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Calories":    st.column_config.NumberColumn(format="%.0f kcal"),
            "Protein (g)": st.column_config.ProgressColumn(min_value=0, max_value=40),
            "Fiber (g)":   st.column_config.ProgressColumn(min_value=0, max_value=20),
        }
    )