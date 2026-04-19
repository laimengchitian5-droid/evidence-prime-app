import streamlit as st
import pandas as pd
import json
import os
import time
from datetime import datetime
from groq import Groq

# Plotlyの動的インポート（環境エラー対策）
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# --- 1. CORE CONFIGURATION ---
st.set_page_config(
    page_title="Evidence Prime Pro | Global",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. SECURITY SYSTEM (Absolute-Proof) ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if st.session_state.authenticated:
        return True
    
    st.markdown("""
        <style>
        .login-card {
            background: rgba(255, 255, 255, 0.05);
            padding: 3rem;
            border-radius: 30px;
            border: 1px solid #6366f1;
            text-align: center;
            backdrop-filter: blur(20px);
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🔒 Global Gate")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        pwd = st.text_input("Enter Passkey", type="password", placeholder="Secret code...")
        if st.button("Unlock Core", use_container_width=True):
            if pwd == st.secrets.get("password", "admin"):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid Passkey.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

check_password()

# --- 3. PERSISTENT MEMORY SYSTEM (A-C Model) ---
MEMORY_FILE = "user_memory_global.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f: return json.load(f)
        except: pass
    return {
        "big_five": {"E": 3, "A": 3, "C": 3, "N": 3, "O": 3},
        "achievements": [{"date": "2024-05-20", "score": 50}],
        "history": [],
        "language": "JP",
        "theme_color": "#6366f1"
    }

def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(st.session_state.memory, f, indent=4)

if "memory" not in st.session_state:
    st.session_state.memory = load_memory()
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. ULTIMATE UI ENGINE (Glassmorphism 2.0) ---
def apply_style():
    mem = st.session_state.memory
    # サイドバーでのテーマ制御
    st.sidebar.title("🛠️ System OS")
    theme_preset = st.sidebar.selectbox("Theme Preset", ["Cyber", "Ocean", "Forest", "Lava", "Ghost"])
    presets = {
        "Cyber": "#6366f1", "Ocean": "#0ea5e9", 
        "Forest": "#10b981", "Lava": "#f43f5e", "Ghost": "#94a3b8"
    }
    main_color = presets[theme_preset]
    st.session_state.memory["theme_color"] = main_color
    
    st.markdown(f"""
        <style>
        .stApp {{
            background: radial-gradient(circle at top right, {main_color}15, #020617);
            color: #f1f5f9;
        }}
        /* チャットバブルの進化 */
        div[data-testid="stChatMessage"] {{
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid {main_color}22;
            border-left: 4px solid {main_color};
            backdrop-filter: blur(15px);
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 15px;
        }}
        /* ボタンアニメーション */
        .stButton>button {{
            background: linear-gradient(135deg, {main_color}dd, {main_color}44);
            border: none; color: white; border-radius: 12px;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }}
        .stButton>button:hover {{
            transform: scale(1.05) translateY(-3px);
            box-shadow: 0 10px 20px {main_color}44;
        }}
        /* タブのデザイン */
        .stTabs [data-baseweb="tab"] {{
            font-weight: 600; color: #94a3b8;
        }}
        .stTabs [aria-selected="true"] {{
            color: {main_color} !important;
            border-bottom: 2px solid {main_color} !important;
        }}
        </style>
    """, unsafe_allow_html=True)
    return main_color

main_color = apply_style()

# --- 5. ANALYTICS ENGINE (Plotly) ---
def render_analytics():
    if not PLOTLY_AVAILABLE:
        st.warning("Analytics Engine is loading... Please check requirements.txt")
        return

    st.subheader("📊 Growth & Personality Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Big Five Radar Chart
        bf = st.session_state.memory["big_five"]
        categories = ['Extraversion', 'Agreeableness', 'Conscientiousness', 'Neuroticism', 'Openness']
        values = [bf['E'], bf['A'], bf['C'], bf['N'], bf['O']]
        
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=values, theta=categories, fill='toself',
            line=dict(color=main_color), marker=dict(color=main_color)
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[1, 5], gridcolor="#334155"), bgcolor="rgba(0,0,0,0)"),
            paper_bgcolor='rgba(0,0,0,0)', font_color="#f1f5f9", margin=dict(l=40, r=40, t=20, b=20)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col2:
        # Achievement Line Chart
        df = pd.DataFrame(st.session_state.memory["achievements"])
        fig_line = px.line(df, x="date", y="score", title="Cognitive Growth")
        fig_line.update_traces(line_color=main_color, mode='lines+markers')
        fig_line.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color="#f1f5f9", xaxis=dict(gridcolor="#1e293b"), yaxis=dict(gridcolor="#1e293b")
        )
        st.plotly_chart(fig_line, use_container_width=True)

# --- 6. AI AGENT CORE (Groq Llama 3.3 70B) ---
def chat_with_ai(user_input):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    bf = st.session_state.memory["big_five"]
    
    # 25通りの性格適応ロジック
    strategies = {
        "logic": "Use structured data, academic citations, and logical steps.",
        "support": "Use empathetic tone, psychological safety, and small wins.",
        "creative": "Use metaphors, unconventional ideas, and experimental approaches."
    }
    
    # C(勤勉性)とN(神経症傾向)に基づく戦略選択
    current_strat = strategies["logic"] if bf["C"] >= 4 else strategies["support"]
    if bf["O"] >= 4: current_strat += " " + strategies["creative"]

    system_prompt = f"""
    You are 'Evidence Prime Pro', a world-class AI agent for a 17-year-old visionary developer.
    [USER PROFILE]
    Traits: E:{bf['E']}, A:{bf['A']}, C:{bf['C']}, N:{bf['N']}, O:{bf['O']}
    Strategy: {current_strat}
    
    [CORE DIRECTIVES]
    1. A (Authority): Cite verifiable sources and scientific links.
    2. B (Blueprint): Provide actionable plans in markdown tables or Mermaid charts.
    3. C (Context): Reference user's personality in every advice to maximize execution.
    
    Tone: Professional yet visionary. Encourage the developer's journey.
    """
    
    messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            stream=True
        )
        return completion
    except Exception as e:
        st.error(f"AI Core Error: {e}")
        return None

# --- 7. MAIN INTERFACE ---
def main():
    tab_chat, tab_insight, tab_blueprint, tab_core = st.tabs([
        "💬 AI Agent", "🧬 Insight Analysis", "📋 Blueprint Hub", "⚙️ System Core"
    ])

    # --- Chat Tab ---
    with tab_chat:
        st.title("Evidence Prime Pro")
        st.caption("Next-Gen AI Partner | A-C Model Integrated")
        
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        if prompt := st.chat_input("Solve scientifically..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                res_area = st.empty()
                full_res = ""
                chunks = chat_with_ai(prompt)
                if chunks:
                    for chunk in chunks:
                        content = chunk.choices.delta.content
                        if content:
                            full_res += content
                            res_area.markdown(full_res + "▌")
                    res_area.markdown(full_res)
                    st.session_state.messages.append({"role": "assistant", "content": full_res})

    # --- Insight Tab ---
    with tab_insight:
        render_analytics()
        st.divider()
        st.subheader("🧬 Personality Tuning")
        col1, col2 = st.columns(2)
        bf = st.session_state.memory["big_five"]
        with col1:
            e = st.select_slider("Extraversion (静 ↔ 活)", options=[1,2,3,4,5], value=bf["E"])
            a = st.select_slider("Agreeableness (独 ↔ 共)", options=[1,2,3,4,5], value=bf["A"])
            c = st.select_slider("Conscientiousness (即 ↔ 計)", options=[1,2,3,4,5], value=bf["C"])
        with col2:
            n = st.select_slider("Neuroticism (冷 ↔ 繊)", options=[1,2,3,4,5], value=bf["N"])
            o = st.select_slider("Openness (伝 ↔ 新)", options=[1,2,3,4,5], value=bf["O"])
        
        if st.button("Sync Personality to AI Core"):
            st.session_state.memory["big_five"] = {"E": e, "A": a, "C": c, "N": n, "O": o}
            save_memory()
            st.toast("AI context updated successfully!", icon="🧠")

    # --- Blueprint Tab ---
    with tab_blueprint:
        st.header("📋 Actionable Blueprint")
        st.info("Here, the AI's generated plans are structured for execution.")
        # 仮のタスク表示
        tasks = [
            {"Task": "Market Research", "Priority": "High", "Status": "Ongoing"},
            {"Task": "API Security Audit", "Priority": "Critical", "Status": "Pending"}
        ]
        st.table(tasks)
        st.button("Export Blueprint as JSON")

    # --- System Core Tab ---
    with tab_core:
        st.header("⚙️ Core Memory Status")
        st.json(st.session_state.memory)
        if st.button("Purge System Memory"):
            st.session_state.memory = load_memory()
            st.rerun()

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Evidence Prime Pro v2.1 | Dev: 17yo Visionary")
    st.sidebar.caption(f"Status: Operational | Groq-Llama-3.3")

if __name__ == "__main__":
    main()
