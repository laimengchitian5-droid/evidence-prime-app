import streamlit as st
import pandas as pd
import json
import os
import time
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from groq import Groq

# --- 1. SETTINGS & AUTHENTICATION ---
st.set_page_config(
    page_title="Evidence Prime Pro | Global",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if st.session_state.authenticated:
        return True
    
    st.markdown("""
        <style>
        .login-box {
            padding: 2rem;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            border: 1px solid #6366f1;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🛡️ Evidence Prime Pro: Security Gate")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.info("このアプリは17歳の開発者による次世代AIプロトタイプです。")
        pwd = st.text_input("合言葉を入力", type="password")
        if st.button("Access Granted 🚀", use_container_width=True):
            if pwd == st.secrets.get("password", "admin"):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Access Denied.")
    st.stop()

check_password()

# --- 2. DATA & API INITIALIZATION ---
client = Groq(api_key=st.secrets.get("GROQ_API_KEY", "your_key"))
MEMORY_FILE = "user_memory_v2.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f: return json.load(f)
        except: pass
    return {
        "big_five": {"E": 3, "A": 3, "C": 3, "N": 3, "O": 3},
        "achievements": [],
        "tasks": [],
        "ai_loyalty": 0
    }

if "memory" not in st.session_state:
    st.session_state.memory = load_memory()
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. DYNAMIC GLASSMORPHISM ENGINE ---
def apply_global_theme():
    st.sidebar.title("🧬 System OS")
    
    # テーマプリセット（世界基準のデザイン）
    theme_choice = st.sidebar.select_slider(
        "Theme Palette",
        options=["Cyber", "Deep Sea", "Forest", "Sakura", "Lava"]
    )
    palette = {
        "Cyber": "#6366f1", "Deep Sea": "#0ea5e9", 
        "Forest": "#10b981", "Sakura": "#f472b6", "Lava": "#f43f5e"
    }
    main_color = palette[theme_choice]
    
    st.markdown(f"""
        <style>
        :root {{ --main-color: {main_color}; }}
        .stApp {{
            background: linear-gradient(180deg, #0f172a 0%, #000000 100%);
            color: #f8fafc;
        }}
        /* グラスモーフィズム */
        div[data-testid="stChatMessage"] {{
            background: rgba(255, 255, 255, 0.03);
            border-left: 5px solid {main_color};
            border-radius: 10px;
            margin: 15px 0;
            backdrop-filter: blur(10px);
        }}
        .stTabs [data-baseweb="tab-list"] {{
            background: rgba(255,255,255,0.02);
            border-radius: 15px;
            padding: 5px;
        }}
        .stButton>button {{
            background: linear-gradient(90deg, {main_color}aa, {main_color}44);
            border: none; color: white; border-radius: 10px;
            font-weight: bold; transition: 0.3s;
        }}
        .stButton>button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px {main_color}66;
        }}
        /* カスタムスクロールバー */
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-thumb {{ background: {main_color}44; border-radius: 10px; }}
        </style>
    """, unsafe_allow_html=True)
    return main_color

main_color = apply_global_theme()

# --- 4. CORE FUNCTIONALITY: ANALYSIS & VISUALIZATION ---
def render_stats():
    st.subheader("📊 Performance Insight")
    df = pd.DataFrame(st.session_state.memory.get("achievements", [
        {"date": "2024-05-20", "score": 60},
        {"date": "2024-05-21", "score": 75},
        {"date": "2024-05-22", "score": 90}
    ]))
    
    fig = px.line(df, x="date", y="score", title="Growth Velocity")
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color="white", margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

def big_five_dashboard():
    st.subheader("🧬 Personality Architecture")
    bf = st.session_state.memory["big_five"]
    
    categories = ['Extraversion', 'Agreeableness', 'Conscientiousness', 'Neuroticism', 'Openness']
    values = [bf['E'], bf['A'], bf['C'], bf['N'], bf['O']]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values, theta=categories, fill='toself',
        line=dict(color=main_color)
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5], gridcolor="gray")),
        showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 診断スライダー
    col1, col2 = st.columns(2)
    with col1:
        e = st.select_slider("Extraversion", options=[1,2,3,4,5], value=bf['E'])
        a = st.select_slider("Agreeableness", options=[1,2,3,4,5], value=bf['A'])
        c = st.select_slider("Conscientiousness", options=[1,2,3,4,5], value=bf['C'])
    with col2:
        n = st.select_slider("Neuroticism", options=[1,2,3,4,5], value=bf['N'])
        o = st.select_slider("Openness", options=[1,2,3,4,5], value=bf['O'])
    
    if st.button("Update Profile 🧠"):
        st.session_state.memory["big_five"] = {"E": e, "A": a, "C": c, "N": n, "O": o}
        with open(MEMORY_FILE, "w") as f: json.dump(st.session_state.memory, f)
        st.success("Profile Synced to Global Network.")

# --- 5. AI LOGIC: THE GLOBAL AGENT ---
def run_ai_agent(user_input):
    bf = st.session_state.memory["big_five"]
    
    # ユーザー特性に合わせた動的システムプロンプト
    # Conscientiousness(C)が高い=プロ仕様、低い=コーチング重視
    tone = "Highly logical and structural" if bf['C'] >= 4 else "Encouraging and breaking tasks into tiny pieces"
    
    system_prompt = f"""
    You are 'Evidence Prime Pro', a world-class AI agent.
    User Traits: E:{bf['E']}, A:{bf['A']}, C:{bf['C']}, N:{bf['N']}, O:{bf['O']}
    Current Strategy: {tone}
    
    MISSION:
    1. A (Authority): Cite latest global evidence.
    2. B (Blueprint): Provide actionable plans in JSON or Mermaid charts.
    3. C (Context): Reference past interaction and personality traits.
    
    Always output in the user's language but maintain a global high-tech perspective.
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
            stream=True
        )
        return completion
    except Exception as e:
        st.error(f"Groq API Connection Error: {e}")
        return None

# --- 6. MAIN LAYOUT ---
def main():
    st.sidebar.markdown("---")
    st.sidebar.write(f"📅 Last Sync: {datetime.now().strftime('%H:%M:%S')}")
    st.sidebar.progress(st.session_state.memory.get("ai_loyalty", 45), text="AI Alignment Score")

    tab_home, tab_blueprint, tab_science, tab_settings = st.tabs([
        "💬 Global Chat", "📋 Blueprint Hub", "📊 Science Insight", "⚙️ System Core"
    ])

    with tab_home:
        st.title("Evidence Prime Pro")
        st.caption("Empowered by Llama 3.3 70B & Your Personality Context.")
        
        chat_container = st.container()
        with chat_container:
            for m in st.session_state.messages:
                with st.chat_message(m["role"]): st.write(m["content"])

        if prompt := st.chat_input("Enter your mission..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.write(prompt)

            with st.chat_message("assistant"):
                res_box = st.empty()
                full_res = ""
                completion = run_ai_agent(prompt)
                if completion:
                    for chunk in completion:
                        content = chunk.choices[0].delta.content
                        if content:
                            full_res += content
                            res_box.markdown(full_res + "▌")
                    res_box.markdown(full_res)
                    st.session_state.messages.append({"role": "assistant", "content": full_res})

    with tab_blueprint:
        st.header("📋 Automated Blueprint")
        st.info("AI generated action plans and Mermaid diagrams will appear here.")
        # ここでメッセージ履歴からMermaid記法を抽出して表示するロジックを追加可能
        st.button("Export as PDF")
        st.button("Sync to Google Calendar")

    with tab_science:
        st.header("📊 Personal Science Dashboard")
        col_l, col_r = st.columns(2)
        with col_l: render_stats()
        with col_r: big_five_dashboard()

    with tab_settings:
        st.header("⚙️ Core Configuration")
        st.json(st.session_state.memory)
        if st.button("Factory Reset Memory"):
            st.session_state.memory = load_memory()
            st.rerun()

if __name__ == "__main__":
    main()
