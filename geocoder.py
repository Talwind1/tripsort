import requests
import time

def get_location_name(lat, lon):
    # Nominatim דורשים User-Agent כדי לדעת מי פונה אליהם
    headers = {'User-Agent': 'TripSort_Educational_Project_v1'}
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # שליפת שם המקום או הכתובת
            return data.get('display_name', 'Unknown Location')
        return "Location not found"
    except Exception as e:
        return f"Error: {e}"

# בדיקה מהירה (קואורדינטות של כיכר קטלוניה, ברצלונה)
if __name__ == "__main__":
    print(f"Testing API... {get_location_name(41.3871, 2.1700)}")    