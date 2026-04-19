import streamlit as st
from utils.styles import apply_glassmorphism
from core.personality import PersonalityManager
from core.hybrid_engine import HybridEngine
from modules.blueprint import render_blueprint

# セットアップ
st.set_page_config(page_title="Evidence Prime Pro", layout="wide")
apply_glassmorphism()
pm = PersonalityManager()
engine = HybridEngine()

# --- サイドバー：性格診断 ---
with st.sidebar:
    st.title("🧬 Personality")
    for trait in st.session_state.scores.keys():
        st.session_state.scores[trait] = st.slider(trait, 0, 100, st.session_state.scores[trait])
    st.plotly_chart(pm.render_radar_chart(), use_container_width=True)

# --- メインコンテンツ ---
st.title("Evidence Prime Pro")
query = st.text_input("今、解決したい課題や目標は何ですか？", placeholder="例：朝型人間に変わりたい、集中力を上げたい")

if query:
    with st.spinner("AIがエビデンスを解析し、プランを構築中..."):
        context = pm.get_context_string()
        blueprint_json = engine.generate_blueprint(query, context)
        render_blueprint(blueprint_json)

st.divider()
st.caption("Powered by Gemini 3.1 Pro & Groq (Llama 3.3)")
