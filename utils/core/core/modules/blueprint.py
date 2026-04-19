import streamlit as st
import json
from icalendar import Calendar, Event
from datetime import datetime, timedelta

def render_blueprint(json_raw):
    try:
        # JSONの抽出（マークダウンの除去など）
        json_str = json_raw.replace('```json', '').replace('```', '').strip()
        data = json.loads(json_str)
        
        st.subheader("🚀 実行プラン")
        for i, task in enumerate(data["tasks"]):
            with st.container():
                st.markdown(f"""
                <div class="blueprint-card">
                    <h4>{task['title']}</h4>
                    <p>{task['action']}</p>
                    <small>💡 根拠: {task['evidence']}</small>
                </div>
                """, unsafe_allow_html=True)
                
                # カレンダー生成
                if st.button(f"カレンダーに追加", key=f"btn_{i}"):
                    ics = create_ics(task['title'], task['action'])
                    st.download_button("ファイルをダウンロード", ics, file_name=f"task_{i}.ics")
    except Exception as e:
        st.error("プランの生成に失敗しました。もう一度お試しください。")

def create_ics(title, description):
    cal = Calendar()
    event = Event()
    event.add('summary', title)
    event.add('description', description)
    event.add('dtstart', datetime.now() + timedelta(days=1))
    event.add('dtend', datetime.now() + timedelta(days=1, hours=1))
    cal.add_component(event)
    return cal.to_ical()
