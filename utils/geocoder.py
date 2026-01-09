# utils/geocoder.py
import requests
from django.conf import settings

def geocode_address(address, city="Nairobi"):
    """Convert address to coordinates using Nominatim (OpenStreetMap)"""
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': f"{address}, {city}, Kenya",
            'format': 'json',
            'limit': 1
        }
        headers = {
            'User-Agent': 'CampusMarketplace/1.0 (contact@example.com)'
        }
        
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        
        if data:
            return {
                'latitude': float(data[0]['lat']),
                'longitude': float(data[0]['lon'])
            }
    except Exception as e:
        print(f"Geocoding error: {e}")
    
    return None