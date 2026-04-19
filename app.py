import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from groq import Groq

# Plotlyの動的インポート
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except:
    PLOTLY_AVAILABLE = False

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="Evidence Prime Pro | Global", page_icon="🧬", layout="wide")

# --- 2. SECURITY SYSTEM ---
def check_password():
    if st.session_state.get("authenticated"):
        return True
    
    st.title("🔒 Global Gate")
    # Secretsから取得、なければデフォルト 'admin'
    target = st.secrets.get("password", "admin")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.write("17yo Developer's Visionary AI Platform")
        pwd = st.text_input("Enter Passkey", type="password")
        if st.button("Unlock Core", use_container_width=True):
            if pwd == target:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Invalid Passkey. Check your Streamlit Secrets.")
    st.stop()

check_password()

# --- 3. INITIALIZATION ---
client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))
MEMORY_FILE = "user_memory.json"

if "memory" not in st.session_state:
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f: st.session_state.memory = json.load(f)
    else:
        st.session_state.memory = {
            "big_five": {"E":3, "A":3, "C":3, "N":3, "O":3},
            "achievements": [{"date": datetime.now().strftime("%Y-%m-%d"), "score": 50}]
        }

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. DESIGN ENGINE ---
def apply_theme():
    st.sidebar.title("🛠️ System OS")
    theme = st.sidebar.selectbox("Theme", ["Cyber", "Ocean", "Lava"])
    colors = {"Cyber": "#6366f1", "Ocean": "#0ea5e9", "Lava": "#f43f5e"}
    main_color = colors[theme]
    
    st.markdown(f"""
        <style>
        .stApp {{ background: radial-gradient(circle at top right, {main_color}22, #020617); color: #f1f5f9; }}
        div[data-testid="stChatMessage"] {{
            background: rgba(255, 255, 255, 0.02);
            border-left: 4px solid {main_color};
            backdrop-filter: blur(10px);
            border-radius: 15px;
        }}
        .stButton>button {{ background: {main_color}aa; border: none; color: white; border-radius: 10px; }}
        </style>
    """, unsafe_allow_html=True)
    return main_color

main_color = apply_theme()

# --- 5. MAIN INTERFACE ---
tab_chat, tab_insight, tab_blueprint = st.tabs(["💬 Chat", "🧬 Insight", "📋 Blueprint"])

with tab_chat:
    st.title("Evidence Prime Pro")
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Input your goal..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        # 最強プロンプト構築
        bf = st.session_state.memory["big_five"]
        sys_prompt = f"Evidence Prime Proとして回答。User traits: E:{bf['E']}, A:{bf['A']}, C:{bf['C']}, N:{bf['N']}, O:{bf['O']}. 科学的根拠(A), 行動計画(B), 文脈適応(C)を徹底せよ。"

        with st.chat_message("assistant"):
            res_box = st.empty()
            full_res = ""
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": sys_prompt}] + st.session_state.messages,
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    res_box.markdown(full_res + "▌")
            res_box.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})

with tab_insight:
    if PLOTLY_AVAILABLE:
        st.subheader("🧬 Personality Analysis")
        bf = st.session_state.memory["big_five"]
        fig = go.Figure(data=go.Scatterpolar(
            r=[bf['E'], bf['A'], bf['C'], bf['N'], bf['O']],
            theta=['Ext', 'Agr', 'Con', 'Neu', 'Opn'], fill='toself', line_color=main_color
        ))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", polar=dict(bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig, use_container_width=True)

    # 診断スライダー
    opts = [1,2,3,4,5]
    col1, col2 = st.columns(2)
    with col1:
        e = st.select_slider("Extraversion", options=opts, value=bf['E'])
        c = st.select_slider("Conscientiousness", options=opts, value=bf['C'])
    with col2:
        n = st.select_slider("Neuroticism", options=opts, value=bf['N'])
        o = st.select_slider("Openness", options=opts, value=bf['O'])
    
    if st.button("Sync Intelligence"):
        st.session_state.memory["big_five"] = {"E":e, "A":bf['A'], "C":c, "N":n, "O":o}
        with open(MEMORY_FILE, "w") as f: json.dump(st.session_state.memory, f)
        st.success("Synced.")

with tab_blueprint:
    st.header("📋 Action Blueprint")
    st.info("AI-generated plans will be structured here.")
    # 簡易テーブル表示
    st.table(pd.DataFrame([{"Step": "Analyze", "Evidence": "Meta-analysis 2023", "Status": "Ready"}]))

st.sidebar.caption(f"v2.5 | Global Edition")
