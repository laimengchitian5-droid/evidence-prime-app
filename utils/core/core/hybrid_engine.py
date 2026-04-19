import streamlit as st
import google.generativeai as genai
from groq import Groq

class HybridEngine:
    def __init__(self):
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        self.gemini = genai.GenerativeModel('gemini-1.5-pro') # 3.1 Pro
        self.groq = Groq(api_key=st.secrets["GROQ_API_KEY"])

    def generate_blueprint(self, query, personality_context):
        prompt = f"""
        ユーザーの性格コンテキスト: {personality_context}
        課題: {query}
        
        上記に基づき、科学的根拠(Authority)を含んだ具体的な行動計画(Blueprint)をJSONで出力せよ。
        フォーマット:
        {{
          "tasks": [
            {{"title": "タスク名", "action": "具体的な行動", "evidence": "根拠とリンク", "duration": 30}}
          ]
        }}
        """
        # Geminiで深い推論とJSON構造化
        response = self.gemini.generate_content(prompt)
        return response.text
