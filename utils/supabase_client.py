import os
import streamlit as st
from sqlalchemy import create_engine, text
from typing import Optional
from dotenv import load_dotenv
import urllib.parse
import requests

# Load environment variables from .env file if present
try:
    load_dotenv()
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")

# ----------------------- DATABASE CONNECTION ------------------------

def get_supabase_client():
    """
    Get Supabase database engine using SQLAlchemy.
    Returns: SQLAlchemy engine or None if failed.
    """
    try:
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL")
        
        if not database_url:
            st.error("DATABASE_URL environment variable not set.")
            return None

        # Create SQLAlchemy engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        return engine
    
    except Exception as e:
        st.error(f"❌ Database connection failed: {str(e)}")
        return None

def test_supabase_connection() -> bool:
    """
    Test if Supabase DB connection works.
    """
    try:
        return get_supabase_client() is not None
    except:
        return False

# ----------------------- STORAGE CONFIG ------------------------

def get_supabase_storage_client():
    """
    Load Supabase Storage config from environment.
    """
    try:
        storage_url = os.getenv("SUPABASE_URL")
        storage_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not storage_url or not storage_key:
            st.warning("Supabase storage credentials not found.")
            return None

        return {
            "url": storage_url,
            "key": storage_key
        }
    
    except Exception as e:
        st.error(f"⚠️ Storage config error: {str(e)}")
        return None

# ----------------------- FILE UPLOAD ------------------------

def upload_file_to_storage(file_content: bytes, file_path: str, content_type: str) -> Optional[str]:
    """
    Upload a file to Supabase Storage.
    Returns: Public URL of uploaded file or None.
    """
    try:
        config = get_supabase_storage_client()
        if not config:
            return None

        bucket = "heritage-files"
        upload_url = f"{config['url']}/storage/v1/object/{bucket}/{file_path}"

        headers = {
            "Authorization": f"Bearer {config['key']}",
            "Content-Type": content_type,
            "x-upsert": "false"
        }

        response = requests.post(upload_url, data=file_content, headers=headers)

        if response.status_code == 200:
            return f"{config['url']}/storage/v1/object/public/{bucket}/{file_path}"
        else:
            st.error(f"❌ Upload failed: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        st.error(f"❌ Upload error: {str(e)}")
        return None

def get_storage_file_url(file_path: str) -> Optional[str]:
    """
    Get public URL for file in Supabase Storage.
    """
    try:
        config = get_supabase_storage_client()
        if config:
            bucket = "heritage-files"
            return f"{config['url']}/storage/v1/object/public/{bucket}/{file_path}"
        return None
    
    except Exception as e:
        st.error(f"⚠️ Failed to get file URL: {str(e)}")
        return None

def create_storage_bucket(bucket_name: str = "heritage-files") -> bool:
    """
    Create a public storage bucket (optional).
    """
    try:
        config = get_supabase_storage_client()
        if not config:
            return False

        headers = {
            "Authorization": f"Bearer {config['key']}",
            "Content-Type": "application/json"
        }

        data = {
            "id": bucket_name,
            "name": bucket_name,
            "public": True
        }

        response = requests.post(f"{config['url']}/storage/v1/bucket", json=data, headers=headers)

        if response.status_code in [200, 201, 409]:  # 409 means already exists
            return True
        else:
            st.error(f"❌ Bucket creation failed: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        st.error(f"⚠️ Bucket error: {str(e)}")
        return False

# ----------------------- DB INFO ------------------------

def get_database_info() -> dict:
    """
    Return database and storage status for diagnostics.
    """
    try:
        engine = get_supabase_client()
        return {
            "connected": engine is not None,
            "database_url": os.getenv("DATABASE_URL", "").split("@")[-1] if os.getenv("DATABASE_URL") else "",
            "storage_configured": get_supabase_storage_client() is not None
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
            "storage_configured": False
        }
