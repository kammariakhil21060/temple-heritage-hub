import streamlit as st
import requests
from typing import Tuple, Optional

def get_ip_location() -> Optional[Tuple[float, float, str]]:
    """
    Get location from IP address using ip-api.com
    Returns: (latitude, longitude, address) or None if failed
    """
    try:
        response = requests.get("http://ip-api.com/json/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                latitude = data.get('lat')
                longitude = data.get('lon')
                city = data.get('city', '')
                region = data.get('regionName', '')
                country = data.get('country', '')
                address = f"{city}, {region}, {country}".strip(', ')
                return latitude, longitude, address
    except Exception as e:
        st.error(f"Error getting IP location: {str(e)}")
    return None

def get_coordinates_from_address(address: str) -> Optional[Tuple[float, float]]:
    """
    Get coordinates from address using Nominatim (OpenStreetMap)
    Returns: (latitude, longitude) or None if failed
    """
    try:
        # Using Nominatim API for geocoding
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': address,
            'format': 'json',
            'limit': 1
        }
        headers = {
            'User-Agent': 'Temple Heritage Hub (Streamlit App)'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                latitude = float(data[0]['lat'])
                longitude = float(data[0]['lon'])
                return latitude, longitude
    except Exception as e:
        st.error(f"Error geocoding address: {str(e)}")
    return None

def get_location_options():
    """
    Provide location input options for users
    Returns a dictionary with location method and coordinates
    """
    location_data = {
        'method': None,
        'latitude': None,
        'longitude': None,
        'address': None
    }
    
    st.subheader("📍 Location Information")
    
    location_method = st.radio(
        "How would you like to set the location?",
        ["Manual Entry", "IP-based Location", "Address Lookup", "GPS Coordinates"]
    )
    
    location_data['method'] = location_method
    
    if location_method == "Manual Entry":
        col1, col2 = st.columns(2)
        with col1:
            latitude = st.number_input("Latitude", format="%.6f", value=0.0, key="manual_lat")
        with col2:
            longitude = st.number_input("Longitude", format="%.6f", value=0.0, key="manual_lon")
        
        address = st.text_input("Address/Description", placeholder="Enter address or location description")
        
        if latitude != 0.0 or longitude != 0.0:
            location_data['latitude'] = latitude
            location_data['longitude'] = longitude
            location_data['address'] = address
    
    elif location_method == "IP-based Location":
        if st.button("🌐 Detect Location from IP"):
            with st.spinner("Detecting location..."):
                ip_location = get_ip_location()
                if ip_location:
                    latitude, longitude, address = ip_location
                    location_data['latitude'] = latitude
                    location_data['longitude'] = longitude
                    location_data['address'] = address
                    
                    st.success(f"✅ Location detected: {address}")
                    st.info(f"Coordinates: {latitude:.6f}, {longitude:.6f}")
                else:
                    st.error("❌ Could not detect location from IP address")
    
    elif location_method == "Address Lookup":
        address_input = st.text_input("Enter Address", placeholder="e.g., Angkor Wat, Cambodia")
        
        if st.button("🔍 Lookup Coordinates") and address_input:
            with st.spinner("Looking up coordinates..."):
                coordinates = get_coordinates_from_address(address_input)
                if coordinates:
                    latitude, longitude = coordinates
                    location_data['latitude'] = latitude
                    location_data['longitude'] = longitude
                    location_data['address'] = address_input
                    
                    st.success(f"✅ Coordinates found: {latitude:.6f}, {longitude:.6f}")
                else:
                    st.error("❌ Could not find coordinates for this address")
    
    elif location_method == "GPS Coordinates":
        st.info("📱 For GPS location, please enter coordinates manually or use a GPS app on your device.")
        
        col1, col2 = st.columns(2)
        with col1:
            gps_lat = st.number_input("GPS Latitude", format="%.6f", value=0.0, key="gps_lat")
        with col2:
            gps_lon = st.number_input("GPS Longitude", format="%.6f", value=0.0, key="gps_lon")
        
        manual_address = st.text_input("Address (optional)", placeholder="Provide address if known")
        
        if gps_lat != 0.0 or gps_lon != 0.0:
            location_data['latitude'] = gps_lat
            location_data['longitude'] = gps_lon
            location_data['address'] = manual_address
    
    return location_data

def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Validate if coordinates are within valid ranges
    Returns: True if valid, False otherwise
    """
    if latitude is None or longitude is None:
        return False
    
    return -90 <= latitude <= 90 and -180 <= longitude <= 180

def format_coordinates(latitude: float, longitude: float, precision: int = 6) -> str:
    """
    Format coordinates for display
    Returns: Formatted coordinate string
    """
    if latitude is None or longitude is None:
        return "No coordinates"
    
    lat_dir = "N" if latitude >= 0 else "S"
    lon_dir = "E" if longitude >= 0 else "W"
    
    return f"{abs(latitude):.{precision}f}°{lat_dir}, {abs(longitude):.{precision}f}°{lon_dir}"

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula
    Returns: Distance in kilometers
    """
    import math
    
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth's radius in kilometers
    r = 6371
    
    return c * r
