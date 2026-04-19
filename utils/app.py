import streamlit as st
import json
import os
from datetime import datetime
from groq import Groq

# ==========================================
# MODULE 1: SECURITY & AUTHENTICATION
# ==========================================
def check_password():
    """absolute-proof: 認証が通るまで他のコードを実行させない"""
    if st.session_state.get("authenticated"):
        return True
    
    st.title("🧬 Evidence Prime Pro")
    st.subheader("システムアクセス認証")
    
    # Secretsから安全に取得（設定漏れ時は'admin'を予備に）
    target_pwd = st.secrets.get("password", "admin")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        pwd = st.text_input("合言葉を入力してください", type="password")
    with col2:
        st.write(" ") # 余白調整
        login_btn = st.button("ログイン 🚀", use_container_width=True)

    if login_btn:
        if pwd == target_pwd:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("合言葉が正しくありません。")
    
    st.info("※このアプリは高度なプライバシー保護のため認証を必須としています。")
    st.stop()

# ==========================================
# MODULE 2: UI & MOBILE OPTIMIZATION
# ==========================================
def apply_core_ui():
    """PC/スマホ両対応のレスポンシブ・グラスモーフィズムCSS"""
    main_color = "#6366f1" # 基本ブランドカラー
    
    st.markdown(f"""
        <style>
        /* ベース背景とフォント */
        .stApp {{
            background: #020617;
            color: #f1f5f9;
            font-family: "Hiragino Kaku Gothic ProN", sans-serif;
        }}
        /* スマホ・PC両対応のチャットデザイン */
        div[data-testid="stChatMessage"] {{
            background: rgba(255, 255, 255, 0.03);
            border-left: 3px solid {main_color};
            border-radius: 12px;
            backdrop-filter: blur(10px);
            padding: 1rem;
            margin-bottom: 0.8rem;
        }}
        /* スマホで押しやすい巨大ボタン */
        .stButton>button {{
            width: 100%;
            height: 3.5rem;
            border-radius: 10px;
            background: {main_color}44;
            border: 1px solid {main_color};
            font-weight: bold;
            transition: 0.3s;
        }}
        /* 入力エリアのモバイル最適化 */
        .stChatInputContainer {{
            padding-bottom: 2rem;
        }}
        </style>
    """, unsafe_allow_html=True)
    return main_color

# ==========================================
# MODULE 3: PERSISTENT MEMORY (JSON Safe Storage)
# ==========================================
MEMORY_FILE = "user_memory.json"

def init_memory():
    """初期データの定義と読み込み"""
    if "memory" not in st.session_state:
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    st.session_state.memory = json.load(f)
            except:
                st.session_state.memory = {"big_five": {}}
        else:
            st.session_state.memory = {
                "user_profile": {"name": "User", "created_at": str(datetime.now())},
                "big_five": {"E": 3, "A": 3, "C": 3, "N": 3, "O": 3},
                "last_update": ""
            }

def save_memory():
    """メモリを物理ファイルに安全に書き出し"""
    st.session_state.memory["last_update"] = str(datetime.now())
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.memory, f, indent=4, ensure_ascii=False)

# ==========================================
# MAIN EXECUTION
# ==========================================
def main():
    # 1. 認証 (Security First)
    check_password()
    
    # 2. UI適用 (UX First)
    brand_color = apply_core_ui()
    
    # 3. メモリ同期 (Data First)
    init_memory()

    # --- ヘッダー領域 ---
    st.title("🧬 Evidence Prime Pro")
    st.caption("安定・安全・高性能基盤モデル v4.1")

    # --- タブ構成 (モジュール化の土台) ---
    tab_chat, tab_settings = st.tabs(["💬 対話エンジン", "⚙️ システム設定"])

    with tab_chat:
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # 過去ログの表示
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        # チャット入力
        if prompt := st.chat_input("課題を入力してください..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # AI応答ロジック (Groq連携の口だけ用意)
            with st.chat_message("assistant"):
                res_box = st.empty()
                res_box.info("AI基盤準備完了。APIキーを設定すると思考を開始します。")

    with tab_settings:
        st.subheader("⚙️ 基盤データ管理")
        st.write("現在のメモリ状態（長期記憶）")
        st.json(st.session_state.memory)
        
        if st.button("メモリをリセット"):
            if os.path.exists(MEMORY_FILE):
                os.remove(MEMORY_FILE)
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()
# ==========================================
# MODULE 4: BIG FIVE TUNING & GROQ ENGINE (v4.2)
# ==========================================

def run_big_five_logic():
    """
    サイドバーで性格診断を管理し、AIの思考回路を書き換える
    """
    with st.sidebar:
        st.markdown("---")
        st.subheader("🧬 性格プロファイル (Big Five)")
        st.caption("AIの回答をあなたの性格に最適化します。")
        
        # メモリから現在の値を取得（初期値3）
        bf = st.session_state.memory.get("big_five", {"E":3, "A":3, "C":3, "N":3, "O":3})
        
        # 診断スライダー (短縮版尺度に基づいた5因子)
        opts = [1, 2, 3, 4, 5]
        new_e = st.select_slider("👥 外向性 (静か ↔ 社交的)", options=opts, value=bf.get("E", 3))
        new_a = st.select_slider("🤝 協調性 (合理的 ↔ 共感的)", options=opts, value=bf.get("A", 3))
        new_c = st.select_slider("📈 勤勉性 (即興的 ↔ 計画的)", options=opts, value=bf.get("C", 3))
        new_n = st.select_slider("🧠 繊細さ (冷静 ↔ 繊細)", options=opts, value=bf.get("N", 3))
        new_o = st.select_slider("🎨 開放性 (保守的 ↔ 好奇心)", options=opts, value=bf.get("O", 3))
        
        if st.button("AIの思考回路に同期 🧠", use_container_width=True):
            st.session_state.memory["big_five"] = {
                "E": new_e, "A": new_a, "C": new_c, "N": new_n, "O": new_o
            }
            save_memory() # 基盤モジュールの保存関数
            st.toast("AIがあなたの性格に適応しました！", icon="✅")

    return st.session_state.memory["big_five"]

def get_optimized_prompt(bf):
    """
    Groqの能力を最大化する「性格適応型」システムプロンプト生成
    """
    # 因子のスコアに基づいたAIの戦略分岐（B-Cモデルの核）
    strategy_c = "【超・小分け計画】目標を3分で終わる極小タスクに分解して提示せよ。" if bf['C'] <= 2 else "【構造的計画】詳細なガントチャート形式の計画を提示せよ。"
    strategy_n = "【心理的安全性】徹底して寄り添い、安心感を与える日本語を使え。" if bf['N'] >= 4 else "【論理的合理性】事実に基づき、無駄を省いたシャープな助言を行え。"
    strategy_o = "【革新的提案】既存の枠を超えた斬新なアイデアを1つ含めよ。" if bf['O'] >= 4 else "【堅実な裏付け】伝統的で実証済みの確実な手法を推奨せよ。"

    return f"""
# 命令:
あなたは世界最高のAIパートナー『Evidence Prime Pro』です。
17歳の天才開発者が提唱する【A-Cモデル】に基づき、以下の指示を完遂してください。

## A (Authority):
- 全ての回答に、最新の科学的エビデンス（出典・検証リンク）を付与せよ。

## B (Blueprint):
- 提案は必ず実行可能な『Markdownテーブル形式のアクションプラン』にまとめよ。
- 戦略: {strategy_c}

## C (Context):
- ユーザーの性格特性（外向:{bf['E']}, 協調:{bf['A']}, 勤勉:{bf['C']}, 繊細:{bf['N']}, 開放:{bf['O']}）を反映せよ。
- 接し方の方針: {strategy_n} / {strategy_o}
- 言語: 常に温かくも知的な『日本語』で回答せよ。
"""

def execute_groq_chat(user_input):
    """
    Groq APIを叩き、ストリーミングで回答を生成する
    """
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        st.error("APIキーが未設定です。")
        return

    client = Groq(api_key=api_key)
    bf = run_big_five_logic()
    system_prompt = get_optimized_prompt(bf)

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
            stream=True
        )
        
        full_res = ""
        res_area = st.empty()
        
        for chunk in completion:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    full_res += delta.content
                    res_area.markdown(full_res + "▌")
        
        res_area.markdown(full_res)
        st.session_state.messages.append({"role": "assistant", "content": full_res})
        
    except Exception as e:
        st.error(f"Groq API Error: {e}")

# --- 基盤の main() 内で以下のように呼び出す ---
# if prompt := st.chat_input(...):
#     execute_groq_chat(prompt)
# ==========================================
# MODULE 5: VISUAL INSIGHT ENGINE (修正版)
# ==========================================

def render_big_five_radar():
    """
    Big Fiveデータを可視化（インポートエラーと変数未定義を完全に防ぐ）
    """
    # 内部での再チェック（PLOTLY_AVAILABLEが定義されていない場合への備え）
    try:
        import plotly.graph_objects as go
    except ImportError:
        st.warning("可視化エンジン(Plotly)がインストールされていません。")
        return

    st.subheader("📊 パーソナリティ・構造分析")
    
    # メモリとカラーの安全な取得
    bf = st.session_state.memory.get("big_five", {"E":3, "A":3, "C":3, "N":3, "O":3})
    current_color = "#6366f1" # デフォルト色（main_color未定義対策）

    # 頂点を「開放性」にし、画像通り時計回りに配置
    categories = ['開放性', '神経症傾向', '協調性', '外向性', '勤勉性']
    values = [
        bf.get('O', 3), bf.get('N', 3), bf.get('A', 3), 
        bf.get('E', 3), bf.get('C', 3)
    ]
    
    # グラフ描画
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]], # 閉じた図形にする
        theta=categories + [categories[0]],
        fill='toself',
        line=dict(color=current_color, width=3),
        fillcolor="rgba(99, 102, 241, 0.3)", # 安定した色指定
        marker=dict(size=10, color=current_color)
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5], # 1-5スケールで完全固定
                tickvals=[1, 2, 3, 4, 5],
                gridcolor="rgba(255, 255, 255, 0.1)",
                tickfont=dict(color="#94a3b8")
            ),
            angularaxis=dict(
                rotation=90, # 「開放性」を真上に配置
                direction="clockwise", # 時計回り
                gridcolor="rgba(255, 255, 255, 0.1)",
                tickfont=dict(size=14, color="#f1f5f9")
            ),
            bgcolor="rgba(0,0,0,0)"
        ),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=400,
        margin=dict(l=40, r=40, t=40, b=40)
    )

    # グラフ表示
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # --- 数値メトリクス ---
    st.markdown("---")
    m_cols = st.columns(5)
    labels_short = ["O", "N", "A", "E", "C"]
    for i, (lbl, val) in enumerate(zip(labels_short, values)):
        m_cols[i].metric(lbl, val)

# モジュールの呼び出し（安全な実行）
if st.session_state.get("authenticated"):
    render_big_five_radar()
