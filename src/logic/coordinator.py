import time
import json
import os
import sys
import os
sys.path.append(os.getcwd())

class TripCoordinator:
    def __init__(self, geo_service, weather_service):
        self.geo = geo_service
        self.weather = weather_service
        self.cache_file = "data/geo_cache.json"
        self.cache = self._load_cache()

    def _load_cache(self):
        """טוען את המטמון מהקובץ אם הוא קיים"""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        """שומר את המטמון לקובץ"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=4)

    def enrich_trip_data(self, photos):
        """
        עובר על כל התמונות ומעשיר אותן במיקום ומזג אוויר.
        מיישם מנגנון Cache ו-Throttle (השהייה) למניעת חסימות.
        """
        enriched_photos = []
        
        for photo in photos:
            lat = photo['gps']['lat']
            lon = photo['gps']['lon']
            timestamp = photo['timestamp']
            
            # יצירת מפתח ייחודי למיקום (עיגול ל-3 ספרות לדיוק שכונתי וחיסכון בבקשות)
            location_key = f"{round(lat, 3)},{round(lon, 3)}"
            
            # 1. שליפת מיקום (עם Cache)
            if location_key in self.cache:
                location_data = self.cache[location_key]
            else:
                print(f"Fetching location for {location_key}...")
                location_data = self.geo.get_location_details(lat, lon)
                self.cache[location_key] = location_data
                self._save_cache()
                time.sleep(1.1) # הגנה על ה-API של Nominatim
            
            # 2. שליפת מזג אוויר (דינמי לפי תאריך)
            # הערה: Open-Meteo פחות נוקשים ב-Rate Limit, אבל כדאי להיזהר
            weather_data = self.weather.get_weather(lat, lon, timestamp)
            
            # 3. Data Fusion - איחוד הנתונים לאובייקט אחד
            # 3. Data Fusion - איחוד הנתונים לאובייקט אחד (המבנה המפורט)
            enriched_photo = {
                "id": photo['id'],
                "time": timestamp,
                # אנחנו שומרים את כל האובייקט שהגיע מה-GeoService
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
            """שומר את נתוני התמונות המועשרים לקובץ JSON"""
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(enriched_data, f, indent=4, ensure_ascii=False)
            print(f"✅ Success! Enriched data saved to {output_file}")
    

# בדיקת הרצה מהירה
if __name__ == "__main__":
    from src.services.geo_service import GeoService
    from src.services.weather_service import WeatherService
    
    # 1. טעינת נתוני המקור
    with open('data/mock_photos.json', 'r') as f:
        mock_data = json.load(f)
        
    # 2. אתחול ה-Coordinator
    coord = TripCoordinator(GeoService(), WeatherService())
    
    # 3. העשרת הנתונים (שים לב - בזכות ה-Cache זה יהיה מהיר עכשיו!)
    full_results = coord.enrich_trip_data(mock_data)
    
    # 4. שמירה לקובץ
    coord.save_enriched_data(full_results)