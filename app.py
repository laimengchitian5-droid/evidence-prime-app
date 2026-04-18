import streamlit as st
from groq import Groq

# 1. ページ基本設定
st.set_page_config(page_title="Evidence Prime Pro", page_icon="🧬", layout="wide")

# カスタムCSS（エラーを修正済み：unsafe_allow_html=True）
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #007BFF; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 認証機能（合言葉） ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔑 Evidence Prime Pro")
    st.info("このアプリは招待制です。開発者から共有された合言葉を入力してください。")
    
    input_pwd = st.text_input("合言葉を入力", type="password")
    if st.button("ログイン"):
        if input_pwd == st.secrets["APP_PASSWORD"]:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("合言葉が正しくありません。")
    st.stop()

# --- 3. 精密性格診断（初回ログイン時のみ） ---
if "user_profile" not in st.session_state:
    st.title("🧠 パーソナル診断")
    st.write("科学的な分析結果をあなた専用にカスタマイズするため、5つの質問に答えてください。")
    
    with st.form("personality_form"):
        col1, col2 = st.columns(2)
        with col1:
            q1 = st.select_slider("1. 予定は事前にしっかり組みたい", options=["全く違う", "普通", "超そう"])
            q2 = st.select_slider("2. 新しい効率化術を試すのが好きだ", options=["全く違う", "普通", "超そう"])
        with col2:
            q3 = st.select_slider("3. 週末はアクティブに動きたい", options=["全く違う", "普通", "超そう"])
            q4 = st.select_slider("4. 正論よりも寄り添いを重視する", options=["全く違う", "普通", "超そう"])
        
        q5 = st.select_slider("5. プレッシャーに強い方だ", options=["全く違う", "普通", "超そう"])
        gender = st.radio("性別", ["男性", "女性", "回答しない"], horizontal=True)
        
        if st.form_submit_button("診断を完了してアプリを開始"):
            st.session_state.user_profile = {
                "planning": q1, "curiosity": q2, "activity": q3, "empathy": q4, "stress": q5, "gender": gender
            }
            st.rerun()
    st.stop()

# --- 4. メイン分析機能（認証＆診断完了後に表示） ---
# Secretsにキーがない場合のエラー回避
if "GROQ_API_KEY" not in st.secrets:
    st.error("Groq APIキーがSecretsに設定されていません。")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.sidebar.title("👤 Your Profile")
p = st.session_state.user_profile
st.sidebar.write(f"タイプ: {p['gender']} / {p['planning']}派")
if st.sidebar.button("診断をやり直す"):
    del st.session_state.user_profile
    st.rerun()

st.title("🧬 Evidence Prime Pro")
query = st.text_input("知りたいトピックを入力してください", placeholder="例：朝のスムージーの効果、集中力を上げる方法など")

if query:
    with st.spinner("Llama 3.3 70Bがエビデンスを精査中..."):
        # プロファイルに基づいたパーソナライズ命令
        tone = "共感重視で優しく" if p['empathy'] == "超そう" else "論理重視で端的に"
        detail = "ステップバイステップの計画" if p['planning'] == "超そう" else "即効性のあるヒント"
        
        system_prompt = f"""
        あなたは科学的エビデンスの専門家です。17歳の開発者のパートナーとして、以下のユーザーに最適化された回答をしてください。
        
        【ユーザー情報】
        性別: {p['gender']}, 計画性: {p['planning']}, 好奇心: {p['curiosity']}, メンタル耐性: {p['stress']}
        
        【回答ルール】
        1. ティア表: 科学的根拠の強さをS〜Cでランク付け
        2. フローチャート: {detail}をテキストで作成
        3. ライフハック: ユーザーの性格に合わせた具体的なアドバイス
        4. カレンダー案: 性格に合わせたスケジュール提案
        
        トーン: {tone}
        """

        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
            model="llama-3.3-70b-versatile",
        )
        
        # 結果表示
        st.markdown(chat_completion.choices.message.content)
        
        # YouTube検索リンク
        st.markdown(f"--- \n### 🎥 関連動画をチェック\n[YouTubeで「{query} 科学」を検索](https://youtube.com{query}+科学)")
