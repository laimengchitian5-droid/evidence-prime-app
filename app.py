import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from groq import Groq

# --- 1. CORE CONFIG & AUTHENTICATION ---
st.set_page_config(page_title="Evidence Prime Pro", layout="wide", initial_sidebar_state="expanded")

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if st.session_state.authenticated:
        return True
    
    st.title("🔒 Evidence Prime Pro Access")
    # st.secrets["password"] が設定されている前提
    pwd = st.text_input("合言葉を入力してください", type="password")
    if st.button("Unlock"):
        if pwd == st.secrets.get("password", "admin"): # デフォルト値をadminに設定
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("認証失敗")
    return False

if not check_password():
    st.stop()

# Groqクライアントの初期化
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. DYNAMIC UI & GLASSMORPHISM CSS ---
def apply_ui_system():
    st.sidebar.title("🎨 Design & Settings")
    theme_mode = st.sidebar.radio("Quick Theme", ["Custom", "Midnight", "Deep Sea", "Emerald", "Crimson"], horizontal=True)
    presets = {
        "Midnight": "#6366f1", "Deep Sea": "#0ea5e9", 
        "Emerald": "#10b981", "Crimson": "#f43f5e"
    }
    main_color = st.sidebar.color_picker("Brand Color", presets.get(theme_mode, "#6366f1")) if theme_mode == "Custom" else presets[theme_mode]

    st.markdown(f"""
        <style>
        .stApp {{ background: radial-gradient(circle at top right, {main_color}22, #000000); background-attachment: fixed; color: #e2e8f0; }}
        div[data-testid="stChatMessage"] {{ background: rgba(255, 255, 255, 0.03); border: 1px solid {main_color}33; backdrop-filter: blur(12px); border-radius: 18px; margin: 10px 0; padding: 15px; }}
        .stButton>button {{ border-radius: 20px; border: 1px solid {main_color}; background-color: transparent; color: {main_color}; }}
        .stButton>button:hover {{ background-color: {main_color}; color: white; }}
        </style>
    """, unsafe_allow_html=True)
    return main_color

# --- 3. MEMORY SYSTEM ---
MEMORY_FILE = "user_memory.json"
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f: return json.load(f)
        except: pass
    return {"big_five": {"E":3, "A":3, "C":3, "N":3, "O":3}, "history": []}

def save_memory(data):
    with open(MEMORY_FILE, "w") as f: json.dump(data, f, indent=4)

# --- 4. MAIN APP ---
def main():
    main_color = apply_ui_system()
    if "memory" not in st.session_state: st.session_state.memory = load_memory()
    if "messages" not in st.session_state: st.session_state.messages = []

    tab_chat, tab_persona, tab_bank = st.tabs(["💬 Chat", "🧬 Personality", "📊 Memory"])

    with tab_persona:
        st.subheader("🧬 Big Five 診断（タップ選択）")
        # options= を [1, 2, 3, 4, 5] に修正
        opts = [1, 2, 3, 4, 5]
        col1, col2 = st.columns(2)
        with col1:
            e = st.select_slider("👥 外向性", options=opts, value=st.session_state.memory["big_five"].get("E", 3))
            a = st.select_slider("🤝 協調性", options=opts, value=st.session_state.memory["big_five"].get("A", 3))
            c = st.select_slider("📈 勤勉性", options=opts, value=st.session_state.memory["big_five"].get("C", 3))
        with col2:
            n = st.select_slider("🧠 神経症傾向", options=opts, value=st.session_state.memory["big_five"].get("N", 3))
            o = st.select_slider("🎨 開放性", options=opts, value=st.session_state.memory["big_five"].get("O", 3))
        
        if st.button("設定を保存してAIに同期"):
            st.session_state.memory["big_five"] = {"E": e, "A": a, "C": c, "N": n, "O": o}
            save_memory(st.session_state.memory)
            st.success("同期完了！")

    with tab_chat:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.write(m["content"])

        if prompt := st.chat_input("科学的根拠に基づく解決策を提案します"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.write(prompt)

            # 最強プロンプト生成
            bf = st.session_state.memory["big_five"]
            system_msg = f"あなたはEvidence Prime Proです。ユーザー特性(E:{bf['E']}, A:{bf['A']}, C:{bf['C']}, N:{bf['N']}, O:{bf['O']})に基づき、科学的根拠(Authority)と図解を含む行動計画(Blueprint)を提示せよ。17歳の開発者の情熱を体現し、親しみやすくもプロフェッショナルに振る舞え。"

            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                full_res = ""
                # Groq API呼び出し
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": system_msg}] + st.session_state.messages,
                    stream=True,
                )
                for chunk in completion:
                    content = chunk.choices[0].delta.content
                    if content:
                        full_res += content
                        response_placeholder.markdown(full_res + "▌")
                response_placeholder.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})

    with tab_bank:
        st.json(st.session_state.memory)

if __name__ == "__main__":
    main()
