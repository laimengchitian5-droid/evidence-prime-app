import streamlit as st

def apply_glassmorphism():
    st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    .stApp {
        color: #f8fafc;
    }
    /* グラスモーフィズム・カード */
    div.stButton > button, div.stDownloadButton > button {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        color: white;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid #38bdf8;
    }
    /* カスタムコンテナ */
    .blueprint-card {
        background: rgba(255, 255, 255, 0.03);
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #38bdf8;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
