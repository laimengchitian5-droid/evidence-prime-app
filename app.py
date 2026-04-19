import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# --- 1. CORE CONFIG & AUTHENTICATION ---
st.set_page_config(page_title="Evidence Prime Pro", layout="wide", initial_sidebar_state="expanded")

# 認証機能 (absolute-proof)
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if st.session_state.authenticated:
        return True
    
    st.title("🔒 Evidence Prime Pro Access")
    pwd = st.text_input("合言葉を入力してください", type="password")
    if st.button("Unlock"):
        if pwd == st.secrets["password"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("認証失敗")
    return False

if not check_password():
    st.stop()

# --- 2. DYNAMIC UI & GLASSMORPHISM CSS ---
def apply_ui_system():
    # サイドバーでのデザイン制御
    st.sidebar.title("🎨 Design & Settings")
    
    # クイックテーマ選択
    theme_mode = st.sidebar.radio("Quick Theme", ["Custom", "Midnight", "Deep Sea", "Emerald", "Crimson"], horizontal=True)
    presets = {
        "Midnight": "#6366f1", "Deep Sea": "#0ea5e9", 
        "Emerald": "#10b981", "Crimson": "#f43f5e"
    }
    
    if theme_mode == "Custom":
        main_color = st.sidebar.color_picker("Brand Color", "#6366f1")
    else:
        main_color = presets[theme_mode]

    # 言語切り替え
    lang = st.sidebar.selectbox("Language", ["JP", "EN", "KR", "CN"])

    # グラスモーフィズムCSS完全版
    st.markdown(f"""
        <style>
        .stApp {{
            background: radial-gradient(circle at top right, {main_color}22, #000000);
            background-attachment: fixed;
            color: #e2e8f0;
        }}
        /* メッセージカード */
        div[data-testid="stChatMessage"] {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid {main_color}33;
            backdrop-filter: blur(12px);
            border-radius: 18px;
            margin: 10px 0;
            padding: 15px;
        }}
        /* タブのスタイル */
        .stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
        .stTabs [data-baseweb="tab"] {{
            background-color: rgba(255,255,255,0.05);
            border-radius: 10px 10px 0 0;
            padding: 10px 20px;
            color: white;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: {main_color}44 !important;
            border-bottom: 2px solid {main_color} !important;
        }}
        </style>
    """, unsafe_allow_html=True)
    return main_color, lang

# --- 3. MEMORY & DATA SYSTEM (A-C Model) ---
MEMORY_FILE = "user_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"personality": {}, "big_five": {}, "history_summary": "", "last_update": ""}

def save_memory(data):
    data["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- 4. BIG FIVE DIAGNOSTIC (Tap System) ---
def big_five_section():
    st.markdown("### 🧬 Big Five 精密性格診断")
    st.caption("各項目をタップして、あなたの現在の状態を教えてください。")
    
    col1, col2 = st.columns(2)
    with col1:
        e = st.select_slider("👥 外向性 (静か ↔ 社交的)", options=, value=3)
        a = st.select_slider("🤝 協調性 (合理的 ↔ 共感的)", options=, value=3)
        c = st.select_slider("📈 勤勉性 (即興的 ↔ 計画的)", options=, value=3)
    with col2:
        n = st.select_slider("🧠 神経症傾向 (冷静 ↔ 繊細)", options=, value=3)
        o = st.select_slider("🎨 開放性 (保守的 ↔ 好奇心)", options=, value=3)
    
    if st.button("性格プロファイルを永久保存", use_container_width=True):
        st.session_state.memory["big_five"] = {"E": e, "A": a, "C": c, "N": n, "O": o}
        save_memory(st.session_state.memory)
        st.success("長期記憶バンクへ同期完了。AIの思考回路がアップデートされました。")

# --- 5. AI ENGINE & PROMPT (Groq Integration Ready) ---
def generate_system_prompt():
    mem = st.session_state.memory
    bf = mem.get("big_five", {"E":3, "A":3, "C":3, "N":3, "O":3})
    
    # 性格に応じた適応ロジック（最強プロンプト）
    c_trait = "細かいタスク分解とリマインド" if bf["C"] <= 2 else "高度な構造化と長期目標"
    n_trait = "心理的安全性を重視した肯定表現" if bf["N"] >= 4 else "客観的かつストレートな事実提示"
    
    prompt = f"""
あなたは『Evidence Prime Pro』、17歳の天才開発者の相棒です。
【A-Cモデル運用指示】
- A (Authority): Google Scholar級の信頼性。検証リンクを必ず提示。
- B (Blueprint): JSON形式で行動計画を生成し、Mermaidで図解せよ。
- C (Context): 以下のユーザー特性を全回答に反映せよ。
  [性格スコア] E:{bf['E']}, A:{bf['A']}, C:{bf['C']}, N:{bf['N']}, O:{bf['O']}
  [適応戦略] {c_trait} / {n_trait}
    """
    return prompt

# --- 6. MAIN INTERFACE ---
def main():
    main_color, lang = apply_ui_system()
    
    if "memory" not in st.session_state:
        st.session_state.memory = load_memory()
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # タブ構成（機能全網羅）
    tab_chat, tab_blueprint, tab_persona, tab_bank = st.tabs(["💬 Chat Agent", "🗓️ Blueprint", "🧬 Personality", "📊 Memory Bank"])

    with tab_persona:
        big_five_section()

    with tab_chat:
        st.title("Evidence Prime Pro")
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        if prompt := st.chat_input("解決したい課題を入力..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            
            # ここにGroq API呼び出しを挿入（system_prompt=generate_system_prompt()）
            # Mermaid図解やエビデンスリンクの処理をここに記述
            with st.chat_message("assistant"):
                st.write("（ここにLlama 3.3 70Bの、性格に最適化された回答が表示されます）")

    with tab_blueprint:
        st.subheader("週間アクションプラン")
        # 既存のテーブル・ダウンロード機能をここに集約
        st.info("チャットで生成された計画がここに自動反映されます。")

    with tab_bank:
        st.subheader("長期記憶データ (JSON)")
        st.json(st.session_state.memory)

if __name__ == "__main__":
    main()
