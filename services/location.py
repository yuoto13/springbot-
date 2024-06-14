from geopy.geocoders import Nominatim
import logging

async def get_city_by_location(latitude, longitude):
    geolocator = Nominatim(user_agent="weather_bot")
    try:
        location_info = geolocator.reverse((latitude, longitude), language="ru")
        city = location_info.raw['address'].get('city', location_info.raw['address'].get('town', ''))
        return city
    except Exception as e:
        logging.error(f"Exception occurred while fetching location: {e}")
        return None