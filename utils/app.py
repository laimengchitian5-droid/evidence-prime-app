import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from groq import Groq

# Plotlyのインポート（スマホ環境での安定性を重視）
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# --- 1. 基本設定（スマホでの見やすさを最優先） ---
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
    
    col1, col2, col3 = st.columns([1, 10, 1])
    with col2:
        st.write("17yo Developer's Visionary AI")
        pwd = st.text_input("合言葉（半角入力）", type="password")
        if st.button("ログイン 🚀", use_container_width=True):
            if pwd == target_pwd:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("合言葉が正しくありません。半角で入力してください。")
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
        "achievements": [{"date": datetime.now().strftime("%Y-%m-%d"), "score": 50}],
        "language": "日本語"
    }

def save_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.memory, f, indent=4, ensure_ascii=False)

if "memory" not in st.session_state:
    st.session_state.memory = load_memory()
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. デザインエンジン（スマホ最適化CSS） ---
def apply_ui_theme():
    # サイドバーはスマホでは閉じられているためデフォルト色を指定
    main_color = "#6366f1" 
    
    st.markdown(f"""
        <style>
        .stApp {{
            background: radial-gradient(circle at top right, {main_color}15, #020617);
            color: #f1f5f9;
        }}
        /* スマホの狭い画面でも文字を読みやすく */
        div[data-testid="stChatMessage"] {{
            background: rgba(255, 255, 255, 0.02);
            border-left: 3px solid {main_color};
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 10px;
            font-size: 15px;
        }}
        .stButton>button {{
            background: {main_color}aa;
            color: white; border-radius: 8px; border: none;
            width: 100%; height: 3.5rem; /* スマホで押しやすいサイズ */
        }}
        </style>
    """, unsafe_allow_html=True)
    return main_color

main_color = apply_ui_theme()

# --- 5. AIコア（AttributeError/空データ対策済み） ---
def run_ai_agent():
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        st.error("APIキーが設定されていません。")
        return None
    
    client = Groq(api_key=api_key)
    bf = st.session_state.memory["big_five"]
    lang = st.session_state.memory.get("language", "日本語")
    
    system_prompt = f"""
    あなたは『Evidence Prime Pro』です。日本語で回答してください。
    ユーザー性格: 外向:{bf['E']}, 協調:{bf['A']}, 勤勉:{bf['C']}, 繊細:{bf['N']}, 開放:{bf['O']}
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
                        # 安全なデータアクセス
                        if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                            delta = chunk.choices[0].delta
                            if hasattr(delta, 'content') and delta.content:
                                full_res += delta.content
                                res_box.markdown(full_res + "▌")
                    res_box.markdown(full_res)
                    st.session_state.messages.append({"role": "assistant", "content": full_res})

    with tab_insight:
        st.subheader("🧬 科学的プロファイル")
        if PLOTLY_AVAILABLE:
            bf = st.session_state.memory["big_five"]
            fig = go.Figure(data=go.Scatterpolar(
                r=[bf['E'], bf['A'], bf['C'], bf['N'], bf['O']],
                theta=['外向', '協調', '勤勉', '繊細', '開放'], fill='toself', line_color=main_color
            ))
            # 範囲を 0-5 に固定してエラー防止
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                paper_bgcolor='rgba(0,0,0,0)', font_color="white", height=300
            )
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        # スライダーの選択肢をリストで定義
        opts = [1, 2, 3, 4, 5]
        e = st.select_slider("外向性", options=opts, value=bf['E'])
        c = st.select_slider("勤勉性", options=opts, value=bf['C'])
        
        if st.button("AIに同期 🧠"):
            st.session_state.memory["big_five"].update({"E":e, "C":c})
            save_memory()
            st.success("同期完了！")

    with tab_blueprint:
        st.header("📋 プランニング")
        st.info("対話を開始すると、ここに計画が構築されます。")

if __name__ == "__main__":
    main()
