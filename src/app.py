import streamlit as st
import json
from src.services.llm_service import LLMService
from src.logic.coordinator import TripCoordinator
from src.services.geo_service import GeoService
from src.services.weather_service import WeatherService
import pandas as pd
from collections import Counter

# הגדרות דף
st.set_page_config(page_title="TripSort AI", page_icon="📸", layout="wide")

st.title("📸 TripSort AI")
st.subheader("Your Intelligent Photo Curator")

# אתחול שירותים
#@st.cache_resource # שומר את השירותים בזיכרון שלא יווצרו מחדש בכל לחיצה
def init_services():
    return LLMService(), TripCoordinator(GeoService(), WeatherService())

llm, coordinator = init_services()

# טעינת נתונים
with open('data/enriched_photos.json', 'r') as f:
    enriched_data = json.load(f)

# ממשק צד (Sidebar)
with st.sidebar:
    st.header("Trip Stats")
    st.metric("Total Photos", len(enriched_data))
    # st.info("Trip to: Barcelona 🇪🇸")

# אזור הקלט של המשתמש
user_query = st.text_input("How would you like to organize your photos?", 
                           placeholder="e.g., 'Group my first day photos with creative names'")

if user_query:
    with st.spinner("AI is working its magic..."):
        suggestion = llm.get_album_suggestions(enriched_data, user_query)
        st.markdown("### AI Suggestions")
        st.success(suggestion)

# תצוגת גלריה בסיסית (כדי שיהיה ויזואלי)
st.divider()
st.write("### Raw Metadata Preview")
st.json(enriched_data) # מציג רק את 2 התמונות הראשונות כדוגמה

# 1. ניצור רשימה ריקה שתכיל רק את הנקודות למפה
map_points = []

# 2. נעבור תמונה-תמונה (כאן ה-p הופך ל-photo כדי שיהיה ברור)
for photo in enriched_data:
    # נבדוק אם יש בכלל מידע על מיקום בתוך התמונה הזו
    location_data = photo.get("location")
    
    if location_data:
        # ננסה לשלוף את ה-lat וה-lon
        lat = location_data.get("lat")
        lon = location_data.get("lon")
        
        # רק אם שניהם קיימים, נוסיף אותם לרשימת המפה
        if lat is not None and lon is not None:
            map_points.append({"lat": float(lat), "lon": float(lon)})

# 3. אם מצאנו נקודות, נציג את המפה
if map_points:
    st.subheader("Map of your journey")
    df = pd.DataFrame(map_points)
    st.map(df)
else:
    # אם לא מצאנו, לא נראה כלום או נראה הודעה שקטה
    st.info("No GPS data found to display on map.")

# 1. חילוץ כל שמות הערים שקיימים בנתונים (סינון ערכים ריקים)
all_cities = [
    p["location"]["city"] 
    for p in enriched_data 
    if p.get("location") and p["location"].get("city")
]

# 2. מציאת העיר השכיחה ביותר
if all_cities:
    most_common_city = Counter(all_cities).most_common(1)[0][0]
    st.info(f"TripSort: {most_common_city} Memories 📸")
else:
    st.info("TripSort: Your Journey 📸")