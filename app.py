print("App started")
import streamlit as st
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
from sqlalchemy import text
from utils.supabase_client import (
    get_supabase_client,
    upload_file_to_storage
)
from database import (
    init_database,
    insert_temple,
    get_all_temples,
    get_temple_count,
    get_contribution_count
)

# Set environment variables directly
os.environ["SUPABASE_URL"] = "https://rrbrghxzuzzxroqbwfqi.supabase.co"
os.environ["SUPABASE_ANON_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJyYnJnaHh6dXp6eHJvcWJ3ZnFpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM4MDU0OTMsImV4cCI6MjA2OTM4MTQ5M30.Evcf0lPD7reXvgZNZrAZDoHHLDx72AUmUHMSOXgQNV4"
os.environ["DATABASE_URL"] = "postgresql://postgres:Akhil%40112233@db.rrbrghxzuzzxroqbwfqi.supabase.co:5432/postgres"

# Configure Streamlit page
st.set_page_config(
    page_title="Temple Heritage Hub",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- Upload Function ----------------------

def insert_temple_data(name, description, location, image_url, audio_url):
    """Insert temple data using the new database function"""
    try:
        temple_id = insert_temple(
            name=name,
            description=description,
            location=location,
            image_url=image_url,
            audio_url=audio_url
        )
        return temple_id is not None
    except Exception as e:
        st.error(f"❌ Error inserting temple data: {e}")
        return False

# ----------------- Main App ----------------------

def main():
    st.title("🏛️ Temple Heritage Hub")
    st.markdown("### A platform to document and preserve sacred temple knowledge.")

    # Initialize database connection
    if init_database():
        st.success("✅ Connected to Supabase Database")
        
        # Display statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            temple_count = get_temple_count()
            st.metric("Total Temples", temple_count)
        with col2:
            contribution_count = get_contribution_count()
            st.metric("Total Contributions", contribution_count)
        with col3:
            st.metric("Active Users", "Coming Soon")
    else:
        st.error("❌ Failed to connect to Supabase. Check your .env file or credentials.")
        return

    st.markdown("---")
    st.header("📤 Upload Temple Content")

    with st.form("temple_upload_form"):
        name = st.text_input("Temple Name", max_chars=100)
        description = st.text_area("Temple Description")
        location = st.text_input("Location")
        image_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
        audio_file = st.file_uploader("Upload Audio", type=["mp3", "wav"])

        submit = st.form_submit_button("📤 Submit Temple")

        if submit:
            if not name:
                st.error("❌ Temple name is required!")
            else:
                image_url = None
                audio_url = None

                if image_file:
                    file_path = f"images/{image_file.name}"
                    image_url = upload_file_to_storage(
                        image_file.read(), file_path, image_file.type
                    )

                if audio_file:
                    audio_path = f"audio/{audio_file.name}"
                    audio_url = upload_file_to_storage(
                        audio_file.read(), audio_path, audio_file.type
                    )

                if insert_temple_data(name, description, location, image_url, audio_url):
                    st.success("🎉 Temple uploaded successfully!")
                    st.balloons()
                else:
                    st.error("❌ Failed to upload temple.")

    st.markdown("---")
    st.header("📜 View Recently Uploaded Temples")

    try:
        temples_df = get_all_temples()
        if not temples_df.empty:
            for _, temple in temples_df.head(5).iterrows():
                with st.expander(f"🛕 {temple['name']} - {temple.get('location', 'No location')}"):
                    if temple.get('description'):
                        st.write(temple['description'])
                    if temple.get('image_url'):
                        st.image(temple['image_url'], use_column_width=True)
                    if temple.get('audio_url'):
                        st.audio(temple['audio_url'])
                    if temple.get('created_at'):
                        st.caption(f"🗓️ Uploaded on: {temple['created_at'].strftime('%Y-%m-%d') if hasattr(temple['created_at'], 'strftime') else str(temple['created_at'])[:10]}")
        else:
            st.info("📝 No temples uploaded yet. Be the first to contribute!")
    except Exception as e:
        st.error(f"Failed to fetch temples: {str(e)}")

    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit + Supabase")

if __name__ == "__main__":
    main()
