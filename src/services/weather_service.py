import requests

class WeatherService:
    def __init__(self):
        self.base_url = "https://archive-api.open-meteo.com/v1/archive"

    def get_weather(self, lat, lon, timestamp):
        """
        Fetch historical weather data for location and timestamp.
        """
        # extracting (YYYY-MM-DD)
        date_str = timestamp.split('T')[0]
        
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": date_str,
            "end_date": date_str,
            "daily": ["weather_code", "temperature_2m_max"],
            "timezone": "auto"
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            max_temp = data['daily']['temperature_2m_max'][0]
            weather_code = data['daily']['weather_code'][0]

            # weather code to textual desctiption
            condition = self._translate_weather_code(weather_code)
            
            return {
                "temp": f"{max_temp}°C",
                "condition": condition
            }
        except Exception as e:
            print(f"Weather API Error: {e}")
            return {"temp": "Unknown", "condition": "Unknown"}

    def _translate_weather_code(self, code):
        mapping = {
            0: "Clear sky",
            1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Fog", 48: "Depositing rime fog",
            51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
            95: "Thunderstorm"
        }
        return mapping.get(code, "Cloudy")

# Quick test
if __name__ == "__main__":
    service = WeatherService()
    result = service.get_weather(41.3871, 2.1701, "2024-05-10T10:30:00")
    print(f"Weather Result: {result}")