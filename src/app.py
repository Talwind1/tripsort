import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import json
from services.llm_service import LLMService
from logic.coordinator import TripCoordinator
from services.llm_service import LLMService
from logic.coordinator import TripCoordinator
from services.geo_service import GeoService
from services.weather_service import WeatherService
import pandas as pd
from collections import Counter

# --- הגדרות דף ---
st.set_page_config(page_title="TripSort AI", page_icon="📸", layout="wide")

# --- אתחול שירותים (Cached) ---
@st.cache_resource
def init_services():
    return LLMService(), TripCoordinator(GeoService(), WeatherService())

llm, coordinator = init_services()

# --- טעינת נתונים ---
@st.cache_data
def load_data():
    with open('data/enriched_photos.json', 'r') as f:
        return json.load(f)

enriched_data = load_data()

# --- ניהול זיכרון הצ'אט (Context Management) ---
# זה קריטי כדי לעמוד בדרישה של multi-turn exchanges
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- ממשק צד (Sidebar) ---
with st.sidebar:
    st.title("📸 TripSort AI")
    st.markdown("### Your Intelligent Photo Curator")
    st.divider()
    
    # סטטיסטיקות
    st.metric("Total Photos", len(enriched_data))
    
    # חילוץ עיר שכיחה (הלוגיקה שלך)
    all_cities = [p["location"]["city"] for p in enriched_data if p.get("location") and p["location"].get("city")]
    if all_cities:
        most_common_city = Counter(all_cities).most_common(1)[0][0]
        st.info(f"Trip to: {most_common_city} 🇪🇸")
    
    st.divider()
    
    # הצגת המפה ב-Sidebar כדי להשאיר את הצ'אט נקי (External Data Integration)
    map_points = [{"lat": float(p["location"]["lat"]), "lon": float(p["location"]["lon"])} 
                  for p in enriched_data if p.get("location") and p["location"].get("lat")]
    
    if map_points:
        st.subheader("Journey Map")
        st.map(pd.DataFrame(map_points))

# --- ממשק הצ'אט המרכזי ---

# 1. הצגת היסטוריית ההודעות
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 2. קלט מהמשתמש (Chat Input במקום Text Input)
if prompt := st.chat_input("How would you like to organize your photos?"):
    
    # הצגת הודעת המשתמש ושמירה בזיכרון
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 3. תגובת ה-AI (Hallucination Handling & Data Integration)
    with st.chat_message("assistant"):
        with st.spinner("AI is analyzing your trip metadata..."):
            # שליחת השאילתה ל-LLM עם המידע המועשר
            response = llm.get_album_suggestions(
                enriched_data, 
                prompt, 
                chat_history=st.session_state.messages[:-1] # שולחים את כל מה שהיה לפני השאלה הנוכחית
            )
            st.markdown(response)
            
            # כפתור שקיפות (User Trust - סעיף 2 בקריטריונים)
            with st.expander("View Source Metadata"):
                st.json(enriched_data[:2]) 
    
    # שמירת תגובת ה-AI בזיכרון
    st.session_state.messages.append({"role": "assistant", "content": response})

# --- גלריה ויזואלית בתחתית (אופציונלי) ---
if not st.session_state.messages:
    st.divider()
    st.info("Start a conversation to organize your photos! Try asking for 'mornings in Barcelona' or 'rainy day activities'.")