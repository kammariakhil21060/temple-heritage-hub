import os
import streamlit as st
from sqlalchemy import create_engine, text
from typing import Optional
from dotenv import load_dotenv
load_dotenv()
import urllib.parse

def get_supabase_client():
    """
    Get Supabase connection using DATABASE_URL
    Returns database connection or None if failed
    """
    try:
        # Try to get DATABASE_URL from environment variable first
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_password = os.getenv("SUPABASE_PASSWORD")
            if supabase_url and supabase_password:
                host = supabase_url.replace("https://", "").replace("http://", "")
                escaped_password = urllib.parse.quote_plus(supabase_password)
                database_url = f"postgresql://postgres:{escaped_password}@{host}:5432/postgres"
            else:
                st.error("DATABASE_URL or SUPABASE_PASSWORD environment variable not set.")
                return None
        # Test the connection
        engine = create_engine(database_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as e:
        st.error(f"Failed to connect to Supabase: {str(e)}")
        st.info("""
        Connection troubleshooting:
        - Ensure your DATABASE_URL is correctly formatted
        - Check that your Supabase project is active
        - Verify your database password is correct
        - Make sure you're using the correct connection string format
        """)
        return None

def test_supabase_connection() -> bool:
    """
    Test Supabase database connection
    Returns: True if connection successful, False otherwise
    """
    try:
        client = get_supabase_client()
        return client is not None
    except Exception:
        return False

def get_supabase_storage_client():
    """
    Get Supabase storage client for file operations
    Note: This requires the supabase-py library for storage operations
    For now, we'll use direct REST API calls
    """
    try:
        # Use the provided Supabase credentials
        storage_url = os.getenv("SUPABASE_URL", "https://rrbrghxzuzzxroqbwfqi.supabase.co")
        storage_key = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJyYnJnaHh6dXp6eHJvcWJ3ZnFpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM4MDU0OTMsImV4cCI6MjA2OTM4MTQ5M30.Evcf0lPD7reXvgZNZrAZDoHHLDx72AUmUHMSOXgQNV4")
        
        if not storage_url or not storage_key:
            st.warning("Supabase storage credentials not configured. File uploads will be disabled.")
            return None
        
        return {
            "url": storage_url,
            "key": storage_key
        }
    
    except Exception as e:
        st.error(f"Storage client error: {str(e)}")
        return None

def upload_file_to_storage(file_content: bytes, file_path: str, content_type: str) -> Optional[str]:
    """
    Upload file to Supabase storage using REST API
    Returns: Public URL of uploaded file or None if failed
    """
    try:
        import requests
        
        storage_config = get_supabase_storage_client()
        if not storage_config:
            return None
        
        bucket_name = "heritage-files"
        upload_url = f"{storage_config['url']}/storage/v1/object/{bucket_name}/{file_path}"
        
        headers = {
            "Authorization": f"Bearer {storage_config['key']}",
            "Content-Type": content_type,
            "x-upsert": "false"
        }
        
        response = requests.post(upload_url, data=file_content, headers=headers)
        
        if response.status_code == 200:
            # Get public URL
            public_url = f"{storage_config['url']}/storage/v1/object/public/{bucket_name}/{file_path}"
            return public_url
        else:
            st.error(f"Storage upload failed: {response.status_code} - {response.text}")
            return None
    
    except Exception as e:
        st.error(f"Storage upload error: {str(e)}")
        return None

def get_storage_file_url(file_path: str) -> Optional[str]:
    """
    Get public URL for a file in Supabase storage
    """
    try:
        storage_config = get_supabase_storage_client()
        if not storage_config:
            return None
        
        bucket_name = "heritage-files"
        public_url = f"{storage_config['url']}/storage/v1/object/public/{bucket_name}/{file_path}"
        return public_url
    
    except Exception as e:
        st.error(f"Error getting file URL: {str(e)}")
        return None

def create_storage_bucket(bucket_name: str) -> bool:
    """
    Create a storage bucket in Supabase
    Returns: True if successful, False otherwise
    """
    try:
        import requests
        
        storage_config = get_supabase_storage_client()
        if not storage_config:
            return False
        
        create_url = f"{storage_config['url']}/storage/v1/bucket"
        
        headers = {
            "Authorization": f"Bearer {storage_config['key']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "id": bucket_name,
            "name": bucket_name,
            "public": True
        }
        
        response = requests.post(create_url, json=data, headers=headers)
        
        if response.status_code in [200, 201]:
            return True
        elif response.status_code == 409:
            # Bucket already exists
            return True
        else:
            st.error(f"Bucket creation failed: {response.status_code} - {response.text}")
            return False
    
    except Exception as e:
        st.error(f"Bucket creation error: {str(e)}")
        return False

def get_database_info() -> dict:
    """
    Get information about the connected database
    """
    try:
        engine = get_supabase_client()
        if not engine:
            return {}
        
        info = {
            "connected": True,
            "database_url": os.getenv("DATABASE_URL", "").split("@")[-1] if os.getenv("DATABASE_URL") else "",
            "storage_configured": get_supabase_storage_client() is not None
        }
        
        return info
    
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
            "storage_configured": False
        }
