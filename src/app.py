import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import json
from services.llm_service import LLMService
from logic.coordinator import TripCoordinator
from services.geo_service import GeoService
from services.weather_service import WeatherService
import pandas as pd
from collections import Counter

st.set_page_config(page_title="TripSort AI", page_icon="📸", layout="wide")

@st.cache_resource
def init_services():
    return LLMService(), TripCoordinator(GeoService(), WeatherService())

llm, coordinator = init_services()

@st.cache_data
def load_data():
    with open('data/enriched_photos.json', 'r') as f:
        return json.load(f)

enriched_data = load_data()

# Context Management
# multi-turn exchanges
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("📸 TripSort AI")
    st.markdown("### Your Intelligent Photo Curator")
    st.divider()
    
    
    st.metric("Total Photos", len(enriched_data))
    
    # find city of the trip
    all_cities = [p["location"]["city"] for p in enriched_data if p.get("location") and p["location"].get("city")]
    if all_cities:
        most_common_city = Counter(all_cities).most_common(1)[0][0]
        st.info(f"Trip to: {most_common_city} 🇪🇸")
    
    st.divider()
    
    map_points = [{"lat": float(p["location"]["lat"]), "lon": float(p["location"]["lon"])} 
                  for p in enriched_data if p.get("location") and p["location"].get("lat")]
    
    if map_points:
        st.subheader("Journey Map")
        st.map(pd.DataFrame(map_points))

# chat interface

# show history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How would you like to organize your photos?"):
    
# Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI response (Hallucination Handling & Data Integration)
    with st.chat_message("assistant"):
        with st.spinner("AI is analyzing your trip metadata..."):
            # send query with enriched data to LLM
            response = llm.get_album_suggestions(
                enriched_data, 
                prompt, 
                chat_history=st.session_state.messages[:-1] 
                )
            st.markdown(response)
            
            # User Trust
            with st.expander("View Source Metadata"):
                st.json(enriched_data[:2]) 
    
    # save response in memory
    st.session_state.messages.append({"role": "assistant", "content": response})

if not st.session_state.messages:
    st.divider()
    st.info("Start a conversation to organize your photos! Try asking for 'mornings in Barcelona' or 'rainy day activities'.")