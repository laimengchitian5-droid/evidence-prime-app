import streamlit as st
from groq import Groq
import urllib.parse

# --- 1. ページ基本設定 ---
st.set_page_config(page_title="Evidence Prime Pro", page_icon="🧬", layout="wide")

# --- 2. カスタムCSS（見た目の強化） ---
st.markdown("""
    <style>
    .main { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .stButton>button { border-radius: 20px; transition: all 0.3s; border: none; background: #4A90E2; color: white; width: 100%; }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
    .stChatFloatingInputContainer { background-color: rgba(255,255,255,0.8); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. セッション状態の初期化 ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "personality" not in st.session_state:
    st.session_state.personality = {"status": "未診断", "logic": "標準", "openness": "普通"}
if "auth" not in st.session_state:
    st.session_state.auth = False

# --- 4. 認証機能 ---
if not st.session_state.auth:
    st.title("🛡️ Evidence Prime Pro Portal")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("このアプリは17歳の開発者によって設計されています。")
        pwd = st.text_input("認証キー（合言葉）を入力:", type="password")
        if st.button("アクセスを許可する"):
            if pwd == st.secrets.get("APP_PASSWORD", "absolute-proof"):
                st.session_state.auth = True
                st.balloons()
                st.rerun()
            else:
                st.error("アクセス権限がありません。")
    st.stop()

# --- 5. Groqクライアント設定 ---
# Secretsの読み込みエラーを防ぐためのガード
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception as e:
    st.error("APIキーがSecretsに設定されていません。")
    st.stop()

# --- 6. サイドバー（設定・履歴消去） ---
with st.sidebar:
    st.title("⚙️ Control Panel")
    st.write(f"**Status:** 認証済み ✅")
    if st.button("🗑️ チャット履歴を消去"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.write("### 性格プロファイル")
    st.json(st.session_state.personality)

# --- 7. メインコンテンツ（タブ構造） ---
tab_diag, tab_chat, tab_tool = st.tabs(["🧬 高精密性格診断", "💬 エビデンス・チャット", "📊 分析ツール"])

# --- Tab 1: 性格診断 (5問) ---
with tab_diag:
    st.header("Personality Analysis")
    with st.form("diag_form"):
        st.write("直感でお答えください。AIがあなた専用の口調と回答スタイルに最適化されます。")
        q1 = st.select_slider("1. 新しい知識を得ることに興奮する？", options=["全くない", "たまに", "普通", "強い", "非常に強い"])
        q2 = st.radio("2. 意思決定の基準は？", ["論理とデータ", "感情と共感"])
        q3 = st.radio("3. 週末の過ごし方は？", ["一人で深く集中", "友人と刺激的に"])
        q4 = st.select_slider("4. 完璧主義な方だと思う？", options=["違う", "少し", "普通", "強い", "完璧主義"])
        q5 = st.radio("5. 好きな議論のタイプは？", ["抽象的な理論", "具体的な事実"])
        
        if st.form_submit_button("診断を確定し、AIを最適化する"):
            st.session_state.personality = {
                "openness": q1, "logic": q2, "energy": q3, "perfection": q4, "fact": q5, "status": "診断済み"
            }
            st.success("AIのパーソナライズが完了しました！")

# --- Tab 2: メインチャット (YouTube連携 & 連続質問) ---
with tab_chat:
    st.header("Evidence Based Chat")
    
    # メッセージ表示
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # 入力フォーム
    if prompt := st.chat_input("知りたいエビデンスを質問してください..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AIへのインストラクション
        p = st.session_state.personality
        sys_msg = f"""あなたは世界最高峰の科学コミュニケーターです。
        ユーザー性格設定: {p}
        この性格に合わせ、親しみやすい、あるいは専門的な口調を使い分けてください。
        回答の最後に必ず 'Keywords: [検索ワード]' の形式で、YouTube検索に最適な日本語キーワードを1つだけ出力してください。"""

        try:
            full_messages = [{"role": "system", "content": sys_msg}] + st.session_state.messages
            response = client.chat.completions.create(
                messages=full_messages,
                model="llama-3.3-70b-versatile",
            )
            
            # 【ダブルチェック修正箇所】[0]を追加
            full_res = response.choices[0].message.content
            
            # YouTubeキーワード抽出
            yt_q = "科学 エビデンス"
            if "Keywords:" in full_res:
                yt_q = full_res.split("Keywords:")[-1].replace("[", "").replace("]", "").strip()

            with st.chat_message("assistant"):
                st.markdown(full_res)
                # YouTubeリンクボタン
                encoded_yt = urllib.parse.quote(yt_q)
                st.markdown(f"#### 📺 関連動画でさらに深く学ぶ")
                st.info(f"「{yt_q}」の検索結果をチェックしよう！")
                st.link_button(f"YouTubeで '{yt_q}' を検索", f"https://youtube.com{encoded_yt}")

            st.session_state.messages.append({"role": "assistant", "content": full_res})

        except Exception as e:
            st.error(f"APIエラーが発生しました。SecretsのAPIキーを確認してください。: {e}")

# --- Tab 3: 分析ツール ---
with tab_tool:
    st.header("Evidence Tools")
    st.write("将来的に、ここへティア表生成エンジンを組み込みます。")
    st.progress(40, text="開発進行度: 40%")
