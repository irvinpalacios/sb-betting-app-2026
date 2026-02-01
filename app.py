import streamlit as st
import pandas as pd
import time
import altair as alt
import random

# Must be the first Streamlit command
st.set_page_config(layout="wide", page_title="Super Bowl LX ") 

# Hide the Streamlit structure
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            div[data-testid="stToolbar"] {visibility: hidden;}
            div[data-testid="stDecoration"] {visibility: hidden;}
            div[data-testid="stStatusWidget"] {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

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
    .block-container { padding-top: 1rem; max-width: 95% !important; }

    /* 2. HEADER */
    .header-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 20px;
        border-bottom: 2px solid #aa0000;
        padding-bottom: 20px;
    }
    .super-bowl-title {
        font-family: 'Teko', sans-serif;
        font-size: 6rem;
        font-weight: 700;
        font-style: italic;
        text-transform: uppercase;
        letter-spacing: 4px;
        background: linear-gradient(180deg, #ffffff 30%, #b3b3b3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
        margin: 0;
        text-shadow: 0px 4px 10px rgba(0,0,0,0.5);
    }
    .badge-container {
        display: flex;
        gap: 15px;
        margin-top: 10px;
        justify-content: center;
        align-items: center;
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
    }
    .points-remaining-badge {
        background-color: #1e5a9e;
        color: white;
        padding: 5px 15px;
        font-family: 'Roboto Condensed', sans-serif;
        font-weight: 700;
        text-transform: uppercase;
        font-size: 1.2rem;
        border-radius: 4px;
        letter-spacing: 2px;
        box-shadow: 0 0 15px rgba(30, 90, 158, 0.6);
    }

    /* 3. PODIUM CONTAINER */
    .podium-container {
        display: flex;
        justify-content: center;
        align-items: flex-end;
        gap: 20px;
        margin-top: 20px;
        margin-bottom: 30px;
        height: 400px;
    }

    /* 4. PILLARS & CARDS */
    .pillar {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border-radius: 12px 12px 0 0;
        padding: 10px;
        transition: transform 0.3s ease;
        position: relative;
        backdrop-filter: blur(12px);
        border-top: 1px solid rgba(255,255,255,0.4);
        box-shadow: 0 10px 40px rgba(0,0,0,0.6);
    }
    
    /* Stats Cards (New Feature) */
    .stats-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        height: 100%;
    }
    .stats-title {
        font-family: 'Roboto Condensed', sans-serif;
        color: #aaa;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 10px;
    }
    .stats-value {
        font-family: 'Teko', sans-serif;
        font-size: 2rem;
        font-weight: 600;
        line-height: 1;
    }

    /* Rank Medals */
    .rank-circle {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Teko', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #000;
        position: absolute;
        top: -25px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.5);
        z-index: 10;
    }

    /* 1st Place (Gold) */
    .place-1 {
        height: 100%;
        width: 300px;
        background: linear-gradient(160deg, rgba(255, 215, 0, 0.2), rgba(0,0,0,0.6));
        border: 2px solid #FFD700;
        z-index: 2;
    }
    .place-1 .rank-circle { background: radial-gradient(#FFD700, #DAA520); border: 2px solid white; }
    .place-1 .score-text { color: #FFD700; text-shadow: 0 0 20px rgba(255, 215, 0, 0.4); }

    /* 2nd Place (Silver) */
    .place-2 {
        height: 75%;
        width: 260px;
        background: linear-gradient(160deg, rgba(192, 192, 192, 0.2), rgba(0,0,0,0.6));
        border: 2px solid #C0C0C0;
        z-index: 1;
    }
    .place-2 .rank-circle { background: radial-gradient(#E0E0E0, #A9A9A9); border: 2px solid white; }
    .place-2 .score-text { color: #E0E0E0; }

    /* 3rd Place (Bronze) */
    .place-3 {
        height: 60%;
        width: 260px;
        background: linear-gradient(160deg, rgba(205, 127, 50, 0.2), rgba(0,0,0,0.6));
        border: 2px solid #CD7F32;
        z-index: 1;
    }
    .place-3 .rank-circle { background: radial-gradient(#FFA07A, #8B4513); border: 2px solid white; }
    .place-3 .score-text { color: #FF8C00; }

    /* Text */
    .name-text {
        font-family: 'Teko', sans-serif;
        font-size: 2.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 25px;
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
        margin: -5px 0 0 0;
        line-height: 1;
    }
    .pts-label {
        font-family: 'Roboto Condensed', sans-serif;
        font-size: 0.85rem;
        text-transform: uppercase;
        opacity: 0.65;
        letter-spacing: 3px;
        margin-top: 5px;
    }

    /* TICKER STYLING */
    .ticker-wrap {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #aa0000;
        overflow: hidden;
        height: 40px;
        display: flex;
        align-items: center;
        border-top: 2px solid #fff;
        z-index: 9999;
    }
    .ticker-move {
        display: inline-block;
        white-space: nowrap;
        animation: ticker-move 30s linear infinite;
        font-family: 'Roboto Condensed', sans-serif;
        font-size: 1.2rem;
        color: white;
        font-weight: 700;
        text-transform: uppercase;
    }
    .ticker-item { display: inline-block; padding: 0 50px; }
    
    /* REFRESH TIMER STYLING */
    .refresh-timer {
        position: fixed;
        top: 15px;
        right: 15px;
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 20px;
        padding: 5px 15px;
        color: #ccc;
        font-family: 'Roboto Condensed', sans-serif;
        font-size: 0.9rem;
        backdrop-filter: blur(5px);
        z-index: 9999;
        display: flex;
        align-items: center;
        gap: 5px;
    }

    /* UPPER STAGE LAYOUT (Podium + Chase Pack Sidebar) */
    .upper-stage {
        display: flex;
        gap: 30px;
        margin-bottom: 30px;
        align-items: flex-start;
    }
    
    .podium-section {
        flex: 1;
        min-width: 0;
    }
    
    .chase-pack-sidebar {
        width: 400px;
        flex-shrink: 0;
    }
    
    /* CHASE PACK STYLING */
    .chase-pack-header {
        font-family: 'Teko', sans-serif;
        font-size: 2rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #aaa;
        margin-bottom: 20px;
        text-align: center;
    }
    
    .chase-pack-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 10px;
    }
    
    .chase-player-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 12px 15px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .chase-player-card:hover {
        transform: translateY(-2px);
        border-color: rgba(255, 255, 255, 0.3);
    }
    
    .chase-player-card.wooden-spoon {
        border: 2px solid #cc0000;
        background: rgba(204, 0, 0, 0.1);
    }
    
    .chase-player-left {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .chase-rank {
        font-family: 'Teko', sans-serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: #666;
        min-width: 25px;
    }
    
    .chase-player-card.wooden-spoon .chase-rank {
        color: #cc0000;
    }
    
    .chase-name {
        font-family: 'Teko', sans-serif;
        font-size: 1.4rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #fff;
    }
    
    .chase-player-card.wooden-spoon .chase-name {
        color: #cc0000;
    }
    
    .chase-score {
        font-family: 'Teko', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #fff;
    }
    
    .chase-player-card.wooden-spoon .chase-score {
        color: #cc0000;
    }

    @keyframes ticker-move {
        0% { transform: translate3d(100%, 0, 0); }
        100% { transform: translate3d(-100%, 0, 0); }
    }
    @keyframes pulse-red {
        0% { box-shadow: 0 0 0 0 rgba(204, 0, 0, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(204, 0, 0, 0); }
        100% { box-shadow: 0 0 0 0 rgba(204, 0, 0, 0); }
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 LOGIC
# ==========================================
def load_data():
    try:
        df_resp = pd.read_csv(RESPONSES_URL)
        df_key = pd.read_csv(KEY_URL)
        return df_resp, df_key
    except Exception:
        return pd.DataFrame(), pd.DataFrame()

def calculate_scores(responses, key):
    if responses.empty or key.empty:
        return pd.DataFrame(columns=['Name', 'Score'])

    answer_map = dict(zip(key.iloc[:, 0], key.iloc[:, 1]))
    scores = []

    for _, row in responses.iterrows():
        try:
            raw_val = row.iloc[2] # Grab 3rd column
            name = str(raw_val).strip()
            if "@" in name: name = name.split("@")[0] # Clean emails
            if name.lower() in ["nan", ""]: name = "Anonymous"
        except:
            name = "Unknown"

        points = 0
        for q, correct_ans in answer_map.items():
            if q in row:
                user_ans = str(row[q]).strip().lower()
                correct_ans_str = str(correct_ans).strip().lower()
                if correct_ans_str not in ["nan", "pending", ""]:
                     if user_ans == correct_ans_str:
                        points += 1
        scores.append({"Name": name, "Score": points})
    
    return pd.DataFrame(scores).sort_values("Score", ascending=False)

def get_party_stats(df, responses, key_df):
    # 1. Wooden Spoon (Last Place)
    last_place_name = "---"
    if len(df) >= 4:
        last_place_name = df.iloc[-1]['Name'].upper()
    
    # 2. Rivalry (Find 4th & 5th place)
    rivalry_text = "---"
    if len(df) >= 5:
        p4 = df.iloc[3]['Name'].upper()
        p5 = df.iloc[4]['Name'].upper()
        rivalry_text = f"{p4} vs {p5}"
    
    # 3. Party Pulse (Smart Upcoming or Winner Pick)
    pulse_text = "Seahawks: 50% / Pats: 50%"
    pulse_label = "📊 CROWD PREDICTION"
    
    # Check for Unanswered Questions
    unanswered = []
    if not key_df.empty:
        for _, row in key_df.iterrows():
            ans = str(row.iloc[1]).strip().lower()
            if ans in ["nan", "pending", ""]:
                unanswered.append(row.iloc[0])
                
    if unanswered:
        # Show a random upcoming question
        q_text = random.choice(unanswered)
        
        # Label: Clean Question Text (Right of colon)
        clean_q = q_text.split(":", 1)[-1].strip()
        pulse_label = f"🎲 {clean_q}"
        
        # Stats: Calculate % for top answer
        pulse_text = "Waiting for bets..."
        try:
            if q_text in responses.columns:
                counts = responses[q_text].value_counts(normalize=True).mul(100).round(0)
                if not counts.empty:
                    top_pick = counts.index[0]
                    top_pct = int(counts.iloc[0])
                    pulse_text = f"{top_pct}% voted for {top_pick}"
        except:
            pass
    else:
        # Fallback: Show Winner Stats
        pulse_label = "📊 CROWD PREDICTION"
        try:
            col_match = [c for c in responses.columns if "winner" in c.lower() or "team" in c.lower()]
            if col_match:
                target_col = col_match[0]
                counts = responses[target_col].value_counts(normalize=True).mul(100).round(0)
                if not counts.empty:
                    top_pick = counts.index[0]
                    top_pct = int(counts.iloc[0])
                    pulse_text = f"{top_pick} ({top_pct}%)"
        except:
            pass
        
    return last_place_name, rivalry_text, pulse_text, pulse_label

def calculate_points_remaining(key_df):
    """Calculate how many questions are still unanswered (null values in key)"""
    if key_df.empty:
        return 0
    try:
        # Count null/pending values in the answer column (second column)
        answer_col = key_df.iloc[:, 1]
        null_count = answer_col.isna().sum()
        # Also count 'pending' or empty strings as unanswered
        pending_count = answer_col.astype(str).str.lower().isin(['pending', '', 'nan']).sum()
        return max(null_count, pending_count)
    except:
        return 0

# ==========================================
# 📺 APP EXECUTION
# ==========================================

# 1. HEADER (Static part - will be updated with dynamic badges)
header_placeholder = st.empty()

placeholder = st.empty()

# 2. MAIN CONTENT LOOP
with placeholder.container():
    responses, key = load_data()
    
    # Calculate points remaining
    points_remaining = calculate_points_remaining(key)
    
    # Update header with dynamic points remaining
    header_placeholder.markdown(f"""
<div class="header-container">
<div class="super-bowl-title">Super Bowl LX</div>
<div class="super-bowl-title" style="font-size: 2.5rem; color: #ccc;">Betting Challenge</div>
<div class="badge-container">
<div class="live-badge">Live • Levi's Stadium</div>
<div class="points-remaining-badge">⚡ Points Left in Game: {points_remaining}</div>
</div>
</div>
""", unsafe_allow_html=True)
    
    if responses.empty:
        st.info("Waiting for data... Check your CSV links.")
        leader_name = "---"
        leader_score = 0
    else:
        df = calculate_scores(responses, key).reset_index(drop=True)
        
        # --- STATE MANAGEMENT & ALERTS ---
        n1 = df.iloc[0]['Name'] if len(df) > 0 else "---"
        s1 = int(df.iloc[0]['Score']) if len(df) > 0 else 0
        
        # Init State
        if 'last_leader' not in st.session_state: st.session_state.last_leader = n1
        if 'last_top_score' not in st.session_state: st.session_state.last_top_score = s1

        # Check for NEW LEADER
        if st.session_state.last_leader != n1:
            st.balloons()
            st.toast(f"🚨 NEW LEADER: {n1}!", icon="👑")
            st.session_state.last_leader = n1
            
        # Check for SCORE UPDATE
        elif s1 > st.session_state.last_top_score:
            st.toast(f"📈 POINTS UPDATED! Leader at {s1}", icon="🏈")
            st.session_state.last_top_score = s1
            
        leader_name = n1
        leader_score = s1

        # --- PODIUM RENDER ---
        def get_player(idx):
            if len(df) > idx: return df.iloc[idx]['Name'], int(df.iloc[idx]['Score'])
            return "---", 0

        p1n, p1s = get_player(0)
        p2n, p2s = get_player(1)
        p3n, p3s = get_player(2)
        
        # --- BUILD CHASE PACK HTML ---
        chase_pack_html = ''
        if len(df) > 3:
            chase_pack = df.iloc[3:].reset_index(drop=True)
            last_place_idx = len(chase_pack) - 1
            
            chase_pack_html = '<div class="chase-pack-sidebar"><div class="chase-pack-header">The Chase Pack</div><div class="chase-pack-grid">'
            
            for idx, row in chase_pack.iterrows():
                rank = idx + 4
                name = row['Name']
                score = int(row['Score'])
                wooden_spoon_class = ' wooden-spoon' if idx == last_place_idx else ''
                chase_pack_html += f'<div class="chase-player-card{wooden_spoon_class}"><div class="chase-player-left"><div class="chase-rank">{rank}</div><div class="chase-name">{name}</div></div><div class="chase-score">{score}</div></div>'
            
            chase_pack_html += '</div></div>'

        # --- UPPER STAGE: PODIUM + CHASE PACK SIDEBAR ---
        st.markdown(f"""
<div class="upper-stage">
<div class="podium-section">
<div class="podium-container">
<div class="pillar place-2">
<div class="rank-circle">2</div>
<div class="name-text">{p2n}</div>
<div class="score-text">{p2s}</div>
<div class="pts-label">Points</div>
</div>
<div class="pillar place-1">
<div class="rank-circle">1</div>
<div class="name-text">{p1n}</div>
<div class="score-text">{p1s}</div>
<div class="pts-label">Current Leader</div>
</div>
<div class="pillar place-3">
<div class="rank-circle">3</div>
<div class="name-text">{p3n}</div>
<div class="score-text">{p3s}</div>
<div class="pts-label">Points</div>
</div>
</div>
</div>
{chase_pack_html}
</div>
""", unsafe_allow_html=True)

        # --- PARTY STATS ROW ---
        spoon, rivalry, pulse, label = get_party_stats(df, responses, key)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-title">🔥 Rivalry Watch</div>
                <div class="stats-value" style="font-size: 1.5rem; color: #ffcc00;">{rivalry}</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-title">{label}</div>
                <div class="stats-value" style="font-size: 1.5rem; color: #00d2ff;">{pulse}</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-title">🥄 The Wooden Spoon</div>
                <div class="stats-value" style="font-size: 1.5rem; color: #ff4444;">{spoon}</div>
            </div>
            """, unsafe_allow_html=True)

# 3. TICKER (ALWAYS VISIBLE)
# Safety logic: Ensure all ticker variables have default values
if 'leader_name' not in locals():
    leader_name = "---"
if 'leader_score' not in locals():
    leader_score = 0
if 'spoon' not in locals():
    spoon = "---"
if 'rivalry' not in locals():
    rivalry = "---"

# Calculate player count
try:
    player_count = len(df) if 'df' in locals() and not df.empty else 0
except:
    player_count = 0

st.markdown(f"""
    <div class="ticker-wrap">
        <div class="ticker-move">
            <span class="ticker-item">🏈 SUPER BOWL LX LIVE LEADERBOARD</span>
            <span class="ticker-item">🏆 LEADER: {leader_name} ({leader_score} PTS)</span>
            <span class="ticker-item">👥 {player_count} PLAYERS ACTIVE</span>
            <span class="ticker-item">🥄 NEEDS HELP: {spoon}</span>
            <span class="ticker-item">🔥 HOT BATTLE: {rivalry}</span>
            <span class="ticker-item">🍻 HYDRATE & CELEBRATE</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# 4. REFRESH TIMER LOOP (Replaces simple sleep)
timer_placeholder = st.empty()
for i in range(REFRESH_RATE, 0, -1):
    timer_placeholder.markdown(f"""
        <div class="refresh-timer">
            <span>↻</span> Updating in {i}s
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1)

st.rerun()
