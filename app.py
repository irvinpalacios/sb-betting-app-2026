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
# 🎨 BROADCAST QUALITY UI (CUSTOM CSS)
# ==========================================
st.markdown("""
    <style>
    /* IMPORT FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Teko:wght@400;600;700&family=Roboto+Condensed:wght@400;700&display=swap');

    /* 1. BACKGROUND: "Levi's Stadium Night" Theme */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #1e3c72, #021124 80%);
        color: #ffffff;
    }
    .block-container { padding-top: 1.5rem; max-width: 95% !important; }

    /* 2. HEADER: TV Broadcast Style */
    .header-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 30px;
        border-bottom: 2px solid #aa0000; /* Red Accent */
        padding-bottom: 20px;
    }
    
    .super-bowl-title {
        font-family: 'Teko', sans-serif;
        font-size: 6rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 4px;
        background: linear-gradient(180deg, #ffffff 30%, #b3b3b3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
        margin: 0;
        text-shadow: 0px 4px 10px rgba(0,0,0,0.5);
    }
    
    .live-badge {
        background-color: #cc0000;
        color: white;
        padding: 5px 15px;
        font-family: 'Roboto Condensed', sans-serif;
        font-weight: 700;
        text-transform: uppercase;
        font-size: 1.2rem;
        border-radius: 4px;
        letter-spacing: 2px;
        box-shadow: 0 0 15px rgba(204, 0, 0, 0.6);
        animation: pulse-red 2s infinite;
        margin-top: 10px;
    }

    /* 3. PODIUM CONTAINER */
    .podium-container {
        display: flex;
        justify-content: center;
        align-items: flex-end;
        gap: 25px;
        margin-top: 20px;
        margin-bottom: 60px;
        height: 450px; /* Taller for grandeur */
    }

    /* 4. PILLARS: 3D Metallic Look */
    .pillar {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border-radius: 12px 12px 0 0;
        padding: 10px;
        transition: transform 0.3s ease;
        position: relative;
        /* Glossy Glass Effect */
        backdrop-filter: blur(12px);
        border-top: 1px solid rgba(255,255,255,0.4);
        box-shadow: 0 10px 40px rgba(0,0,0,0.6);
    }
    
    /* Rank Medals (Floating above) */
    .rank-circle {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Teko', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: #000;
        position: absolute;
        top: -30px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.5);
        z-index: 10;
    }

    /* 1st Place (Gold) */
    .place-1 {
        height: 100%;
        width: 320px;
        background: linear-gradient(160deg, rgba(255, 215, 0, 0.2), rgba(0,0,0,0.6));
        border: 2px solid #FFD700;
        z-index: 2;
    }
    .place-1 .rank-circle { background: radial-gradient(#FFD700, #DAA520); border: 2px solid white; }
    .place-1 .score-text { color: #FFD700; text-shadow: 0 0 20px rgba(255, 215, 0, 0.4); }

    /* 2nd Place (Silver) */
    .place-2 {
        height: 75%;
        width: 280px;
        background: linear-gradient(160deg, rgba(192, 192, 192, 0.2), rgba(0,0,0,0.6));
        border: 2px solid #C0C0C0;
        z-index: 1;
    }
    .place-2 .rank-circle { background: radial-gradient(#E0E0E0, #A9A9A9); border: 2px solid white; }
    .place-2 .score-text { color: #E0E0E0; }

    /* 3rd Place (Bronze) */
    .place-3 {
        height: 60%;
        width: 280px;
        background: linear-gradient(160deg, rgba(205, 127, 50, 0.2), rgba(0,0,0,0.6));
        border: 2px solid #CD7F32;
        z-index: 1;
    }
    .place-3 .rank-circle { background: radial-gradient(#FFA07A, #8B4513); border: 2px solid white; }
    .place-3 .score-text { color: #FF8C00; }

    /* 5. TEXT STYLING */
    .name-text {
        font-family: 'Teko', sans-serif;
        font-size: 2.5rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 30px;
        text-align: center;
        line-height: 1.1;
        width: 100%;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .score-text {
        font-family: 'Teko', sans-serif;
        font-size: 7rem;
        font-weight: 700;
        margin: -10px 0 0 0;
        line-height: 1;
    }
    
    .pts-label {
        font-family: 'Roboto Condensed', sans-serif;
        font-size: 1rem;
        text-transform: uppercase;
        opacity: 0.7;
        letter-spacing: 2px;
    }

    /* 6. TABLE STYLING */
    .stDataFrame {
        margin-top: 20px;
        border-top: 2px solid #333;
    }

    /* ANIMATIONS */
    @keyframes pulse-red {
        0% { box-shadow: 0 0 0 0 rgba(204, 0, 0, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(204, 0, 0, 0); }
        100% { box-shadow: 0 0 0 0 rgba(204, 0, 0, 0); }
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 ROBUST LOGIC & GRADING
# ==========================================
def load_data():
    try:
        # We read CSVs directly. 
        # header=0 ensures the first row is treated as headers.
        df_resp = pd.read_csv(RESPONSES_URL)
        df_key = pd.read_csv(KEY_URL)
        return df_resp, df_key
    except Exception:
        return pd.DataFrame(), pd.DataFrame()

def calculate_scores(responses, key):
    if responses.empty or key.empty:
        return pd.DataFrame(columns=['Name', 'Score'])

    # Map the Key: {Question: Answer}
    answer_map = dict(zip(key.iloc[:, 0], key.iloc[:, 1]))
    scores = []

    for _, row in responses.iterrows():
        # --- CRITICAL FIX: Safe Name Extraction ---
        # We grab the 2nd column (index 1) by Position, NOT by Name.
        # This completely ignores duplicate headers or weird "dtype" formatting.
        try:
            raw_val = row.iloc[1]
            name = str(raw_val).strip()
            if name.lower() == "nan" or name == "":
                name = "Anonymous"
        except:
            name = "Unknown"

        points = 0
        for q, correct_ans in answer_map.items():
            if q in row:
                user_ans = str(row[q]).strip().lower()
                correct_ans_str = str(correct_ans).strip().lower()
                
                # Grading Logic
                if correct_ans_str not in ["nan", "pending", ""]:
                     if user_ans == correct_ans_str:
                        points += 1
        
        scores.append({"Name": name, "Score": points})
    
    # Return sorted leaderboard
    return pd.DataFrame(scores).sort_values("Score", ascending=False)

# ==========================================
# 📺 MAIN APP DISPLAY
# ==========================================

# 1. HEADER SECTION
st.markdown("""
    <div class="header-container">
        <div class="super-bowl-title">Super Bowl LX</div>
        <div class="super-bowl-title" style="font-size: 2.5rem; color: #ccc;">Betting Challenge</div>
        <div class="live-badge">Live • Levi's Stadium</div>
    </div>
""", unsafe_allow_html=True)

placeholder = st.empty()

with placeholder.container():
    responses, key = load_data()
    
    if responses.empty:
        st.info("Waiting for data connection... (Check CSV Links)")
    else:
        # 2. CALCULATE
        df = calculate_scores(responses, key).reset_index(drop=True)
        
        # Helper to get safe data
        def get_player(idx):
            if len(df) > idx:
                return df.iloc[idx]['Name'], int(df.iloc[idx]['Score'])
            return "---", 0

        n1, s1 = get_player(0)
        n2, s2 = get_player(1)
        n3, s3 = get_player(2)

        # 3. THE PODIUM
        st.markdown(f"""
        <div class="podium-container">
            <div class="pillar place-2">
                <div class="rank-circle">2</div>
                <div class="name-text">{n2}</div>
                <div class="score-text">{s2}</div>
                <div class="pts-label">Points</div>
            </div>
            
            <div class="pillar place-1">
                <div class="rank-circle">1</div>
                <div class="name-text">{n1}</div>
                <div class="score-text">{s1}</div>
                <div class="pts-label">Current Leader</div>
            </div>
            
            <div class="pillar place-3">
                <div class="rank-circle">3</div>
                <div class="name-text">{n3}</div>
                <div class="score-text">{s3}</div>
                <div class="pts-label">Points</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 4. THE LEAGUE TABLE
        if len(df) > 3:
            st.markdown("### 🔽 The Chase Pack")
            
            # Configure a clean table view
            st.dataframe(
                df.iloc[3:],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Name": st.column_config.TextColumn("Player", width="large"),
                    "Score": st.column_config.ProgressColumn(
                        "Points",
                        format="%d",
                        min_value=0,
                        max_value=25,
                    )
                }
            )

# Auto-Refresh
time.sleep(REFRESH_RATE)
st.rerun()
