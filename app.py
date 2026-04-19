import streamlit as st
from groq import Groq
import urllib.parse
import json
import os
from datetime import datetime
import pandas as pd

# --- 1. 定数・設定 ---
DB_FILE = "user_memory.json"
APP_TITLE = "🧬 Evidence Prime Pro"

# --- 2. 永続化エンジン (C: 記憶機能) ---
class MemoryEngine:
    @staticmethod
    def load():
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        # デフォルトの記憶構造
        return {
            "personality": {"分析": "未完了", "タイプ": "未設定"},
            "history_summary": "新規ユーザー。丁寧な日本語でサポートを開始せよ。",
            "habits": []
        }

    @staticmethod
    def save(data):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

# --- 3. デザイン・システム ---
def apply_ultra_theme():
    st.set_page_config(page_title=APP_TITLE, page_icon="🧬", layout="wide")
    main_color = st.session_state.get("theme_color", "#4A90E2")
    st.markdown(f"""
        <style>
        .stApp {{ background: #0F1116; color: #E0E0E0; }}
        .stButton>button {{
            background: linear-gradient(45deg, {main_color}, #2C3E50);
            color: white; border: none; border-radius: 12px; font-weight: bold;
            transition: 0.3s; width: 100%; height: 3em;
        }}
        .stButton>button:hover {{ transform: translateY(-2px); box-shadow: 0 4px 20px {main_color}66; }}
        .stTextInput>div>div>input {{ background-color: #1A1C23; color: white; border-radius: 10px; }}
        </style>
        """, unsafe_allow_html=True)

# --- 4. セッション初期化 ---
if "auth" not in st.session_state: st.session_state.auth = False
if "memory" not in st.session_state: st.session_state.memory = MemoryEngine.load()
if "messages" not in st.session_state: st.session_state.messages = []
if "temp_schedule" not in st.session_state: st.session_state.temp_schedule = None
if "theme_color" not in st.session_state: st.session_state.theme_color = "#4A90E2"
if "lang" not in st.session_state: st.session_state.lang = "日本語"

apply_ultra_theme()

# --- 5. 認証ゲート ---
if not st.session_state.auth:
    st.title("🛡️ システム認証")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.write("Evidence Prime Pro へアクセスするには合言葉が必要です。")
        pwd = st.text_input("合言葉（APP_PASSWORD）を入力:", type="password")
        if st.button("認証して起動"):
            if pwd == st.secrets.get("APP_PASSWORD", "absolute-proof"):
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("合言葉が正しくありません。")
    st.stop()

# --- 6. AI コア (Groq Llama 3.3) ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("APIキーが設定されていません。")
    st.stop()

def process_ai_request():
    m = st.session_state.memory
    sys_prompt = f"""あなたは世界最高峰の科学エビデンス専門家です。
    【対応言語】: {st.session_state.lang}
    【ユーザー性格】: {json.dumps(m['personality'], ensure_ascii=False)}
    【過去のコンテキスト】: {m['history_summary']}
    
    【ルール】
    1. 常に科学的根拠(Tier 1~4)に基づき、日本語で回答せよ。
    2. 回答の根拠となるキーワードを 'リソース: [ワード1, ワード2]' の形式で最後に出力せよ。
    3. 行動計画を提案する場合は、必ず以下のJSON形式を含めよ。
    ```json
    {{"weekly_plan": [{{"day": "月", "action": "..."}}, ...]}}
    ```
    """
    
    response = client.chat.completions.create(
        messages=[{"role": "system", "content": sys_prompt}] + st.session_state.messages,
        model="llama-3.3-70b-versatile",
        temperature=0.6
    ).choices[0].message.content
    return response

# --- 7. メインレイアウト ---
tab1, tab2, tab3, tab4 = st.tabs(["💬 究極チャット", "📅 行動計画", "🧠 長期記憶", "⚙️ 設定"])

# --- Tab 1: チャット ---
with tab1:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("知りたいエビデンスや悩みを入力..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.spinner("科学データベースをスキャン中..."):
            res_content = process_ai_request()
            
            # スケジュール抽出
            if "```json" in res_content:
                try:
                    js_str = res_content.split("```json")[1].split("```")[0]
                    st.session_state.temp_schedule = json.loads(js_str).get("weekly_plan")
                except: pass

            with st.chat_message("assistant"):
                st.markdown(res_content.split("```json")[0]) # 本文のみ
                
                # リソースリンク生成
                if "リソース:" in res_content:
                    st.divider()
                    st.write("🌐 **信頼性検証リンク:**")
                    kw_part = res_content.split("リソース:")[-1].strip(" []").split(",")
                    cols = st.columns(len(kw_part))
                    for i, kw in enumerate(kw_part):
                        q = kw.strip()
                        url = f"https://google.com{urllib.parse.quote(q)}+エビデンス"
                        cols[i].link_button(f"🔗 {q}", url)

            st.session_state.messages.append({"role": "assistant", "content": res_content})

# --- Tab 2: 行動計画 ---
with tab2:
    st.header("週間エビデンス・プラン")
    if st.session_state.temp_schedule:
        df = pd.DataFrame(st.session_state.temp_schedule)
        st.table(df)
        if st.button("📝 この計画を長期記憶に保存する"):
            st.session_state.memory["habits"] = st.session_state.temp_schedule
            MemoryEngine.save(st.session_state.memory)
            st.success("記憶バンク（JSONファイル）に保存しました。")
    else:
        st.info("チャットで具体的な目標や改善したい習慣を相談してください。")

# --- Tab 3: 記憶管理 ---
with tab3:
    st.header("ニューラル・メモリ・バンク")
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.subheader("性格・プロフィール")
        p_json = json.dumps(st.session_state.memory["personality"], ensure_ascii=False, indent=2)
        new_p = st.text_area("AIが認識しているあなたのプロファイル（JSON形式）:", value=p_json, height=200)
        if st.button("プロフィールを更新"):
            try:
                st.session_state.memory["personality"] = json.loads(new_p)
                MemoryEngine.save(st.session_state.memory)
                st.success("更新完了")
            except: st.error("正しいJSON形式で入力してください。")

    with col_r:
        st.subheader("対話コンテキストの要約")
        summary = st.text_area("AIが長期的に保持しているあなたの文脈:", value=st.session_state.memory["history_summary"], height=200)
        if st.button("要約を同期"):
            st.session_state.memory["history_summary"] = summary
            MemoryEngine.save(st.session_state.memory)
            st.success("同期完了")

# --- Tab 4: 設定 ---
with tab4:
    st.subheader("システム設定")
    st.session_state.lang = st.selectbox("使用言語", ["日本語", "English", "한국어", "中文"])
    st.session_state.theme_color = st.color_picker("ブランドカラー", st.session_state.theme_color)
    
    st.divider()
    if st.button("🔴 全データをリセット（工場出荷状態）"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.session_state.clear()
        st.rerun()
