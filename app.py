import streamlit as st
from groq import Groq

# --- ページ設定 ---
st.set_page_config(page_title="Evidence Prime Pro", layout="wide", page_icon="🧪")

# --- デザイン調整 ---
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
    # Googleの自動入力が効くようにパスワード形式の入力欄
    api_key = st.text_input("Groq API Keyを入力", type="password")
    
    st.divider()
    gender = st.radio("性別", ["男性", "女性", "回答しない"])
    conscience = st.slider("計画性", 0, 100, 50)
    st.info("17歳が開発した爆速科学分析ツール。")

# --- メイン画面 ---
st.title("💎 Evidence Prime Pro")

topic = st.text_input("分析したいトピックを入力", placeholder="例：テスト勉強の効率を最大化する")

if st.button("🚀 爆速分析を実行"):
    if not api_key:
        st.warning("サイドバーにAPIキーを入力してください。")
    else:
        try:
            client = Groq(api_key=api_key)
            system_prompt = f"""
            あなたは世界最高峰の科学コーチです。17歳の若者が使う専用アプリとして回答してください。
            ユーザー属性: 性別{gender}, 計画性{conscience}/100
            
            【回答構成】
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
                
                # ✅ 修正：回答を正しく取り出す形式に変更
                answer = chat_completion.choices[0].message.content
                
                st.markdown(answer)
                
                st.divider()
                st.link_button(f"📺 '{topic}' の解説動画を検索", f"https://youtube.com{topic}+科学")

        except Exception as e:
            # 💡 エラー内容がわかりやすいように表示
            st.error(f"エラーが発生しました。\n(Error: {e})")
