import streamlit as st
from groq import Groq
import urllib.parse
import json
import os
from datetime import datetime
import pandas as pd

# --- 1. 定数・設定 ---
DB_FILE = "user_memory.json"
APP_TITLE = "🧬 Evidence Prime Pro: Grand Vision"

# --- 2. 永続化エンジン (C: 記憶機能) ---
class MemoryEngine:
    @staticmethod
    def load():
        """ファイルから過去の記憶をロード"""
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"personality": {}, "history_summary": "", "habits": []}

    @staticmethod
    def save(data):
        """現在の状態をファイルに保存"""
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

# --- 3. UI/UX デザインシステム ---
def apply_ultra_theme():
    st.set_page_config(page_title=APP_TITLE, page_icon="🧬", layout="wide")
    main_color = st.session_state.get("theme_color", "#4A90E2")
    st.markdown(f"""
        <style>
        .stApp {{ background: #0F1116; color: #E0E0E0; }}
        .stButton>button {{
            background: linear-gradient(45deg, {main_color}, #2C3E50);
            color: white; border: none; border-radius: 12px; font-weight: bold;
            transition: 0.3s; width: 100%;
        }}
        .stButton>button:hover {{ transform: translateY(-2px); box-shadow: 0 4px 20px {main_color}66; }}
        .memory-card {{
            background: rgba(255, 255, 255, 0.05); border-radius: 15px;
            padding: 20px; border: 1px solid {main_color}44;
        }}
        </style>
        """, unsafe_allow_html=True)

# --- 4. 初期化 ---
if "auth" not in st.session_state: st.session_state.auth = False
if "memory" not in st.session_state: st.session_state.memory = MemoryEngine.load()
if "messages" not in st.session_state: st.session_state.messages = []
if "temp_schedule" not in st.session_state: st.session_state.temp_schedule = None
if "theme_color" not in st.session_state: st.session_state.theme_color = "#4A90E2"

apply_ultra_theme()

# --- 5. 認証 ---
if not st.session_state.auth:
    st.title("🛡️ Secure Access System")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pwd = st.text_input("Enter Command Key:", type="password")
        if st.button("AUTHENTICATE"):
            if pwd == st.secrets.get("APP_PASSWORD", "absolute-proof"):
                st.session_state.auth = True
                st.rerun()
    st.stop()

# --- 6. AI コアロジック (A, B, C の統合) ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def process_ai_request(user_input):
    # C: 過去の要約と性格をコンテキストに注入
    m = st.session_state.memory
    sys_prompt = f"""あなたは「Evidence Prime Pro」の統括知能です。
    【ユーザープロファイル】: {m['personality']}
    【過去の対話要約】: {m['history_summary']}
    
    【A: 信頼性】回答の根拠となるキーワードを 'RESOURCES: [ワード1, ワード2]' で出力せよ。
    【B: 計画】具体的な解決策を以下のJSON形式で回答内に埋め込め。
    ```json
    {{"weekly_plan": [{{"day": "Mon", "action": "..."}}, ...]}}
    ```
    """
    
    # 実行
    messages = [{"role": "system", "content": sys_prompt}] + st.session_state.messages
    response = client.chat.completions.create(
        messages=messages,
        model="llama-3.3-70b-versatile",
        temperature=0.6
    ).choices[0].message.content
    
    return response

# --- 7. メインインターフェース (タブ構造) ---
tab1, tab2, tab3, tab4 = st.tabs(["💬 Quantum Chat", "📅 Action Plan", "🧠 Core Memory", "⚙️ System"])

# --- Tab 1: チャット & A (信頼性) ---
with tab1:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("エビデンスに基づく分析を開始..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.spinner("Accessing Neural Databases..."):
            res_content = process_ai_request(prompt)
            
            # B: スケジュールデータの抽出
            if "```json" in res_content:
                try:
                    js_str = res_content.split("```json")[1].split("```")[0]
                    st.session_state.temp_schedule = json.loads(js_str).get("weekly_plan")
                except: pass

            with st.chat_message("assistant"):
                st.markdown(res_content.split("```json")[0]) # JSONを除いて表示
                
                # A: リソースリンクの生成
                if "RESOURCES:" in res_content:
                    st.divider()
                    st.write("🌐 **Verification Nodes:**")
                    r_part = res_content.split("RESOURCES:")[-1].strip(" []").split(",")
                    cols = st.columns(len(r_part))
                    for i, kw in enumerate(r_part):
                        url = f"https://google.com{urllib.parse.quote(kw.strip())}+evidence"
                        cols[i].link_button(f"🔗 {kw.strip()}", url)

            st.session_state.messages.append({"role": "assistant", "content": res_content})

# --- Tab 2: 行動計画 (B: 実行力) ---
with tab2:
    st.header("Weekly Strategic Plan")
    if st.session_state.temp_schedule:
        df = pd.DataFrame(st.session_state.temp_schedule)
        st.table(df)
        if st.button("📝 この計画を長期記憶に保存"):
            st.session_state.memory["habits"] = st.session_state.temp_schedule
            MemoryEngine.save(st.session_state.memory)
            st.success("記憶バンクに書き込みました。")
    else:
        st.info("チャットで具体的な目標を相談すると、ここに計画が生成されます。")

# --- Tab 3: 記憶管理 (C: 記憶) ---
with tab3:
    st.header("Neural Memory Bank")
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.subheader("Personality Mapping")
        # 簡易診断フォーム
        new_p = st.text_area("自分自身の性格や現在の状況をAIに教え込む:", value=json.dumps(st.session_state.memory["personality"]))
        if st.button("Update Profile"):
            try:
                st.session_state.memory["personality"] = json.loads(new_p)
                MemoryEngine.save(st.session_state.memory)
                st.rerun()
            except: st.error("JSON形式で入力してください。")

    with col_r:
        st.subheader("Context Summary")
        summary = st.text_area("対話の要約（AIが長期的に記憶する内容）:", value=st.session_state.memory["history_summary"])
        if st.button("Sync Summary"):
            st.session_state.memory["history_summary"] = summary
            MemoryEngine.save(st.session_state.memory)
            st.success("同期完了。")

# --- Tab 4: システム設定 ---
with tab4:
    st.subheader("Global Configuration")
    st.session_state.theme_color = st.color_picker("Brand Identity Color", st.session_state.theme_color)
    if st.button("🔴 Factory Reset"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.session_state.clear()
        st.rerun()
