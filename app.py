import streamlit as st
import pandas as pd
import time

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
# REPLACE THESE WITH YOUR ACTUAL CSV LINKS
RESPONSES_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRM-EfkmrH7kIB4hNaudn9Ks3ajIh4vTURC55xDWi9EYa6LAaCFzJsNvfSIz7fFTV_Ufb3fezm_yGN8/pub?gid=949196677&single=true&output=csv"
KEY_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRM-EfkmrH7kIB4hNaudn9Ks3ajIh4vTURC55xDWi9EYa6LAaCFzJsNvfSIz7fFTV_Ufb3fezm_yGN8/pub?gid=1997150247&single=true&output=csv"

REFRESH_RATE = 30  # Seconds between auto-updates

st.set_page_config(
    page_title="SB LX Leaderboard",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 🎨 UI/UX DESIGN (CUSTOM CSS)
# ==========================================
st.markdown("""
    <style>
    /* IMPORT SPORTS FONT */
    @import url('https://fonts.googleapis.com/css2?family=Teko:wght@300;500;700&display=swap');

    /* 1. BACKGROUND & BASICS */
    .stApp {
        background: radial-gradient(circle at center, #1a2a6c, #0d1117);
        color: #ffffff;
    }
    .block-container { padding-top: 1rem; }

    /* 2. HEADER TYPOGRAPHY */
    h1 {
        font-family: 'Teko', sans-serif;
        text-transform: uppercase;
        background: linear-gradient(90deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 5rem !important;
        font-weight: 700 !important;
        text-align: center;
        margin-bottom: 0px;
        letter-spacing: 2px;
        text-shadow: 0px 0px 20px rgba(0, 210, 255, 0.3);
    }
    p { font-family: 'Helvetica Neue', sans-serif; }

    /* 3. PODIUM CONTAINER */
    .podium-container {
        display: flex;
        justify-content: center;
        align-items: flex-end;
        gap: 20px;
        margin-top: 40px;
        margin-bottom: 60px;
        height: 350px;
    }

    /* 4. PODIUM PILLARS (Glassmorphism) */
    .pillar {
        display: flex;
        flex-direction: column;
        justify-content: flex-start; /* Align text to top */
        align-items: center;
        border-radius: 15px 15px 0 0;
        padding: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.3s ease;
        position: relative;
    }
    
    /* 1st Place (Gold) */
    .place-1 {
        height: 100%;
        width: 300px;
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.8), rgba(184, 134, 11, 0.9));
        border: 1px solid rgba(255, 255, 255, 0.3);
        z-index: 2;
        box-shadow: 0 0 50px rgba(255, 215, 0, 0.4);
        animation: pulse 3s infinite;
    }

    /* 2nd Place (Silver) */
    .place-2 {
        height: 75%;
        width: 250px;
        background: linear-gradient(135deg, rgba(192, 192, 192, 0.8), rgba(128, 128, 128, 0.9));
        border: 1px solid rgba(255, 255, 255, 0.2);
        z-index: 1;
    }

    /* 3rd Place (Bronze) */
    .place-3 {
        height: 60%;
        width: 250px;
        background: linear-gradient(135deg, rgba(205, 127, 50, 0.8), rgba(139, 69, 19, 0.9));
        border: 1px solid rgba(255, 255, 255, 0.2);
        z-index: 1;
    }

    /* 5. TEXT STYLING IN PODIUM */
    .medal { font-size: 4rem; margin-top: -40px; margin-bottom: 10px; filter: drop-shadow(0 0 10px rgba(0,0,0,0.5)); }
    
    .player-name {
        font-family: 'Teko', sans-serif;
        font-size: 2.2rem;
        font-weight: 500;
        color: #ffffff;
        text-transform: uppercase;
        line-height: 1;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        margin-bottom: 5px;
        max-width: 100%;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .player-score {
        font-family: 'Teko', sans-serif;
        font-size: 5rem;
        font-weight: 700;
        color: #fff;
        text-shadow: 4px 4px 0px rgba(0,0,0,0.2);
        margin: 0;
        line-height: 1;
    }
    
    .player-sub { font-size: 1rem; opacity: 0.8; font-weight: 300; }

    /* 6. TABLE STYLING */
    .stDataFrame {
        border-radius: 10px;
        box-shadow: 0 0 20px rgba(0,0,0,0.5);
    }

    /* ANIMATION */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 LOGIC & GRADING
# ==========================================
def load_data():
    try:
        df_resp = pd.read_csv(RESPONSES_URL)
        df_key = pd.read_csv(KEY_URL)
        # Rename Column 2 to 'Name' safely
        if not df_resp.empty:
            df_resp = df_resp.rename(columns={df_resp.columns[1]: 'Name'})
        return df_resp, df_key
    except Exception:
        return pd.DataFrame(), pd.DataFrame()

def calculate_scores(responses, key):
    if responses.empty or key.empty:
        return pd.DataFrame(columns=['Name', 'Score'])

    answer_map = dict(zip(key.iloc[:, 0], key.iloc[:, 1]))
    scores = []

    for _, row in responses.iterrows():
        # --- FIX: FORCE STRING CONVERSION ---
        # This prevents the "dtype: object" error in the UI
        name_raw = row['Name']
        name = str(name_raw).strip() if pd.notna(name_raw) else "Anonymous"
        
        points = 0
        for q, correct_ans in answer_map.items():
            if q in row:
                user_ans = str(row[q]).strip().lower()
                correct_ans_str = str(correct_ans).strip().lower()
                
                # Logic: If key is not empty/pending, grade it
                if correct_ans_str not in ["nan", "pending", ""]:
                     if user_ans == correct_ans_str:
                        points += 1
        scores.append({"Name": name, "Score": points})
    
    return pd.DataFrame(scores).sort_values("Score", ascending=False)

# ==========================================
# 📺 APP DISPLAY
# ==========================================
st.title("🏆 SUPER BOWL LX 🏆")
st.markdown("<p style='text-align: center; color: #aab; font-size: 1.2rem; letter-spacing: 1px;'>LIVE BETTING CHALLENGE • LEVI'S STADIUM</p>", unsafe_allow_html=True)

placeholder = st.empty()

with placeholder.container():
    responses, key = load_data()
    
    if responses.empty:
        st.info("Waiting for data connection...")
    else:
        # Calculate & Sort
        df = calculate_scores(responses, key).reset_index(drop=True)
        
        # --- FIX: SAFE DATA EXTRACTION FOR PODIUM ---
        # We define a helper to get safe strings/ints, handling empty lists
        def get_player(idx):
            if len(df) > idx:
                return df.iloc[idx]['Name'], int(df.iloc[idx]['Score'])
            return "---", 0

        n1, s1 = get_player(0)
        n2, s2 = get_player(1)
        n3, s3 = get_player(2)

        # HTML PODIUM
        st.markdown(f"""
        <div class="podium-container">
            <div class="pillar place-2">
                <div class="medal">🥈</div>
                <div class="player-name">{n2}</div>
                <div class="player-score">{s2}</div>
                <div class="player-sub">POINTS</div>
            </div>
            
            <div class="pillar place-1">
                <div class="medal">👑</div>
                <div class="player-name">{n1}</div>
                <div class="player-score">{s1}</div>
                <div class="player-sub">LEADER</div>
            </div>
            
            <div class="pillar place-3">
                <div class="medal">🥉</div>
                <div class="player-name">{n3}</div>
                <div class="player-score">{s3}</div>
                <div class="player-sub">POINTS</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # THE CHASERS LIST
        if len(df) > 3:
            st.markdown("### 🏃 THE CHASE PACK")
            st.dataframe(
                df.iloc[3:],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Name": st.column_config.TextColumn("Player Name", width="medium"),
                    "Score": st.column_config.ProgressColumn(
                        "Total Score",
                        format="%d",
                        min_value=0,
                        max_value=25,
                    )
                }
            )

# Auto-Refresh
time.sleep(REFRESH_RATE)
st.rerun()
