import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent.parent
env_path = base_dir / '.env'
load_dotenv(dotenv_path=env_path)

class LLMService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"

    def _generate_data_summary(self, enriched_data, limit=50):
        """Data Fusion: combines geo + weather + time data"""
        summary = ""
        for p in enriched_data[:limit]:
            loc = p.get('location', {})
            weath = p.get('weather', {})
            
            summary += (
                f"📷 ID: {p.get('id')}\n"
                f"   📅 {p.get('date')} ({p.get('day_of_week')})\n"
                f"   🕐 {p.get('time')} - {p.get('time_of_day')}\n"
                f"   📍 {loc.get('city', 'Unknown')}, {loc.get('suburb', 'N/A')}\n"
                f"   🏛️ Near: {loc.get('poi') or loc.get('full_address', 'N/A')}\n"
                f"   🌤️ {weath.get('temp', 'N/A')}, {weath.get('condition', 'N/A')}\n\n"
            )
        
        if len(enriched_data) > limit:
            summary += f"\n... and {len(enriched_data) - limit} more photos\n"
            
        return summary

    def get_album_suggestions(self, enriched_data, user_query, chat_history=None):
        """
        Decision Logic:
        - Factual questions → Answer from metadata
        - Creative requests → LLM generates ideas
        - Photo IDs → Validated to prevent hallucinations
        """
        data_summary = self._generate_data_summary(enriched_data)

        # Control Strategy: Prompt engineering to reduce hallucinations
        system_prompt = """
You are an expert Photo Curator and Travel Assistant.

CONVERSATION STYLE:
- When user says "those", "them", "these" - refer to photos from your previous response
- When user says "also", "too", "add" - combine with the previous request  
- When user says "different", "other" - provide alternatives to previous suggestion
- Track the context of what was discussed before

STRICT RULES:
1. CONTEXT MEMORY: Remember all previous requests in this conversation
2. DIRECT ANSWERS: If user asks about weather, dates, or locations, answer directly from metadata
3. DATA FUSION: Use location AND weather together for creative album names
4. HALLUCINATION PREVENTION: Use ONLY the photo IDs provided in the data. Never invent IDs.
5. NAMING: Create experience-based album names (e.g., 'Rainy Morning Cafés' not 'Album 1')
6. FALLBACK: Use 'Address' field if 'POI' is empty
7. BE SPECIFIC: Always include the actual photo IDs when suggesting albums

FORMAT:
When suggesting albums, use this structure:
**Album Name** (X photos)
- Photo IDs: [list the actual IDs]
- Description: [brief context]
"""

        # Multi-turn: build messages with history
        messages = [{"role": "system", "content": system_prompt}]
        
        if chat_history:
            for msg in chat_history[-10:]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        user_content = f"""
User Request: "{user_query}"

Trip Data Summary:
{data_summary}

Please answer the question or suggest 2-3 logical albums.
"""
        messages.append({"role": "user", "content": user_content})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # Hallucination Detection: validate IDs
            valid_ids = {str(p["id"]) for p in enriched_data}
            mentioned_ids = re.findall(r'ID[s]?[:\s]+([0-9,\s]+)', ai_response)
            
            if mentioned_ids:
                all_mentioned = []
                for match in mentioned_ids:
                    ids_in_match = [id.strip() for id in match.split(',')]
                    all_mentioned.extend(ids_in_match)
                
                invalid_ids = [id for id in all_mentioned if id and id not in valid_ids]
                
                if invalid_ids:
                    ai_response += f"\n\n⚠️ Warning: IDs {', '.join(invalid_ids)} don't exist in your trip data."
            
            return ai_response
            
        except Exception as e:
            return f"Error contacting OpenAI: {e}"