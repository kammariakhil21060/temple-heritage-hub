import os
import streamlit as st
from sqlalchemy import create_engine, text
from typing import Optional

def get_supabase_client():
    """
    Get Supabase connection using DATABASE_URL
    Returns database connection or None if failed
    """
    try:
        database_url = os.getenv("DATABASE_URL")
        
        if not database_url:
            st.error("DATABASE_URL environment variable not set. Please configure your Supabase connection.")
            st.info("""
            To set up Supabase connection:
            1. Go to the Supabase dashboard (https://supabase.com/dashboard/projects)
            2. Create a new project if you haven't already
            3. Once in the project page, click the "Connect" button on the top toolbar
            4. Copy URI value under "Connection string" -> "Transaction pooler"
            5. Replace [YOUR-PASSWORD] with the database password you set for the project
            6. Set the DATABASE_URL environment variable with this connection string
            """)
            return None
        
        # Test the connection
        engine = create_engine(database_url)
        
        # Test connection with a simple query
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
        - Make sure you're using the Transaction pooler connection string, not the Direct connection
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
        # This would require supabase-py library which we're avoiding
        # For file storage, we'll implement direct REST API calls
        storage_url = os.getenv("SUPABASE_URL", "").replace("/rest/v1", "")
        storage_key = os.getenv("SUPABASE_ANON_KEY", "")
        
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
