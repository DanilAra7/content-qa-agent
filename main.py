import streamlit as st
import os
from dotenv import load_dotenv
from utils.google_api import GoogleClient
from utils.ai_logic import AIAgent
from datetime import datetime

EXPIRY_DATE = datetime(2026, 4, 10) 

if datetime.now() > EXPIRY_DATE:
    st.error("⌛ Термін дії демо-доступу вичерпано. Зверніться до розробника.")
    st.stop()

load_dotenv()

GEMINI_KEY = st.secrets["GEMINI_API_KEY"]

st.set_page_config(page_title="AI QA Agent", layout="wide")

st.title("AI-агент для перевірки статей")

tz_url = st.text_input("Посилання на ТЗ (Google Sheet)")
doc_url = st.text_input("Посилання на статтю (Google Doc)")

if st.button("Перевірити"):
    if not tz_url or not doc_url:
        st.error("Вставте обидва посилання")
    else:
        with st.spinner("Працюю..."):
            try:
                google = GoogleClient()
                agent = AIAgent(GEMINI_KEY)
                
                tz_data = google.read_sheet(tz_url)
                article_text = google.read_doc(doc_url)
                
                reqs = agent.parse_requirements(tz_data)
                
                results = agent.check_article(article_text, reqs)
                
                st.success("Аналіз завершено!")
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Слів", results['word_count'], f"{reqs['min_words']}-{reqs['max_words']}")
                c2.metric("Ключів знайдено", len(results['found_keys']))
                c3.metric("Ключів пропущено", len(results['missing_keys']), delta_color="inverse")
                
                if results['missing_keys']:
                    st.warning(f"⚠️ Пропущені ключі: {', '.join(results['missing_keys'])}")
                
                st.subheader("Вердикт AI:")
                st.write(results['verdict'])
                
            except Exception as e:
                st.error(f"Помилка: {e}. Перевірте доступ Сервісного акаунта до файлів!")