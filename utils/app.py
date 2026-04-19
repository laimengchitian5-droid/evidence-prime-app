import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from groq import Groq

# Plotlyのインポート（環境エラー対策）
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# --- 1. 基本設定 ---
st.set_page_config(
    page_title="Evidence Prime Pro",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. セキュリティ（合言葉認証） ---
def check_password():
    if st.session_state.get("authenticated"):
        return True
    
    st.title("🔒 システムアクセス認証")
    # Secretsから取得、なければデフォルト 'admin'
    target_pwd = st.secrets.get("password", "admin")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pwd = st.text_input("合言葉を入力してください", type="password")
        if st.button("ログイン 🚀", use_container_width=True):
            if pwd == target_pwd:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("合言葉が正しくありません。")
    st.stop()

check_password()

# --- 3. 記憶システム ---
MEMORY_FILE = "user_memory_v3.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return {
        "big_five": {"E": 3, "A": 3, "C": 3, "N": 3, "O": 3},
        "achievements": [{"date": datetime.now().strftime("%Y-%m-%d"), "score": 50}]
    }

def save_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.memory, f, indent=4, ensure_ascii=False)

if "memory" not in st.session_state:
    st.session_state.memory = load_memory()
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. デザインエンジン（モバイル最適化） ---
def apply_ui_theme():
    # サイドバーでのテーマ制御
    st.sidebar.title("🛠️ 設定")
    theme_choice = st.sidebar.select_slider(
        "テーマ",
        options=["サイバー", "オーシャン", "ラヴァ"]
    )
    palette = {"サイバー": "#6366f1", "オーシャン": "#0ea5e9", "ラヴァ": "#f43f5e"}
    main_color = palette[theme_choice]
    
    st.markdown(f"""
        <style>
        .stApp {{
            background: radial-gradient(circle at top right, {main_color}15, #020617);
            color: #f1f5f9;
        }}
        div[data-testid="stChatMessage"] {{
            background: rgba(255, 255, 255, 0.02);
            border-left: 4px solid {main_color};
            border-radius: 12px;
            backdrop-filter: blur(10px);
            padding: 15px;
            margin-bottom: 10px;
        }}
        .stButton>button {{
            background: {main_color}aa;
            color: white; border-radius: 10px; border: none;
            width: 100%;
        }}
        </style>
    """, unsafe_allow_html=True)
    return main_color

main_color = apply_ui_theme()

# --- 5. AIコア（AttributeError対策済み） ---
def run_ai_agent():
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        st.error("APIキーが設定されていません。")
        return None
    
    client = Groq(api_key=api_key)
    bf = st.session_state.memory["big_five"]
    
    system_prompt = f"""
    あなたは『Evidence Prime Pro』です。日本語で回答してください。
    ユーザー性格特性: 外向性:{bf['E']}, 協調性:{bf['A']}, 勤勉性:{bf['C']}, 神経症傾向:{bf['N']}, 開放性:{bf['O']}
    科学的根拠(A)、図解(B)、性格適応(C)を徹底せよ。
    """
    
    try:
        return client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
            stream=True
        )
    except Exception as e:
        st.error(f"AIエラー: {e}")
        return None

# --- 6. メインレイアウト ---
def main():
    tab_chat, tab_insight, tab_blueprint = st.tabs(["💬 チャット", "🧬 分析", "📋 計画"])

    with tab_chat:
        st.title("Evidence Prime Pro")
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("メッセージを入力..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)

            with st.chat_message("assistant"):
                res_box = st.empty()
                full_res = ""
                completion = run_ai_agent()
                if completion:
                    for chunk in completion:
                        if hasattr(chunk, 'choices') and chunk.choices:
                            delta = chunk.choices.delta
                            if hasattr(delta, 'content') and delta.content:
                                full_res += delta.content
                                res_box.markdown(full_res + "▌")
                    res_box.markdown(full_res)
                    st.session_state.messages.append({"role": "assistant", "content": full_res})

    with tab_insight:
        st.subheader("🧬 性格・成長分析")
        if PLOTLY_AVAILABLE:
            bf = st.session_state.memory["big_five"]
            fig = go.Figure(data=go.Scatterpolar(
                r=[bf['E'], bf['A'], bf['C'], bf['N'], bf['O']],
                theta=['外向', '協調', '勤勉', '繊細', '開放'], fill='toself', line_color=main_color
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0,5])),
                paper_bgcolor='rgba(0,0,0,0)', font_color="white", height=350
            )
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        opts = [1, 2, 3, 4, 5]
        col1, col2 = st.columns(2)
        with col1:
            e = st.select_slider("外向性", options=opts, value=bf['E'])
            c = st.select_slider("勤勉性", options=opts, value=bf['C'])
        with col2:
            n = st.select_slider("神経症傾向", options=opts, value=bf['N'])
            o = st.select_slider("開放性", options=opts, value=bf['O'])
        
        if st.button("プロファイルを同期 🧠"):
            st.session_state.memory["big_five"].update({"E":e, "C":c, "N":n, "O":o})
            save_memory()
            st.success("同期完了！")

    with tab_blueprint:
        st.header("📋 アクションプラン")
        st.table(pd.DataFrame([{"項目": "準備中", "詳細": "対話を開始してください"}]))

if __name__ == "__main__":
    main()
