import streamlit as st
from groq import Groq

# ページ設定
st.set_page_config(page_title="Evidence Prime Pro", page_icon="icon.png", layout="wide")

# --- 1. 認証機能（合言葉） ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔑 Evidence Prime Pro - 認証")
    pwd = st.text_input("合言葉を入力してください", type="password")
    if pwd == st.secrets["APP_PASSWORD"]:
        st.session_state.auth = True
        st.rerun()
    elif pwd:
        st.error("合言葉が違います。開発者に確認してください。")
    st.stop()

# --- 2. 精密性格診断（初回のみ） ---
if "user_profile" not in st.session_state:
    st.title("🧠 パーソナル診断")
    st.write("あなたに最適なエビデンスを届けるため、5つの質問に答えてください。")
    
    with st.form("personality_form"):
        st.subheader("あなたの傾向を教えてください")
        q1 = st.select_slider("1. 予定はしっかり立てて動きたい", options=["全く違う", "やや違う", "普通", "まあそう", "超そう"])
        q2 = st.select_slider("2. 新しい知識や効率化にワクワクする", options=["全く違う", "やや違う", "普通", "まあそう", "超そう"])
        q3 = st.select_slider("3. 休日は外で活動的に過ごしたい", options=["全く違う", "やや違う", "普通", "まあそう", "超そう"])
        q4 = st.select_slider("4. 正論よりも気持ちの納得感を大事にする", options=["全く違う", "やや違う", "普通", "まあそう", "超そう"])
        q5 = st.select_slider("5. プレッシャーを感じやすい", options=["全く違う", "やや違う", "普通", "まあそう", "超そう"])
        
        gender = st.selectbox("性別", ["男性", "女性", "回答しない"])
        
        if st.form_submit_button("診断を完了して分析を開始"):
            st.session_state.user_profile = {
                "planning": q1, "curiosity": q2, "activity": q3, "empathy": q4, "stress": q5, "gender": gender
            }
            st.rerun()
    st.stop()

# --- 3. メイン分析機能 ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("🧬 Evidence Prime Pro")
st.sidebar.info(f"診断完了：{st.session_state.user_profile['gender']} / {st.session_state.user_profile['planning']}派")

query = st.text_input("分析したいトピックを入力してください（例：カフェインの摂取タイミング）")

if query:
    with st.spinner("科学的エビデンスを抽出中..."):
        # プロファイルに基づいたシステムプロンプトの作成
        profile = st.session_state.user_profile
        system_prompt = f"""
        あなたは科学的エビデンスに基づき、17歳の開発者のパートナーとして回答するAIです。
        ユーザー属性: 性別:{profile['gender']}, 計画性:{profile['planning']}, 好奇心:{profile['curiosity']}, 共感性:{profile['empathy']}, メンタル耐性:{profile['stress']}
        
        以下の4構成で回答してください：
        1. エビデンス・ティア表（信頼度順）
        2. パーソナライズ・フローチャート（ユーザーの性格に合わせた手順）
        3. 即実践できるライフハック
        4. カレンダー連携案（計画性が高い場合は詳細に、低い場合はシンプルに）
        
        トーン：{'共感重視' if profile['empathy'] in ['まあそう', '超そう'] else '結論重視'}で回答してください。
        """

        # Groq API呼び出し (Llama 3.3 70B)
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            model="llama-3.3-70b-versatile",
        )
        
        response = chat_completion.choices[0].message.content
        st.markdown(response)
        
        # YouTubeリンクの自動生成
        st.markdown(f"--- \n### 🎥 関連動画をチェック\n[YouTubeで「{query} エビデンス」を検索](https://youtube.com{query}+evidence)")
