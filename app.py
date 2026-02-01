import streamlit as st
import pandas as pd
import time
import altair as alt

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
# REPLACE THESE WITH YOUR "PUBLISHED TO WEB" CSV LINKS
RESPONSES_URL = "YOUR_RESPONSES_SHEET_CSV_URL_HERE"
KEY_URL = "YOUR_KEY_SHEET_CSV_URL_HERE"

REFRESH_RATE = 30  # Seconds between auto-updates

st.set_page_config(
    page_title="SB LX Leaderboard",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 🎨 CUSTOM CSS (The "Vibrant TV" Look)
# ==========================================
st.markdown("""
    <style>
    /* Global Dark Theme Adjustments */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Title Styling */
    h1 {
        text-align: center;
        text-transform: uppercase;
        background: -webkit-linear-gradient(45deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        margin-bottom: 0px;
    }

    /* Podium Container */
    .podium-container {
        display: flex;
        justify-content: center;
        align-items: flex-end;
        gap: 15px;
        margin-top: 20px;
        margin-bottom: 40px;
        height: 300px;
    }

    /* Podium Pillars */
    .pillar {
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        align-items: center;
        border-radius: 15px 15px 0 0;
        padding: 20px;
        transition: all 0.5s ease-in-out;
        box-shadow: 0 0 20px rgba(0,0,0,0.5);
    }

    /* 1st Place (Gold) */
    .place-1 {
        height: 100%;
        width: 32%;
        background: linear-gradient(180deg, #FFD700 0%, #B8860B 100%);
        border: 2px solid #FFD700;
        z-index: 2;
        transform: scale(1.05);
    }

    /* 2nd Place (Silver) */
    .place-2 {
        height: 85%;
        width: 28%;
        background: linear-gradient(180deg, #C0C0C0 0%, #7f8c8d 100%);
        border: 2px solid #C0C0C0;
        z-index: 1;
    }

    /* 3rd Place (Bronze) */
    .place-3 {
        height: 70%;
        width: 28%;
        background: linear-gradient(180deg, #CD7F32 0%, #8d5524 100%);
        border: 2px solid #CD7F32;
        z-index: 1;
    }

    /* Text inside Podium */
    .medal-icon { font-size: 3rem; margin-bottom: 10px; }
    .podium-name { font-size: 1.8rem; font-weight: bold; color: white; text-shadow: 2px 2px 4px black; text-align: center; line-height: 1.1;}
    .podium-score { font-size: 2.5rem; font-weight: 900; color: white; margin-top: 10px; text-shadow: 2px 2px 4px black; }

    /* Table Styling */
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 LOGIC & GRADING
# ==========================================
def load_data():
    try:
        df_resp = pd.read_csv(RESPONSES_URL)
        df_key = pd.read_csv(KEY_URL)
        # Basic cleanup: Ensure column 2 is the 'Name' column in responses
        if not df_resp.empty:
            df_resp = df_resp.rename(columns={df_resp.columns[1]: 'Name'})
        return df_resp, df_key
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame()

def calculate_scores(responses, key):
    if responses.empty or key.empty:
        return pd.DataFrame(columns=['Name', 'Score'])

    answer_map = dict(zip(key.iloc[:, 0], key.iloc[:, 1]))
    scores = []

    for _, row in responses.iterrows():
        name = str(row['Name'])
        points = 0
        for q, correct_ans in answer_map.items():
            if q in row:
                user_ans = str(row[q]).strip().lower()
                correct_ans_str = str(correct_ans).strip().lower()
                # Fuzzy matching: Check if answer is contained (e.g. "Yes" matches "Yes - confirmed")
                if correct_ans_str != "nan" and correct_ans_str != "pending":
                     if user_ans == correct_ans_str:
                        points += 1
        scores.append({"Name": name, "Score": points})
    
    return pd.DataFrame(scores).sort_values("Score", ascending=False)

# ==========================================
# 📺 APP EXECUTION
# ==========================================

# 1. State Management for animations
if 'prev_leader' not in st.session_state:
    st.session_state.prev_leader = None

st.title("🏈 SUPER BOWL LX BETTING CHALLENGE 🏈")
st.markdown("<p style='text-align: center; color: #888;'>LIVE FROM LEVI'S STADIUM</p>", unsafe_allow_html=True)

# 2. Data Refresh
placeholder = st.empty()

# Create a container for the loop to keep the layout stable
with placeholder.container():
    responses, key = load_data()
    
    if responses.empty:
        st.warning("Waiting for bets... (Check CSV Link)")
    else:
        # Calculate Leaderboard
        df = calculate_scores(responses, key)
        df = df.reset_index(drop=True)
        
        # Check for Leader Change (Animation Trigger)
        current_leader = df.iloc[0]['Name'] if not df.empty else None
        if st.session_state.prev_leader and current_leader != st.session_state.prev_leader:
            st.balloons()
            st.toast(f"🚨 NEW LEADER: {current_leader}!", icon="👑")
        st.session_state.prev_leader = current_leader

        # --- THE PODIUM (Visual HTML) ---
        # Safe checks for less than 3 players
        p1 = df.iloc[0] if len(df) > 0 else {"Name": "---", "Score": 0}
        p2 = df.iloc[1] if len(df) > 1 else {"Name": "---", "Score": 0}
        p3 = df.iloc[2] if len(df) > 2 else {"Name": "---", "Score": 0}

        st.markdown(f"""
        <div class="podium-container">
            <div class="pillar place-2">
                <div class="medal-icon">🥈</div>
                <div class="podium-name">{p2['Name']}</div>
                <div class="podium-score">{p2['Score']}</div>
            </div>
            <div class="pillar place-1">
                <div class="medal-icon">👑</div>
                <div class="podium-name">{p1['Name']}</div>
                <div class="podium-score">{p1['Score']}</div>
            </div>
            <div class="pillar place-3">
                <div class="medal-icon">🥉</div>
                <div class="podium-name">{p3['Name']}</div>
                <div class="podium-score">{p3['Score']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # --- THE REST OF THE PACK ---
        if len(df) > 3:
            st.markdown("### 🏃 The Chasers")
            
            # Use Streamlit's new column config for a pretty bar chart in the table
            st.dataframe(
                df.iloc[3:],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Name": "Player",
                    "Score": st.column_config.ProgressColumn(
                        "Points",
                        format="%d",
                        min_value=0,
                        max_value=25,
                        help="Current Score out of 25"
                    )
                }
            )

# Auto-Refresh Logic (Manual workaround for Streamlit loop)
time.sleep(REFRESH_RATE)
st.rerun()
