import time
import json
import os
import sys
from datetime import datetime

sys.path.append(os.getcwd())

class TripCoordinator:
    def __init__(self, geo_service, weather_service):
        self.geo = geo_service
        self.weather = weather_service
        self.cache_file = "data/geo_cache.json"
        self.cache = self._load_cache()

    def _load_cache(self):
        """load cache if exists"""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        """save cache to file"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=4)

    def _parse_time_features(self, timestamp):
        """extract date, time, and part of the day from timestamp"""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            hour = dt.hour
            
            if 5 <= hour < 12:
                time_of_day = "Morning"
            elif 12 <= hour < 17:
                time_of_day = "Afternoon"
            elif 17 <= hour < 21:
                time_of_day = "Evening"
            else:
                time_of_day = "Night"
            
            return {
                "date": dt.strftime("%Y-%m-%d"),
                "time": dt.strftime("%H:%M"),
                "time_of_day": time_of_day,
                "day_of_week": dt.strftime("%A"),
                "hour": hour
            }
        except Exception as e:
            print(f"⚠️ Could not parse timestamp '{timestamp}': {e}")
            return {
                "date": "N/A",
                "time": "N/A",
                "time_of_day": "Unknown",
                "day_of_week": "N/A",
                "hour": None
            }

    def enrich_trip_data(self, photos):
        """
        attach weather + location to raw data with external services. 
        Uses caching and rate limiting for API efficiency.
        """
        enriched_photos = []
        
        for photo in photos:
            lat = photo['gps']['lat']
            lon = photo['gps']['lon']
            timestamp = photo['timestamp']
            
            # 1. Time Features
            time_data = self._parse_time_features(timestamp)
            
            # 2. Location (עם Cache)
            location_key = f"{round(lat, 3)},{round(lon, 3)}"
            
            if location_key in self.cache:
                location_data = self.cache[location_key]
            else:
                print(f"Fetching location for {location_key}...")
                location_data = self.geo.get_location_details(lat, lon)
                self.cache[location_key] = location_data
                self._save_cache()
                time.sleep(1.1)
            
            weather_data = self.weather.get_weather(lat, lon, timestamp)
            
            # Data Fusion
            enriched_photo = {
                "id": photo['id'],
                "timestamp": timestamp,
                "date": time_data['date'],
                "time": time_data['time'],
                "time_of_day": time_data['time_of_day'],
                "day_of_week": time_data['day_of_week'],
                "location": {
                    "lat": location_data.get('lat'),
                    "lon": location_data.get('lon'),
                    "poi": location_data.get('poi'),
                    "suburb": location_data.get('suburb'),
                    "city": location_data.get('city'),
                    "full_address": location_data.get('display_name')
                },
                "weather": {
                    "temp": weather_data['temp'],
                    "condition": weather_data['condition']
                }
            }
            enriched_photos.append(enriched_photo)
            
        return enriched_photos
    
    def save_enriched_data(self, enriched_data, output_file="data/enriched_photos.json"):
        """Save enriched photos to JSON file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enriched_data, f, indent=4, ensure_ascii=False)
        print(f"✅ Enriched data saved to {output_file}")


#test run
if __name__ == "__main__":
    from src.services.geo_service import GeoService
    from src.services.weather_service import WeatherService
    
    with open('data/mock_photos.json', 'r') as f:
        mock_data = json.load(f)
        
    coord = TripCoordinator(GeoService(), WeatherService())
    full_results = coord.enrich_trip_data(mock_data)
    coord.save_enriched_data(full_results)