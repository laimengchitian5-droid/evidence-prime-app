import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from groq import Groq

# Plotlyのインポート（可視化エンジン）
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# --- 1. 基本設定 ---
st.set_page_config(
    page_title="Evidence Prime Pro | 究極AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. セキュリティシステム（合言葉認証） ---
def check_password():
    if st.session_state.get("authenticated"):
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
    
    st.title("🔒 システムアクセス認証")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.write("17歳の開発者による次世代AIプラットフォーム")
        target_pwd = st.secrets.get("password", "admin")
        pwd = st.text_input("合言葉を入力してください", type="password")
        if st.button("コア・システムを起動 🚀", use_container_width=True):
            if pwd == target_pwd:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("合言葉が正しくありません。")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

check_password()

# --- 3. 記憶システム ---
MEMORY_FILE = "user_memory_v2.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return {
        "big_five": {"E": 3, "A": 3, "C": 3, "N": 3, "O": 3},
        "achievements": [{"date": datetime.now().strftime("%Y-%m-%d"), "score": 50}],
        "theme_color": "#6366f1"
    }

def save_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.memory, f, indent=4, ensure_ascii=False)

if "memory" not in st.session_state:
    st.session_state.memory = load_memory()
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. デザインエンジン ---
def apply_ui_theme():
    st.sidebar.title("🛠️ システム制御板")
    theme_choice = st.sidebar.select_slider(
        "テーマ・パレット",
        options=["サイバー", "オーシャン", "フォレスト", "サクラ", "ラヴァ"]
    )
    palette = {
        "サイバー": "#6366f1", "オーシャン": "#0ea5e9", 
        "フォレスト": "#10b981", "サクラ": "#f472b6", "ラヴァ": "#f43f5e"
    }
    main_color = palette[theme_choice]
    
    st.markdown(f"""
        <style>
        .stApp {{
            background: radial-gradient(circle at top right, {main_color}15, #020617);
            color: #f1f5f9;
        }}
        div[data-testid="stChatMessage"] {{
            background: rgba(255, 255, 255, 0.02);
            border-left: 5px solid {main_color};
            border-radius: 15px;
            backdrop-filter: blur(10px);
            margin-bottom: 15px;
        }}
        .stButton>button {{
            background: linear-gradient(90deg, {main_color}aa, {main_color}44);
            border: none; color: white; border-radius: 12px;
        }}
        </style>
    """, unsafe_allow_html=True)
    return main_color

main_color = apply_ui_theme()

# --- 5. 解析エンジン (修正済み) ---
def render_analysis_tab():
    if not PLOTLY_AVAILABLE:
        st.warning("解析エンジンをロード中...")
        return

    st.subheader("📊 性格・成長分析")
    col1, col2 = st.columns(2)
    
    with col1:
        bf = st.session_state.memory["big_five"]
        categories = ['外向性', '協調性', '勤勉性', '神経症傾向', '開放性']
        values = [bf['E'], bf['A'], bf['C'], bf['N'], bf['O']]
        
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=values, theta=categories, fill='toself',
            line=dict(color=main_color), marker=dict(color=main_color)
        ))
        # range=[1, 5] を明記してバグを修正
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[1, 5], gridcolor="#334155"), bgcolor="rgba(0,0,0,0)"),
            paper_bgcolor='rgba(0,0,0,0)', font_color="#f1f5f9"
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col2:
        df = pd.DataFrame(st.session_state.memory["achievements"])
        fig_line = px.line(df, x="date", y="score", title="知的成長速度")
        fig_line.update_traces(line_color=main_color, mode='lines+markers')
        fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#f1f5f9")
        st.plotly_chart(fig_line, use_container_width=True)

# --- 6. AIコア ---
def run_ai_agent(user_input):
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        st.error("GROQ_API_KEY が設定されていません。")
        return None
    
    client = Groq(api_key=api_key)
    bf = st.session_state.memory["big_five"]
    
    system_prompt = f"""
    あなたは『Evidence Prime Pro』です。
    ユーザー性格特性: 外向性:{bf['E']}, 協調性:{bf['A']}, 勤勉性:{bf['C']}, 神経症傾向:{bf['N']}, 開放性:{bf['O']}
    上記特性に基づき、科学的根拠(A)、図解(B)、性格適応(C)を徹底して日本語で回答せよ。
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

# --- 7. メインUI ---
def main():
    tab_chat, tab_insight, tab_blueprint, tab_core = st.tabs(["💬 対話", "🧬 分析", "📋 計画", "⚙️ 管理"])

    with tab_chat:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("課題を入力..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)

            with st.chat_message("assistant"):
                res_box = st.empty()
                full_res = ""
                completion = run_ai_agent(prompt)
                if completion:
                    for chunk in completion:
                        content = chunk.choices.delta.content
                        if content:
                            full_res += content
                            res_box.markdown(full_res + "▌")
                    res_box.markdown(full_res)
                    st.session_state.messages.append({"role": "assistant", "content": full_res})

    with tab_insight:
        render_analysis_tab()
        bf = st.session_state.memory["big_five"]
        opts = [1, 2, 3, 4, 5]
        col1, col2 = st.columns(2)
        with col1:
            e = st.select_slider("外向性", options=opts, value=bf['E'])
            a = st.select_slider("協調性", options=opts, value=bf['A'])
            c = st.select_slider("勤勉性", options=opts, value=bf['C'])
        with col2:
            n = st.select_slider("神経症傾向", options=opts, value=bf['N'])
            o = st.select_slider("開放性", options=opts, value=bf['O'])
        
        if st.button("プロファイルを同期"):
            st.session_state.memory["big_five"] = {"E": e, "A": a, "C": c, "N": n, "O": o}
            save_memory()
            st.success("同期完了！AIがあなたに合わせて進化しました。")

    with tab_blueprint:
        st.header("📋 構造化プラン")
        st.table(pd.DataFrame([{"項目": "データなし", "詳細": "チャットで計画を生成してください"}]))

    with tab_core:
        st.json(st.session_state.memory)
        if st.button("リセット"):
            st.session_state.memory = load_memory()
            st.rerun()

if __name__ == "__main__":
    main()
