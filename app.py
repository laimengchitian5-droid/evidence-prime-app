import streamlit as st
from groq import Groq

# --- ページ設定（自作アイコンを適用） ---
st.set_page_config(
    page_title="Evidence Prime Pro", 
    layout="wide", 
    page_icon="icon.png"  # GitHubに置いたicon.pngが自動で反映されます
)

# --- SecretsからAPIキーを自動読み込み ---
# これにより、画面でのキー入力が一切不要になります
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("SecretsにGROQ_API_KEYが設定されていません。")
    st.stop()

# --- アプリらしい高級感のあるデザイン ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { 
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        color: black; font-weight: bold; border-radius: 30px; border: none;
        transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); opacity: 0.9; }
    .stTextInput>div>div>input { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- サイドバー ---
with st.sidebar:
    st.title("🧪 Prime Pro")
    st.caption("Developed by 17yo Visionary")
    st.divider()
    gender = st.radio("性別", ["男性", "女性", "回答しない"])
    conscience = st.slider("計画性", 0, 100, 50)
    st.info("このアプリはあなた専用です。APIキーは裏側で安全に保護されています。")

# --- メイン画面 ---
st.title("💎 Evidence Prime Pro")
st.markdown("### あなたの日常を、科学の力でアップグレードする。")

topic = st.text_input("分析したいトピックを入力", placeholder="例：テスト勉強の効率を最大化する")

if st.button("🚀 爆速分析を実行"):
    if not topic:
        st.warning("トピックを入力してください。")
    else:
        try:
            client = Groq(api_key=GROQ_API_KEY)
            system_prompt = f"""
            あなたは世界最高峰の科学コーチです。17歳の若者が使う専用アプリとして、非常に論理的かつ実践的な回答をしてください。
            ユーザー属性: 性別{gender}, 計画性{conscience}/100
            
            【回答形式】
            1. 📊 実用性能ティア表（S/A/Bランクで比較）
            2. 🛣️ 実践フローチャート（Step 1 → Step 2）
            3. 💡 科学的ライフハック
            4. 📅 カレンダー登録用メモ
            """

            with st.spinner("⚡ 思考の速度を超えて解析中..."):
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": topic}
                    ],
                    model="llama-3.3-70b-versatile",
                )
                answer = chat_completion.choices.message.content
                
                # 結果表示
                st.container()
                st.markdown(answer)
                
                # YouTubeリンク
                st.divider()
                st.link_button(f"📺 関連動画をチェック", f"https://youtube.com{topic}+科学")

        except Exception as e:
            st.error(f"エラーが発生しました。Secretsの設定を確認してください。\n(Error: {e})")
