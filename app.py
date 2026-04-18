import streamlit as st
from groq import Groq

# --- ページ設定 ---
st.set_page_config(page_title="Evidence Prime Pro", layout="wide", page_icon="🧪")

# --- デザイン調整（アプリ感MAX） ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { 
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        color: black; font-weight: bold; border-radius: 30px; border: none; height: 3.5em;
    }
    .stTextInput>div>div>input { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- サイドバー ---
with st.sidebar:
    st.title("🧪 Prime Pro")
    # Googleの自動入力が効くように、普通の入力欄に戻します
    api_key = st.text_input("Groq API Keyを入力", type="password")
    
    st.divider()
    gender = st.radio("性別", ["男性", "女性", "回答しない"])
    conscience = st.slider("計画性", 0, 100, 50)
    st.info("17歳が開発した爆速科学分析ツール。")

# --- メイン画面 ---
st.title("💎 Evidence Prime Pro")

topic = st.text_input("分析したいトピックを入力", placeholder="例：最高の朝のルーティン")

if st.button("🚀 爆速分析を実行"):
    if not api_key:
        st.warning("サイドバーにAPIキーを入力してください。")
    else:
        try:
            client = Groq(api_key=api_key)
            system_prompt = f"""
            あなたは世界最高峰の科学コーチです。17歳の若者が使う専用アプリとして回答してください。
            ユーザー属性: 性別{gender}, 計画性{conscience}/100
            1. 📊 実用性能ティア表
            2. 🛣️ 実践フローチャート
            3. 💡 科学的ライフハック
            4. 📅 カレンダー登録案
            """

            with st.spinner("⚡ 解析中..."):
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": topic}
                    ],
                    model="llama-3.3-70b-versatile",
                )
                st.markdown(chat_completion.choices.message.content)
                
                st.divider()
                st.link_button(f"📺 '{topic}' の解説動画を検索", f"https://youtube.com{topic}+科学")

        except Exception as e:
            st.error(f"エラーが発生しました。APIキーを確認してください。\n(Error: {e})")
