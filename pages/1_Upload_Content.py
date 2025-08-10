import streamlit as st
import os
from datetime import date, datetime
from utils.geolocation import get_location_options, get_coordinates_from_address
from utils.file_handler import upload_file_to_supabase
from database import insert_temple, insert_content_contribution, insert_historical_event
import requests

# Set environment variables directly
os.environ["SUPABASE_URL"] = "https://rrbrghxzuzzxroqbwfqi.supabase.co"
os.environ["SUPABASE_ANON_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJyYnJnaHh6dXp6eHJvcWJ3ZnFpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM4MDU0OTMsImV4cCI6MjA2OTM4MTQ5M30.Evcf0lPD7reXvgZNZrAZDoHHLDx72AUmUHMSOXgQNV4"
os.environ["DATABASE_URL"] = "postgresql://postgres:Akhil%40112233@db.rrbrghxzuzzxroqbwfqi.supabase.co:5432/postgres"

st.set_page_config(page_title="Upload Content", page_icon="📤", layout="wide")

st.title("📤 Upload Content")
st.markdown("Contribute to the temple heritage documentation by uploading multimedia content, temple information, or historical events.")

# Content type selection
content_type = st.selectbox(
    "What would you like to contribute?",
    ["Photo/Image", "Audio Recording", "Document", "Temple Information", "Historical Event"]
)

# Contributor information
st.subheader("👤 Contributor Information")
col1, col2 = st.columns(2)
with col1:
    contributor_name = st.text_input("Your Name (optional)", placeholder="Leave blank to remain anonymous")
with col2:
    anonymous = st.checkbox("Contribute anonymously")

if anonymous:
    contributor_name = None

# Location section
st.subheader("📍 Location Information")
location_method = st.radio(
    "How would you like to set the location?",
    ["Manual Entry", "IP-based Location", "GPS Coordinates"]
)

latitude, longitude, location_address = None, None, ""

if location_method == "Manual Entry":
    col1, col2 = st.columns(2)
    with col1:
        manual_lat = st.number_input("Latitude", format="%.6f", value=0.0)
    with col2:
        manual_lon = st.number_input("Longitude", format="%.6f", value=0.0)
    
    location_address = st.text_input("Address/Description", placeholder="Enter address or location description")
    
    if manual_lat != 0.0 or manual_lon != 0.0:
        latitude, longitude = manual_lat, manual_lon

elif location_method == "IP-based Location":
    if st.button("Get Current Location from IP"):
        try:
            response = requests.get("http://ip-api.com/json/")
            if response.status_code == 200:
                data = response.json()
                latitude = data.get('lat')
                longitude = data.get('lon')
                location_address = f"{data.get('city', '')}, {data.get('regionName', '')}, {data.get('country', '')}"
                st.success(f"Location detected: {location_address}")
                st.write(f"Coordinates: {latitude}, {longitude}")
            else:
                st.error("Could not detect location from IP")
        except Exception as e:
            st.error(f"Error detecting location: {str(e)}")

elif location_method == "GPS Coordinates":
    st.info("GPS location detection requires browser permissions and HTTPS.")
    col1, col2 = st.columns(2)
    with col1:
        gps_lat = st.number_input("GPS Latitude", format="%.6f", value=0.0)
    with col2:
        gps_lon = st.number_input("GPS Longitude", format="%.6f", value=0.0)
    
    if gps_lat != 0.0 or gps_lon != 0.0:
        latitude, longitude = gps_lat, gps_lon
        location_address = st.text_input("Address (optional)", placeholder="Provide address if known")

# Content-specific forms
st.subheader("📝 Content Details")

if content_type in ["Photo/Image", "Audio Recording", "Document"]:
    # File upload
    if content_type == "Photo/Image":
        uploaded_file = st.file_uploader(
            "Choose image file",
            type=['jpg', 'jpeg', 'png', 'gif', 'bmp'],
            help="Supported formats: JPG, JPEG, PNG, GIF, BMP"
        )
    elif content_type == "Audio Recording":
        uploaded_file = st.file_uploader(
            "Choose audio file",
            type=['mp3', 'wav', 'm4a', 'ogg', 'flac'],
            help="Supported formats: MP3, WAV, M4A, OGG, FLAC"
        )
    else:  # Document
        uploaded_file = st.file_uploader(
            "Choose document",
            type=['pdf', 'doc', 'docx', 'txt', 'rtf'],
            help="Supported formats: PDF, DOC, DOCX, TXT, RTF"
        )
    
    title = st.text_input("Title", placeholder="Give your contribution a descriptive title")
    description = st.text_area("Description", placeholder="Describe the content, its significance, or historical context")
    
    if st.button("Upload Content", type="primary", disabled=not uploaded_file or not title):
        if uploaded_file and title:
            with st.spinner("Uploading content..."):
                try:
                    # Upload file to Supabase storage
                    file_url = upload_file_to_supabase(uploaded_file, content_type.lower().replace("/", "_").replace(" ", "_"))
                    
                    if file_url:
                        # Insert into database
                        contribution_id = insert_content_contribution(
                            title=title,
                            content_type=content_type,
                            description=description,
                            file_url=file_url,
                            latitude=latitude,
                            longitude=longitude,
                            location_address=location_address,
                            contributor_name=contributor_name if not anonymous else None
                        )
                        
                        if contribution_id:
                            st.success("✅ Content uploaded successfully!")
                            st.balloons()
                        else:
                            st.error("❌ Failed to save content information to database")
                    else:
                        st.error("❌ Failed to upload file")
                except Exception as e:
                    st.error(f"❌ Upload error: {str(e)}")

elif content_type == "Temple Information":
    col1, col2 = st.columns(2)
    
    with col1:
        temple_name = st.text_input("Temple Name*", placeholder="Official name of the temple")
        deity = st.text_input("Main Deity", placeholder="Primary deity worshipped")
        architectural_style = st.selectbox(
            "Architectural Style",
            ["Dravidian", "Nagara", "Vesara", "Indo-Islamic", "Colonial", "Modern", "Other", "Unknown"]
        )
    
    with col2:
        built_year = st.number_input("Built Year", min_value=1, max_value=datetime.now().year, value=None)
        if not location_address:
            location_address = st.text_input("Temple Address", placeholder="Full address of the temple")
    
    history = st.text_area("History & Significance", placeholder="Historical background, legends, cultural significance...")
    
    if st.button("Add Temple", type="primary", disabled=not temple_name):
        if temple_name:
            with st.spinner("Adding temple information..."):
                try:
                    # Create description with additional details
                    full_description = f"Deity: {deity}\nArchitectural Style: {architectural_style}"
                    if built_year:
                        full_description += f"\nBuilt Year: {built_year}"
                    if history:
                        full_description += f"\n\nHistory & Significance:\n{history}"
                    
                    temple_id = insert_temple(
                        name=temple_name,
                        description=full_description,
                        location=location_address,
                        image_url=None,
                        audio_url=None,
                        contributor_name=contributor_name if not anonymous else None
                    )
                    
                    if temple_id:
                        st.success("✅ Temple information added successfully!")
                        st.balloons()
                    else:
                        st.error("❌ Failed to add temple information")
                except Exception as e:
                    st.error(f"❌ Error adding temple: {str(e)}")

elif content_type == "Historical Event":
    col1, col2 = st.columns(2)
    
    with col1:
        event_title = st.text_input("Event Title*", placeholder="Name of the historical event")
        event_date = st.date_input("Event Date", value=None)
    
    with col2:
        related_temple = st.text_input("Related Temple (optional)", placeholder="Name of associated temple")
    
    event_description = st.text_area("Event Description", placeholder="Describe the historical event, its significance, and impact...")
    
    if st.button("Add Historical Event", type="primary", disabled=not event_title):
        if event_title:
            with st.spinner("Adding historical event..."):
                try:
                    # For now, we'll use content_contributions table for historical events
                    # In a full implementation, you'd want to use the historical_events table
                    contribution_id = insert_content_contribution(
                        title=event_title,
                        content_type="Historical Event",
                        description=event_description,
                        file_url=None,
                        latitude=latitude,
                        longitude=longitude,
                        location_address=location_address,
                        contributor_name=contributor_name if not anonymous else None
                    )
                    
                    if contribution_id:
                        st.success("✅ Historical event added successfully!")
                        st.balloons()
                    else:
                        st.error("❌ Failed to add historical event")
                except Exception as e:
                    st.error(f"❌ Error adding event: {str(e)}")

# Navigation
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🏠 Back to Home"):
        st.switch_page("app.py")
with col2:
    if st.button("🗂️ Browse Temples"):
        st.switch_page("pages/2_Browse_Temples.py")
with col3:
    if st.button("🗺️ View Map"):
        st.switch_page("pages/5_Heritage_Map.py")
