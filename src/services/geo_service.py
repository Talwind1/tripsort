import requests

class GeoService:
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org/reverse"
        self.headers = {
            "User-Agent": "TripSort_App_Educational_Project" 
        }

    def get_location_details(self, lat, lon):
        """
        Convert GPS coordinates to location details       
        """
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "addressdetails": 1,
            "accept-language": "en" 
        }

        try:
            response = requests.get(self.base_url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            address = data.get("address", {})
            
            # extracting Data Fusion
            location_info = {
                "lat": lat,
                "lon": lon,
                "display_name": data.get("display_name"), # full address
                "city": address.get("city") or address.get("town") or address.get("village"),
                "suburb": address.get("suburb") or address.get("neighbourhood"),
                "poi": address.get("amenity") or address.get("tourism") or address.get("landmark")
            }
            
            return location_info
            
        except Exception as e:
            print(f"Geo API Error: {e}")
            return None
        
# Quick test
if __name__ == "__main__":
    service = GeoService()
    test_res = service.get_location_details(41.4036, 2.1744)
    print(f"Geo Result: {test_res}")