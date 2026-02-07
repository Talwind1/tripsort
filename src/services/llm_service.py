import os
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# מוצא את הנתיב האמיתי של תיקיית הפרויקט
base_dir = Path(__file__).resolve().parent.parent.parent
env_path = base_dir / '.env'
load_dotenv(dotenv_path=env_path)

class LLMService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        
        if api_key:
            print(f"DEBUG: Key loaded starting with: {api_key[:10]}...")
        else:
            print(f"DEBUG: No API key found at {env_path}")
            
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"

    def _generate_data_summary(self, enriched_data, limit=20):
        """
        פונקציית עזר: הופכת את ה-JSON לטקסט קריא וממוקד עבור ה-LLM.
        זה עוזר למנוע 'רעש' ולוודא שה-AI רואה את הכתובת המלאה.
        """
        summary = ""
        for p in enriched_data[:limit]:
            loc = p.get('location', {})
            # חילוץ נתונים עם Fallback למקרה ששדות ריקים
            summary += (
                f"- ID: {p.get('id')}, "
                f"City: {loc.get('city', 'Unknown')}, "
                f"Area: {loc.get('suburb', 'N/A')}, "
                f"POI: {loc.get('poi', 'None')}, "
                f"Address: {loc.get('full_address', 'N/A')}\n"
            )
        return summary

    def get_album_suggestions(self, enriched_data, user_query):
        """
        שולח את הנתונים המועשרים ל-LLM ומקבל הצעות לארגון אלבומים.
        """
        
        # 1. יצירת הסיכום המזוקק
        data_summary = self._generate_data_summary(enriched_data)

        # 2. הגדרת ההנחיות למודל
        system_prompt = """
            You are an expert Photo Curator and Travel Assistant. 
            Your goal is to organize travel photos based ONLY on the provided metadata (location, time, and weather).

            STRICT RULES:
            1. RELEVANCE: If photos don't match the query, explicitly state it.
            2. DATA FUSION: Combine city, POI, and suburb to create descriptive names.
            3. HALLUCINATION: Use ONLY the IDs and locations provided.
            #4. NAMING: Generate collective names for albums. Avoid specifics like 'Sunny' if not all photos share that trait.
             #  Example: Use 'Barcelona Exploration' instead of 'Sunny Barcelona' if weather varies.
            4. NAMING: Create names that feel like travel experiences rather than geographic labels. Example: Use 'Gothic Quarter Vibes' or 'Hidden Gems of Gràcia' instead of 'Old Town Photos'. Ensure the name represents the entire group of photos provided.
            5. FALLBACK: If 'POI' is empty, look at 'Address' to identify the landmark.
            6. TONE: Helpful and proactive, yet grounded in data.
            """

        # 3. בניית התוכן שנשלח (הזרקת המשתנים)
        user_content = f"""
        User Request: "{user_query}"

        Below is the summarized data from the user's photos:
        {data_summary}

        Please suggest 2-3 logical albums. For each album, provide:
        - A creative name
        - A brief description based on the location/address
        - List of photo IDs included
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error contacting OpenAI: {e}"