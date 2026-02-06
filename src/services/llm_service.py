import os
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# מוצא את הנתיב האמיתי של תיקיית הפרויקט (שתי רמות מעל הקובץ הנוכחי)
base_dir = Path(__file__).resolve().parent.parent.parent
env_path = base_dir / '.env'

# טוען את הקובץ הספציפי
load_dotenv(dotenv_path=env_path)

class LLMService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        
        # הדפסת עזר לבדיקה (תמחקי אותה אחרי שזה עובד)
        if api_key:
            print(f"DEBUG: Key loaded starting with: {api_key[:10]}...")
        else:
            print("DEBUG: No API key found at " + str(env_path))
            
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"

    def get_album_suggestions(self, enriched_data, user_query):
        """
        שולח את הנתונים המועשרים ל-LLM ומקבל הצעות לארגון אלבומים.
        """
        
        system_prompt = """
        You are an expert Photo Curator and Travel Assistant. 
        Your goal is to help users organize their travel photos based on metadata (location, time, and weather).

        RULES:
        1. DATA FUSION: Use the provided location (city, POI, suburb) and weather to create creative and descriptive album names.
        2. HALLUCINATION MANAGEMENT: Use ONLY the photos provided in the data. Do not invent photos that don't exist.
        3. MULTI-STEP REASONING:
           - First, group photos by location and time gaps (e.g., morning vs. evening).
           - Second, consider the weather (e.g., if it was rainy, suggest indoor activities or themed titles).
           - Third, suggest 2-3 logical albums with a list of photo IDs for each.
        4. TONE: Be helpful, creative, and proactive.
        """

        user_content = f"""
        User Query: "{user_query}"

        Available Photo Data:
        {enriched_data}

        Please suggest how to organize these photos into albums.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.7 # מאזן בין יצירתיות לדיוק
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error contacting OpenAI: {e}"