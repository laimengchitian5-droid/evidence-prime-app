import streamlit as st
from groq import Groq

# --- 初期設定 ---
st.set_page_config(page_title="Evidence Prime Pro", layout="wide")

# セッション状態の初期化（履歴や診断結果を保存）
if "messages" not in st.session_state:
    st.session_state.messages = []
if "personality_result" not in st.session_state:
    st.session_state.personality_result = None
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# --- 認証機能 ---
if not st.session_state.authenticated:
    st.title("🔐 Evidence Prime Pro - Login")
    password = st.text_input("合言葉を入力してください", type="password")
    if st.button("ログイン"):
        if password == st.secrets["APP_PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("合言葉が違います。")
    st.stop()

# --- クライアント設定 ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- UI：タブ機能 ---
tab1, tab2, tab3 = st.tabs(["🧬 性格診断", "💬 メインチャット", "🛠️ エビデンス・ツール"])

# --- Tab 1: 性格診断 ---
with tab1:
    st.header("性格診断（Personalization）")
    if not st.session_state.personality_result:
        with st.form("personality_form"):
            q1 = st.radio("新しいことに挑戦するのが好きですか？", ["はい", "いいえ"])
            q2 = st.radio("計画を立てるのが得意ですか？", ["はい", "いいえ"])
            # 他の質問も同様に追加可能
            submitted = st.form_submit_button("診断する")
            if submitted:
                # 簡易的な診断ロジック（後で詳細化可能）
                res = f"挑戦的: {q1}, 計画的: {q2}"
                st.session_state.personality_result = res
                st.success("診断完了！内容を保存しました。")
    else:
        st.info(f"現在の診断結果: {st.session_state.personality_result}")
        if st.button("再診断する"):
            st.session_state.personality_result = None
            st.rerun()

# --- Tab 2: メインチャット (連続質問可能) ---
with tab2:
    st.header("Evidence Chat")
    
    # 履歴の表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ユーザー入力
    if prompt := st.chat_input("質問を入力してください（例：効率的な勉強法は？）"):
        # 履歴に追加
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AIへのリクエスト（診断結果をシステムプロンプトに含める）
        system_prompt = f"あなたは科学的根拠に基づき回答するプロです。ユーザーの性格: {st.session_state.personality_result}"
        
        # 履歴をすべて含めてAPIに投げることで「連続質問」に対応
        try:
            full_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages
            
            response = client.chat.completions.create(
                messages=full_messages,
                model="llama-3.3-70b-versatile",
            )
            
            # 【ダブルチェック済み】choices[0] を指定
            answer = response.choices[0].message.content
            
            with st.chat_message("assistant"):
                st.markdown(answer)
            
            # AIの回答も履歴に保存
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

# --- Tab 3: エビデンス・ツール ---
with tab3:
    st.header("Special Tools")
    st.write("ティア表作成やライフハック表示機能をここに実装予定。")
