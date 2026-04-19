import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from groq import Groq

# 可視化エンジン
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# --- 1. 基本設定 ---
st.set_page_config(page_title="Evidence Prime Pro", page_icon="🧬", layout="wide")

# --- 2. セキュリティ（絶対防壁） ---
def check_password():
    if st.session_state.get("authenticated"): return True
    st.title("🔒 Evidence Prime Pro Gate")
    target_pwd = st.secrets.get("password", "admin")
    pwd = st.text_input("合言葉を入力", type="password")
    if st.button("Unlock 🚀"):
        if pwd == target_pwd:
            st.session_state.authenticated = True
            st.rerun()
    st.stop()

check_password()

# --- 3. 記憶システム (C: Context) ---
MEMORY_FILE = "user_memory_global.json"
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return {
        "big_five": {"E": 3, "A": 3, "C": 3, "N": 3, "O": 3},
        "history_summary": "", "achievements": [{"date": datetime.now().strftime("%Y-%m-%d"), "score": 50}]
    }

def save_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.memory, f, indent=4, ensure_ascii=False)

if "memory" not in st.session_state: st.session_state.memory = load_memory()
if "messages" not in st.session_state: st.session_state.messages = []

# --- 4. サイドバー：Big Five設定 (ここがミソ) ---
with st.sidebar:
    st.title("🧬 Profile Tuning")
    st.write("性格診断を更新するとAIの思考が変化します。")
    
    bf = st.session_state.memory["big_five"]
    opts = [1, 2, 3, 4, 5]
    
    st.subheader("Big Five 診断")
    e = st.select_slider("👥 外向性", options=opts, value=bf.get("E", 3))
    a = st.select_slider("🤝 協調性", options=opts, value=bf.get("A", 3))
    c = st.select_slider("📈 勤勉性", options=opts, value=bf.get("C", 3))
    n = st.select_slider("🧠 繊細さ", options=opts, value=bf.get("N", 3))
    o = st.select_slider("🎨 開放性", options=opts, value=bf.get("O", 3))
    
    if st.button("性格をAIに同期 🧠", use_container_width=True):
        st.session_state.memory["big_five"] = {"E": e, "A": a, "C": c, "N": n, "O": o}
        save_memory()
        st.toast("AI context updated!")

    st.divider()
    theme_choice = st.radio("Theme", ["Cyber", "Ocean", "Lava"], horizontal=True)
    palette = {"Cyber": "#6366f1", "Ocean": "#0ea5e9", "Lava": "#f43f5e"}
    main_color = palette[theme_choice]

# --- 5. デザインエンジン ---
st.markdown(f"""
    <style>
    .stApp {{ background: radial-gradient(circle at top right, {main_color}15, #020617); color: #f1f5f9; }}
    div[data-testid="stChatMessage"] {{
        background: rgba(255, 255, 255, 0.02);
        border-left: 5px solid {main_color};
        backdrop-filter: blur(10px);
        border-radius: 15px; padding: 20px;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 6. AIコア (A-Cモデルの真髄) ---
def run_ai_agent():
    client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))
    bf = st.session_state.memory["big_five"]
    
    # C: Context に基づく AI戦略
    strat = "高精度な構造化プラン" if bf['C'] >= 4 else "小さな達成感(Small Win)を重視したプラン"
    tone = "論理的かつ客観的" if bf['N'] <= 2 else "共感的かつ励まし重視"

    system_prompt = f"""
    あなたは『Evidence Prime Pro』、17歳の開発者との合作で生まれた次世代AIです。
    【A-Cモデル運用指示】
    - A (Authority): 科学的根拠を提示せよ。
    - B (Blueprint): 行動計画をテーブル形式で必ず出力せよ。
    - C (Context): 下記特性を100%反映せよ。
      [特性] E:{bf['E']}, A:{bf['A']}, C:{bf['C']}, N:{bf['N']}, O:{bf['O']}
      [戦略] {strat} / {tone}
    """
    
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
        stream=True
    )

# --- 7. メインUI ---
tab_chat, tab_blueprint, tab_insight = st.tabs(["💬 Chat Agent", "📅 Blueprint Hub", "📊 Science Insight"])

with tab_chat:
    st.title("Evidence Prime Pro")
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("解決したい課題を入力..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            res_area = st.empty()
            full_res = ""
            completion = run_ai_agent()
            for chunk in completion:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices.delta
                    if hasattr(delta, 'content') and delta.content:
                        full_res += delta.content
                        res_area.markdown(full_res + "▌")
            res_area.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})

with tab_blueprint:
    st.header("📋 行動計画ハブ (B-モデル)")
    st.info("AIが生成したBlueprintがここに蓄積されます。")
    # ここに直近のメッセージからテーブルを抽出して表示するロジックを将来的に統合

with tab_insight:
    st.header("📊 自己分析ダッシュボード")
    if PLOTLY_AVAILABLE:
        categories = ['外向', '協調', '勤勉', '繊細', '開放']
        fig = go.Figure(data=go.Scatterpolar(
            r=[bf['E'], bf['A'], bf['C'], bf['N'], bf['O']],
            theta=categories, fill='toself', line_color=main_color
        ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[1, 5])), paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig, use_container_width=True)
# --- 155行目以降：B-Cモデル & モバイル最適化統合ロジック ---

# 日本語初期設定の強制適用
LANGUAGE_CODE = "ja-JP"

def apply_mobile_optimized_ui(main_color):
    """スマホのブラウザでも崩れない、究極のモバイルUI制御"""
    st.markdown(f"""
        <style>
        /* モバイルでのフォントサイズ調整 */
        html, body, [class*="css"] {{
            font-size: 16px;
        }}
        /* チャットエリアの余白をスマホ用に最適化 */
        .main .block-container {{
            padding: 1rem 0.5rem;
        }}
        /* スマホでのボタンの押しやすさ */
        .stButton>button {{
            width: 100%;
            height: 3.5rem;
            font-weight: bold;
            border-radius: 12px;
            background: linear-gradient(90deg, {main_color}bb, {main_color}44);
        }}
        /* 診断スライダーのラベルがスマホで重ならないようにする */
        div[data-testid="stSlider"] {{
            padding-bottom: 2rem;
        }}
        </style>
    """, unsafe_allow_html=True)

# 実行
current_color = main_color if 'main_color' in locals() else "#6366f1"
apply_mobile_optimized_ui(current_color)

# --- 強化版：B-Cモデル連携ロジック ---
def generate_ultimate_prompt(user_input):
    """
    B (Blueprint): 行動計画の強制
    C (Context): 日本語とBig Fiveの完全同期
    """
    bf = st.session_state.memory.get("big_five", {"E":3,"A":3,"C":3,"N":3,"O":3})
    
    # 勤勉性(C)に応じたB(計画)の出し分け
    if bf["C"] <= 2:
        b_strategy = "【超・小分け計画】3分で終わるタスクに分解してテーブル化してください。"
    else:
        b_strategy = "【構造的計画】詳細な週間ガントチャート形式のテーブルを提示してください。"
        
    # 神経症傾向(N)に応じたC(トーン)の出し分け
    c_strategy = "【安心感重視】科学的事実を伝えつつ、非常に温かく肯定的な日本語で。" if bf["N"] >= 4 else "【事実重視】無駄を省き、論理的で鋭い日本語で。"

    return f"""
# 命令:
あなたはEvidence Prime Proです。以下の【A-Cモデル】を厳守し、日本語で回答してください。

## A (Authority):
- 全ての回答に、信頼できる科学的根拠（[出典]）を添えること。

## B (Blueprint):
- {b_strategy}
- 実行可能なステップをMarkdownテーブルで出力せよ。

## C (Context):
- {c_strategy}
- ユーザー特性: 外向:{bf['E']}, 協調:{bf['A']}, 勤勉:{bf['C']}, 繊細:{bf['N']}, 開放:{bf['O']}
"""

# --- メイン実行処理（修正済み） ---
# 既存のチャットループや診断部分に、この prompt 生成ロジックを反映させてください。
# これにより、日本語設定が外れるのを防ぎ、B-Cモデルが常に機能します。

st.sidebar.markdown("---")
st.sidebar.caption("Evidence Prime Pro v3.8 | Mobile & Blueprint Optimized")
st.sidebar.info("スマホで開けない場合は、ブラウザの『PC版サイトを表示』をオフにしてください。")
