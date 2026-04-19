import plotly.graph_objects as go
import streamlit as st

class PersonalityManager:
    def __init__(self):
        # デフォルトスコア
        if 'scores' not in st.session_state:
            st.session_state.scores = {"開放性": 50, "誠実性": 50, "外向性": 50, "協調性": 50, "神経症的傾向": 50}

    def render_radar_chart(self):
        categories = list(st.session_state.scores.keys())
        values = list(st.session_state.scores.values())
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            line_color='#38bdf8'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white")
        )
        return fig

    def get_context_string(self):
        s = st.session_state.scores
        return f"開放性:{s['開放性']}, 誠実性:{s['誠実性']}, 外向性:{s['外向性']}, 協調性:{s['協調性']}, 神経症:{s['神経症的傾向']}"
