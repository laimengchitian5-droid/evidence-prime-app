import streamlit as st
from groq import Groq
import urllib.parse
import json
from datetime import datetime
import pandas as pd

# --- 1. 究極のデザイン・システム ---
class ThemeEngine:
    @staticmethod
    def apply(main_color, mode):
        bg = "#121212" if mode == "Dark" else "#F0F2F6"
        txt = "#FFFFFF" if mode == "Dark" else "#1E1E1E"
        card_bg = "rgba(255, 255, 255, 0.05)" if mode == "Dark" else "rgba(255, 255, 255, 0.7)"
        
        st.markdown(f"""
            <style>
            .stApp {{ background: {bg}; color: {txt}; font-family: 'Inter', sans-serif; }}
            .stTabs [data-baseweb="tab-list"] {{ gap: 24px; }}
            .stTabs [data-baseweb="tab"] {{
                background-color: transparent; border-radius: 4px; color: {txt}; font-weight: 600;
            }}
            div[data-testid="stExpander"] {{
                background: {card_bg}; backdrop-filter: blur(10px); border-radius: 15px; border: 1px solid {main_color}44;
            }}
            .stButton>button {{
                width: 100%; border-radius: 30px; background: linear-gradient(45deg, {main_color}, {main_color}88);
                color: white; border: none; padding: 10px 20px; font-weight: 700; transition: 0.3s;
            }}
            .stButton>button:hover {{ transform: translateY(-2px); box-shadow: 0 4px 15px {main_color}66; }}
            </style>
            """, unsafe_allow_html=True)

# --- 2. AIコア・ロジック ---
class EvidenceCore:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)

    def generate_response(self, messages, personality, plugins):
        sys_instr = f"""あなたは「Evidence Prime Pro」の核心AIです。
        ユーザー性格: {json.dumps(personality)}
        【必須ルール】
        1. 科学的根拠（エビデンス）のティアを明記せよ。
        2. 手順は必ず '```mermaid\\ngraph TD' で図解せよ(プラグイン有効時)。
        3. 回答の末尾に必ず 'SEARCH_WORD: [キーワード]' を含めよ。
        4. 性格に合わせ、ユーザーのモチベーションを最大化する口調を使え。"""
        
        response = self.client.chat.completions.create(
            messages=[{"role": "system", "content": sys_instr}] + messages,
            model="llama-3.3-70b-versatile",
            temperature=0.7
        )
        return response.choices[0].message.content

# --- 3. セッション・マネージャー ---
def init_session():
    defaults = {
        "messages": [], "personality": {"status": "未診断", "type": "N/A"},
        "auth": False, "habits": [], "score": 0, "theme_color": "#4A90E2", "theme_mode": "Dark"
    }
    for key, val in defaults.items():
        if key not in st.session_state: st.session_state[key] = val

init_session()

# --- 4. 認証・セキュリティ ---
if not st.session_state.auth:
    st.title("💠 Evidence Prime Pro")
    with st.container():
        pwd = st.text_input("🔑 System Access Key", type="password")
        if st.button("Unlock Core"):
            if pwd == st.secrets.get("APP_PASSWORD", "absolute-proof"):
                st.session_state.auth = True
                st.rerun()
    st.stop()

# --- 5. メインエンジン起動 ---
core = EvidenceCore(st.secrets["GROQ_API_KEY"])
ThemeEngine.apply(st.session_state.theme_color, st.session_state.theme_mode)

# --- 6. サイドバー・コントロールセンター ---
with st.sidebar:
    st.image("https://icons8.com", width=80)
    st.title("Control Center")
    
    with st.expander("🎨 Appearance"):
        st.session_state.theme_color = st.color_picker("Brand Color", st.session_state.theme_color)
        st.session_state.theme_mode = st.radio("Mode", ["Dark", "Light"])
    
    with st.expander("🛠️ Plug-ins"):
        p_graph = st.toggle("Mermaid Engine", value=True)
        p_search = st.toggle("Real-time Search", value=True)
        p_stats = st.toggle("Analytical Stats", value=True)

    if st.button("🔴 Reset Memory"):
        st.session_state.messages = []
        st.rerun()

# --- 7. アプリ・インターフェース ---
t1, t2, t3, t4 = st.tabs(["🧬 Diagnostic", "💬 Quantum Chat", "📈 Analytics", "⚙️ Settings"])

# --- Tab 1: 高度な診断 ---
with t1:
    st.subheader("Neural Personality Mapping")
    with st.form("advanced_diag"):
        col_a, col_b = st.columns(2)
        q1 = col_a.select_slider("好奇心レベル", options=range(1, 11))
        q2 = col_b.select_slider("論理性 vs 直感性", options=range(1, 11))
        q3 = st.text_area("あなたの現在の最大の目標は？")
        if st.form_submit_button("Map Identity"):
            st.session_state.personality = {"score": (q1+q2)/2, "goal": q3, "status": "診断済み"}
            st.toast("Identity Mapped Successfully!")

# --- Tab 2: 究極の対話 ---
with t2:
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("指令を入力..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.spinner("AI Thinking..."):
            res = core.generate_response(st.session_state.messages, st.session_state.personality, {})
            
            with st.chat_message("assistant"):
                # Mermaidの抽出と描画
                if "```mermaid" in res and p_graph:
                    parts = res.split("```mermaid")
                    st.markdown(parts[0])
                    st.mermaid(parts[1].split("```")[0])
                    st.markdown(parts[1].split("```")[-1])
                else:
                    st.markdown(res)
                
                # 検索連携
                if "SEARCH_WORD:" in res and p_search:
                    word = res.split("SEARCH_WORD:")[-1].strip(" []")
                    st.link_button(f"🌐 外部エビデンスを確認: {word}", f"https://google.com{urllib.parse.quote(word)}")
                
                if st.button("🚀 この知識を習慣化（トラッカーへ）"):
                    st.session_state.habits.append({"task": prompt, "time": datetime.now().strftime("%H:%M")})
                    st.session_state.score += 10

        st.session_state.messages.append({"role": "assistant", "content": res})

# --- Tab 3: 分析ダッシュボード ---
with t3:
    st.subheader("Performance Analytics")
    if p_stats:
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Experience", f"{st.session_state.score} XP")
        m2.metric("Habits Formed", len(st.session_state.habits))
        m3.metric("Neural Sync", f"{st.session_state.personality.get('score', 0) * 10}%")
        
        if st.session_state.habits:
            df = pd.DataFrame(st.session_state.habits)
            st.table(df)
    else:
        st.info("プラグインを有効にしてください。")

# --- Tab 4: 内部システム設定 ---
with t4:
    st.subheader("System Configuration")
    st.write("Current Session ID:", id(st.session_state))
    st.json(st.session_state.personality)
