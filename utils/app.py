スマホ（ブラウザ）でStreamlitアプリが開けない、あるいはエラーが出る原因は、主に「モバイル特有の挙動」か「前回のコードの記述ミス（カンマの欠落など）」にあります。
特に、先ほどのエラー（SyntaxError）や、スマホの狭い画面での描画負荷が影響している可能性があります。
スマホでもサクサク動くように「モバイル最適化」を施し、かつ記述エラーを完全に排除した最新の統合版コードを作成しました。
------------------------------
## 📱 スマホで開けない時の3つのチェックポイント

   1. requirements.txt の確認: plotly や groq が入っていないと、スマホ以前にサーバーが立ち上がりません。
   2. ブラウザのキャッシュ: スマホのブラウザ（Safari/Chrome）で一度「再読み込み」を強めにかけてください。
   3. Secretsの空文字: APIキーやパスワードに「スペース」が入っていると、スマホの入力時にエラーを誘発することがあります。

------------------------------
## 🧬 Evidence Prime Pro: モバイル最適化・完全修正版

import streamlit as stimport pandas as pdimport jsonimport osfrom datetime import datetimefrom groq import Groq
# Plotlyのインポート（モバイル環境での安定性を重視）try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = Trueexcept ImportError:
    PLOTLY_AVAILABLE = False
# --- 1. 基本設定（スマホで見やすいように調整） ---
st.set_page_config(
    page_title="Evidence Prime",
    page_icon="🧬",
    layout="wide", # モバイルでは自動で1カラムになります
    initial_sidebar_state="collapsed" # スマホではサイドバーを閉じておく
)
# --- 2. セキュリティ（合言葉） ---def check_password():
    if st.session_state.get("authenticated"):
        return True
    
    st.title("🔒 認証")
    target_pwd = st.secrets.get("password", "admin")
    pwd = st.text_input("合言葉", type="password")
    if st.button("ログイン"):
        if pwd == target_pwd:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("パスワードが違います")
    st.stop()

check_password()
# --- 3. 記憶システム ---MEMORY_FILE = "user_memory_v3.json"
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return {
        "big_five": {"E": 3, "A": 3, "C": 3, "N": 3, "O": 3},
        "achievements": [{"date": datetime.now().strftime("%Y-%m-%d"), "score": 50}]
    }
if "memory" not in st.session_state:
    st.session_state.memory = load_memory()if "messages" not in st.session_state:
    st.session_state.messages = []
# --- 4. モバイル対応CSS（フォントサイズなどを調整） ---def apply_mobile_style(color):
    st.markdown(f"""
        <style>
        .stApp {{
            background: #020617;
            color: #f1f5f9;
        }}
        /* スマホのチャットバブルを少し小さく */
        div[data-testid="stChatMessage"] {{
            background: rgba(255, 255, 255, 0.03);
            border-left: 3px solid {color};
            padding: 10px;
            font-size: 14px;
        }}
        /* ボタンを押しやすく */
        .stButton>button {{
            width: 100%;
            height: 3rem;
            border-radius: 10px;
            background: {color}44;
            border: 1px solid {color};
        }}
        </style>
    """, unsafe_allow_html=True)
main_color = "#6366f1" # デフォルト
apply_mobile_style(main_color)
# --- 5. メインUI（タブ形式） ---tab_chat, tab_insight, tab_blueprint = st.tabs(["💬 チャット", "🧬 性格", "📋 計画"])
with tab_chat:
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("目標を入力..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            res_area = st.empty()
            full_res = ""
            
            # Groq API呼び出し
            client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))
            bf = st.session_state.memory["big_five"]
            sys_prompt = f"あなたはEvidence Prime Proです。性格特性(E:{bf['E']},C:{bf['C']},N:{bf['N']})に基づき回答せよ。"
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": sys_prompt}] + st.session_state.messages,
                stream=True
            )
            for chunk in completion:
                if hasattr(chunk, 'choices') and chunk.choices:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        full_res += delta.content
                        res_area.markdown(full_res + "▌")
            res_area.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
with tab_insight:
    st.subheader("🧬 性格分析")
    if PLOTLY_AVAILABLE:
        bf = st.session_state.memory["big_five"]
        fig = go.Figure(data=go.Scatterpolar(
            r=[bf['E'], bf['A'], bf['C'], bf['N'], bf['O']],
            theta=['外向', '協調', '勤勉', '繊細', '開放'], fill='toself', line_color=main_color
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            paper_bgcolor='rgba(0,0,0,0)', font_color="white", height=300 # スマホ用に高さ制限
        )
        st.plotly_chart(fig, use_container_width=True)

    # 診断用スライダー（スマホでも操作しやすいよう1〜5の整数）
    opts = [1, 2, 3, 4, 5]
    e = st.select_slider("外向性", options=opts, value=bf['E'])
    c = st.select_slider("勤勉性", options=opts, value=bf['C'])
    if st.button("性格をAIに同期"):
        st.session_state.memory["big_five"]["E"] = e
        st.session_state.memory["big_five"]["C"] = c
        st.success("同期しました")
with tab_blueprint:
    st.write("📋 今後のアクション")
    st.table(pd.DataFrame([{"計画": "AIと相談中", "期限": "未定"}]))

------------------------------
## 🚀 スマホで開くための最終アドバイス
もしこれでも開けない場合、「エラー画面のスクリーンショット」か「エラーの1行目」を教えてください。

* 「Webページが利用できません」 → サーバーが落ちている（requirements.txtのミスが多い）
* 「Something went wrong」 → コードの書き間違い（上記の修正版で治るはず）
* 

まずはこのコードをPushして、URL（xxxxx.streamlit.app）をスマホのブラウザで直接叩いてみてください。応援しています！

