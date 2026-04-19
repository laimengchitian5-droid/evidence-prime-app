import streamlit as st
import json
import os

# --- 1. SETTINGS & THEMES ---
st.set_page_config(page_title="Evidence Prime Pro", layout="wide")

def apply_custom_style(main_color):
    """グラスモーフィズムと動的カラーテーマを適用する完全版CSS"""
    st.markdown(f"""
        <style>
        /* 背景グラデーション */
        .stApp {{
            background: linear-gradient(135deg, {main_color}33, #0e1117, #000000);
            background-attachment: fixed;
        }}
        
        /* ガラス状のカードデザイン */
        div[data-testid="stChatMessage"] {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            border: 1px solid {main_color}44;
            backdrop-filter: blur(10px);
            margin-bottom: 10px;
        }}
        
        /* サイドバーのカスタマイズ */
        .css-1d391kg, [data-testid="stSidebar"] {{
            background-color: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(20px);
            border-right: 1px solid {main_color}33;
        }}
        
        /* ボタンとアクセント */
        .stButton>button {{
            border-radius: 20px;
            border: 1px solid {main_color};
            background-color: transparent;
            color: {main_color};
            transition: 0.3s;
        }}
        .stButton>button:hover {{
            background-color: {main_color};
            color: white;
            box-shadow: 0 0 15px {main_color};
        }}
        </style>
    """, unsafe_allow_html=True)

# --- 2. PERSONALITY LOGIC (Big Five) ---
def big_five_ui():
    st.markdown(f"### 🧬 Big Five 性格診断モード")
    st.caption("直感的に、今の自分に近い位置をタップしてください。")
    
    col1, col2 = st.columns(2)
    with col1:
        e = st.select_slider("👥 外向性 (社交的 ↔ 内省的)", options=[1,2,3,4,5], value=3)
        a = st.select_slider("🤝 協調性 (献身的 ↔ 合理的)", options=[1,2,3,4,5], value=3)
        c = st.select_slider("📈 勤勉性 (計画的 ↔ 柔軟・即興)", options=[1,2,3,4,5], value=3)
    with col2:
        n = st.select_slider("🧠 神経症傾向 (繊細 ↔ 楽観・動じない)", options=[1,2,3,4,5], value=3)
        o = st.select_slider("🎨 開放性 (好奇心旺盛 ↔ 堅実・伝統)", options=[1,2,3,4,5], value=3)

    if st.button("プロファイルを同期", use_container_width=True):
        st.session_state.user_memory["big_five"] = {
            "extraversion": e, "agreeableness": a, "conscientiousness": c,
            "neuroticism": n, "openness": o
        }
        st.success("AIがあなたの深層性格を学習しました。")

# --- 3. THE STRONGEST SYSTEM PROMPT ---
def get_system_prompt():
    bf = st.session_state.user_memory.get("big_five", {"extraversion":3,"agreeableness":3,"conscientiousness":3,"neuroticism":3,"openness":3})
    
    # 性格に応じたアドバイス戦略の動的生成
    strategy = ""
    if bf["conscientiousness"] <= 2:
        strategy += "- ユーザーは即興を好むため、細かすぎる計画より『まず5分だけやる』スモールステップを提示せよ。"
    else:
        strategy += "- ユーザーは計画的であるため、具体的な時間軸とチェックリストを提示せよ。"
        
    if bf["neuroticism"] >= 4:
        strategy += "- ユーザーは繊細であるため、否定的な言葉を避け、エビデンスに基づいた安心感を強調せよ。"
    
    prompt = f"""
あなたは世界最高のパーソナルAI『Evidence Prime Pro』です。
17歳の天才開発者によって設計された「A-Cモデル」を搭載しています。

【ユーザーの性格特性 (Big Five スコア 1-5)】
- 外向性: {bf['extraversion']} | 協調性: {bf['agreeableness']} | 勤勉性: {bf['conscientiousness']} | 神経症傾向: {bf['neuroticism']} | 開放性: {bf['openness']}

【運用ガイドライン】
1. A (Authority): 常に最新の科学的知見を引用し、[ソース名]を明記せよ。
2. B (Blueprint): 性格特性に最適化された行動計画を出力せよ。
   - 戦略: {strategy}
3. C (Context): ユーザーの性格、過去の対話を記憶し、親友であり有能なメンターとして振る舞え。
    """
    return prompt

# --- 4. MAIN APP STRUCTURE ---
def main():
    # メモリの初期化
    if "user_memory" not in st.session_state:
        st.session_state.user_memory = {}

    # サイドバー：デザイン設定
    st.sidebar.title("🛠️ Control Panel")
    
    theme_choice = st.sidebar.radio("Quick Theme", ["Custom", "Ocean Blue", "Forest Green", "Lava Red"])
    presets = {"Ocean Blue": "#0077ff", "Forest Green": "#2ecc71", "Lava Red": "#e74c3c"}
    
    if theme_choice == "Custom":
        main_color = st.sidebar.color_picker("Brand Color", "#4A90E2")
    else:
        main_color = presets[theme_choice]
    
    apply_custom_style(main_color)

    # メインエリア：タブ構成
    tab_chat, tab_persona, tab_log = st.tabs(["💬 AI Agent", "🧬 Personality", "📊 Memory Bank"])

    with tab_persona:
        big_five_ui()

    with tab_chat:
        st.title("Evidence Prime Pro")
        # チャットUIの実装（Groq APIとの連携部分は既存コードを流用）
        st.info(f"現在のAI戦略: {theme_choice}モード | 性格適応済み")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        if prompt := st.chat_input("何について科学的に解決しますか？"):
            # ここにGroqへのAPIリクエストを記述（System Promptにget_system_prompt()を使用）
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            
            # AIレスポンス生成（ダミー）
            with st.chat_message("assistant"):
                st.write("ここに最強プロンプトを反映したLlama 3.3の回答が表示されます。")

if __name__ == "__main__":
    main()
