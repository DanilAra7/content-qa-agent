from google import genai
import json

import re

def count_words(text):
    text = re.sub(r'https?://\S+', '', text)
    words = re.findall(r'\b\w+\b', text)
    
    return len(words)

class AIAgent:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-flash-latest"

    def parse_requirements(self, tz_data):
        """
        Гнучко витягує вимоги з ТЗ, незалежно від назв колонок.
        """
        tz_text = "\n".join([", ".join(row) for row in tz_data])
        
        prompt = f"""
        Analyze this Technical Task (TZ) for a copywriter and extract:
        1. Min and Max word count (find numbers).
        2. List of keywords for mandatory direct entry.
        
        TZ Data:
        {tz_text}
        
        Return ONLY a JSON object like this:
        {{"min_words": 1000, "max_words": 1400, "keywords": ["word1", "word2"]}}
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                }
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Помилка парсингу ТЗ: {e}")
            return {"min_words": 0, "max_words": 0, "keywords": []}

    def check_article(self, text, reqs):
        """
        Проводить технічну перевірку та формує фінальний вердикт українською мовою.
        """
        # підрахунок слів 
        word_count = count_words(text)
        
        # пошук ключів
        found_keys = []
        missing_keys = []
        for key in reqs['keywords']:
            if key.lower() in text.lower():
                found_keys.append(key)
            else:
                missing_keys.append(key)
        
        prompt = f"""
        Ти — професійний редактор. Твоє завдання — перевірити статтю на відповідність ТЗ.
        
        Вимоги ТЗ: {reqs}
        Фактична кількість слів у тексті: {word_count}
        Знайдені ключі: {found_keys}
        Пропущені ключі: {missing_keys}
        
        Ось ПОВНИЙ текст статті:
        ---
        {text}
        ---
        
        Напиши короткий вердикт українською мовою. 
        1. Чи відповідає обсяг нормі?
        2. Чи всі ключі використані? (Якщо ні — перелічи їх).
        3. Чи є логічне завершення (висновок, FAQ)?
        4. Чи можна приймати статтю?
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            verdict_text = response.text
        except:
            verdict_text = "Не вдалося згенерувати вердикт через обмеження API."

        return {
            "word_count": word_count,
            "found_keys": found_keys,
            "missing_keys": missing_keys,
            "verdict": verdict_text
        }