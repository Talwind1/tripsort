import requests
import time

class GeoService:
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org/reverse"
        self.headers = {
            "User-Agent": "TripSort_App_Educational_Project" # חובה לפי תנאי השימוש שלהם
        }

    def get_location_details(self, lat, lon):
        """
        הופך קואורדינטות לכתובת מפורטת.
        """
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "addressdetails": 1,
            "accept-language": "en" # אנחנו רוצים שמות באנגלית כדי שיהיה ל-LLM קל לעבד
        }

        try:
            # Nominatim מבקשים לא להציף בבקשות (מקסימום 1 לשנייה)
            # אם את מריצה בלולאה על כל המוקה, כדאי להוסיף time.sleep(1) ב-Coordinator
            response = requests.get(self.base_url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            address = data.get("address", {})
            
            # חילוץ הפרטים המעניינים ביותר עבור ה-Data Fusion
            location_info = {
                "display_name": data.get("display_name"), # הכתובת המלאה
                "city": address.get("city") or address.get("town") or address.get("village"),
                "suburb": address.get("suburb") or address.get("neighbourhood"),
                "poi": address.get("amenity") or address.get("tourism") or address.get("landmark")
            }
            
            return location_info
            
        except Exception as e:
            print(f"Geo API Error: {e}")
            return None

# בדיקה מהירה
if __name__ == "__main__":
    service = GeoService()
    # בדיקה על קואורדינטות של הסגרדה פמיליה מהמוקה שלנו
    test_res = service.get_location_details(41.4036, 2.1744)
    print(f"Geo Result: {test_res}")