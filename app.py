import streamlit as st
from groq import Groq
import urllib.parse
import json

# --- 1. ページ基本設定 ---
st.set_page_config(page_title="Evidence Prime Pro", page_icon="🧬", layout="wide")

# --- 2. セッション状態の初期化 ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "personality" not in st.session_state:
    st.session_state.personality = {"status": "未診断"}
if "auth" not in st.session_state:
    st.session_state.auth = False

# --- 3. テーマ・見た目の設定 (サイドバー) ---
with st.sidebar:
    st.title("🎨 UI Customizer")
    main_color = st.color_picker("メインカラーを選択", "#4A90E2")
    bg_type = st.radio("背景スタイル", ["グラデーション", "シンプル", "ダーク"])
    
    # 背景スタイルの定義
    if bg_type == "グラデーション":
        bg_style = f"linear-gradient(135deg, #f5f7fa 0%, {main_color}44 100%)"
        text_color = "#31333F"
    elif bg_type == "ダーク":
        bg_style = "#1E1E1E"
        text_color = "#FFFFFF"
    else:
        bg_style = "#FFFFFF"
        text_color = "#31333F"

# --- 4. カスタムCSSの注入 ---
st.markdown(f"""
    <style>
    .stApp {{
        background: {bg_style};
        color: {text_color};
    }}
    .stButton>button {{
        border-radius: 12px;
        background-color: {main_color};
        color: white;
        border: none;
        height: 3em;
        font-weight: bold;
    }}
    .stTextInput>div>div>input {{
        border-radius: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. 認証機能 ---
if not st.session_state.auth:
    st.title("🛡️ Evidence Prime Pro Portal")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.write("### Welcome to the Future of Evidence")
        pwd = st.text_input("認証キーを入力:", type="password")
        if st.button("アクセスを許可する"):
            if pwd == st.secrets.get("APP_PASSWORD", "absolute-proof"):
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("アクセス権限がありません。")
    st.stop()

# --- 6. Groqクライアント設定 ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 7. サイドバー（管理メニュー） ---
with st.sidebar:
    st.divider()
    if st.button("🗑️ チャット履歴を消去"):
        st.session_state.messages = []
        st.rerun()
    
    # 診断結果の保存（ダウンロード機能）
    if st.session_state.personality.get("status") == "診断済み":
        st.write("### 診断結果を保存")
        p_data = json.dumps(st.session_state.personality, indent=2, ensure_ascii=False)
        st.download_button(
            label="📄 診断結果をダウンロード",
            data=p_data,
            file_name="my_personality.json",
            mime="application/json"
        )

# --- 8. メインコンテンツ ---
tab_diag, tab_chat, tab_tool = st.tabs(["🧬 高精密性格診断", "💬 エビデンス・チャット", "📊 分析ツール"])

# --- Tab 1: 性格診断 ---
with tab_diag:
    st.header("Personality Analysis")
    with st.form("diag_form"):
        q1 = st.select_slider("1. 知的好奇心の強さは？", options=["低い", "普通", "高い", "圧倒的"])
        q2 = st.radio("2. 判断の軸は？", ["データと論理", "共感と直感"])
        q3 = st.radio("3. 集中できる環境は？", ["静かな独りきりの空間", "適度に賑やかな場所"])
        q4 = st.select_slider("4. 行動力のタイプ", options=["慎重派", "バランス", "即断即決"])
        q5 = st.radio("5. 理想の回答スタイルは？", ["結論からズバッと", "丁寧にプロセスを解説"])
        
        if st.form_submit_button("診断結果をAIに記憶させる"):
            st.session_state.personality = {
                "curiosity": q1, "logic": q2, "focus": q3, "action": q4, "style": q5, "status": "診断済み"
            }
            st.success("記憶に成功しました！チャットであなた専用の回答が得られます。")

# --- Tab 2: メインチャット ---
with tab_chat:
    st.header("Evidence Based Chat")
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("知りたいエビデンスを質問してください..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        p = st.session_state.personality
        sys_msg = f"あなたは科学の専門家です。ユーザーの性格({p})に合わせ、最適化された口調で回答してください。回答の最後に必ず 'Keywords: [検索ワード]' を1つ付けてください。"

        try:
            response = client.chat.completions.create(
                messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages,
                model="llama-3.3-70b-versatile",
            )
            
            full_res = response.choices[0].message.content
            
            # YouTube検索リンク生成
            yt_q = full_res.split("Keywords:")[-1].strip() if "Keywords:" in full_res else "科学"
            encoded_yt = urllib.parse.quote(yt_q)

            with st.chat_message("assistant"):
                st.markdown(full_res)
                st.link_button(f"📺 YouTubeで '{yt_q}' を深掘り", f"https://youtube.com{encoded_yt}")

            st.session_state.messages.append({"role": "assistant", "content": full_res})

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

# --- Tab 3: 分析ツール ---
with tab_tool:
    st.header("Special Tools")
    st.write("あなたの性格に基づいた、今日から使えるライフハック：")
    if st.session_state.personality.get("status") == "診断済み":
        if st.session_state.personality["logic"] == "データと論理":
            st.success("🎯 **ロジカル・ライフハック**: ポモドーロ・テクニックを25分-5分で回し、データを記録しましょう。")
        else:
            st.success("✨ **共感型・ライフハック**: 好きな音楽をBGMに、感情の波に乗って作業を進めましょう。")
    else:
        st.warning("性格診断を完了すると、ここに個別のアドバイスが表示されます。")
