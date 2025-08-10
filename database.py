import pandas as pd
from datetime import datetime
import os
from sqlalchemy import create_engine, text
from utils.supabase_client import get_supabase_client
import uuid

def init_database():
    """Initialize the database connection"""
    try:
        engine = get_supabase_client()
        if not engine:
            return False
        
        # Test connection by querying existing tables
        with engine.connect() as conn:
            conn.execute(text("SELECT 1 FROM temples LIMIT 1"))
        
        return True
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False

def get_temple_count():
    """Get total number of temples"""
    try:
        engine = get_supabase_client()
        if not engine:
            return 0
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM temples")).fetchone()
            return result[0] if result else 0
    except:
        return 0

def get_contribution_count():
    """Get total number of contributions"""
    try:
        engine = get_supabase_client()
        if not engine:
            return 0
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM content_contributions")).fetchone()
            return result[0] if result else 0
    except:
        return 0

def get_recent_contributions(limit=5):
    """Get recent contributions"""
    try:
        engine = get_supabase_client()
        if not engine:
            return pd.DataFrame()
        
        query = text("""
            SELECT title, content_type, description, location_address, 
                   contributor_name, created_at
            FROM content_contributions 
            ORDER BY created_at DESC 
            LIMIT :limit
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query, {"limit": limit})
            return pd.DataFrame(result.fetchall(), columns=result.keys())
    except Exception as e:
        print(f"Error fetching recent contributions: {e}")
        return pd.DataFrame()

def insert_temple(name, description=None, location=None, image_url=None, audio_url=None, contributor_name=None):
    """Insert a new temple using the actual temples table schema"""
    try:
        engine = get_supabase_client()
        if not engine:
            return None
        
        with engine.connect() as conn:
            query = text("""
                INSERT INTO temples (id, name, description, location, image_url, audio_url, created_at)
                VALUES (:id, :name, :description, :location, :image_url, :audio_url, NOW())
                RETURNING id
            """)
            
            temple_id = str(uuid.uuid4())
            result = conn.execute(query, {
                "id": temple_id,
                "name": name,
                "description": description,
                "location": location,
                "image_url": image_url,
                "audio_url": audio_url
            })
            conn.commit()
            return temple_id
    except Exception as e:
        print(f"Error inserting temple: {e}")
        return None

def insert_content_contribution(title, content_type, description, file_url,
                               latitude, longitude, location_address, contributor_name):
    """Insert a new content contribution using the actual content_contributions table schema"""
    try:
        engine = get_supabase_client()
        if not engine:
            return None
        
        with engine.connect() as conn:
            query = text("""
                INSERT INTO content_contributions (title, content_type, description, 
                                                 file_url, latitude, longitude, 
                                                 location_address, contributor_name, created_at)
                VALUES (:title, :content_type, :description, :file_url,
                        :latitude, :longitude, :location_address, :contributor_name, NOW())
                RETURNING id
            """)
            
            result = conn.execute(query, {
                "title": title,
                "content_type": content_type,
                "description": description,
                "file_url": file_url,
                "latitude": latitude,
                "longitude": longitude,
                "location_address": location_address,
                "contributor_name": contributor_name
            })
            conn.commit()
            return result.fetchone()[0]
    except Exception as e:
        print(f"Error inserting contribution: {e}")
        return None

def insert_historical_event(temple_id, event_date, event_title, event_description,
                           latitude, longitude, contributor_name):
    """Insert a new historical event using the actual historical_events table schema"""
    try:
        engine = get_supabase_client()
        if not engine:
            return None
        
        with engine.connect() as conn:
            query = text("""
                INSERT INTO historical_events (temple_id, event_date, event_title, 
                                             event_description, latitude, longitude, 
                                             contributor_name, created_at)
                VALUES (:temple_id, :event_date, :event_title, :event_description,
                        :latitude, :longitude, :contributor_name, NOW())
                RETURNING id
            """)
            
            result = conn.execute(query, {
                "temple_id": temple_id,
                "event_date": event_date,
                "event_title": event_title,
                "event_description": event_description,
                "latitude": latitude,
                "longitude": longitude,
                "contributor_name": contributor_name
            })
            conn.commit()
            return result.fetchone()[0]
    except Exception as e:
        print(f"Error inserting historical event: {e}")
        return None

def insert_media_upload(temple_id, uploaded_by, file_type, file_url):
    """Insert a new media upload using the actual media_uploads table schema"""
    try:
        engine = get_supabase_client()
        if not engine:
            return None
        
        with engine.connect() as conn:
            query = text("""
                INSERT INTO media_uploads (id, temple_id, uploaded_by, file_type, file_url, uploaded_at)
                VALUES (:id, :temple_id, :uploaded_by, :file_type, :file_url, NOW())
                RETURNING id
            """)
            
            media_id = str(uuid.uuid4())
            result = conn.execute(query, {
                "id": media_id,
                "temple_id": temple_id,
                "uploaded_by": uploaded_by,
                "file_type": file_type,
                "file_url": file_url
            })
            conn.commit()
            return media_id
    except Exception as e:
        print(f"Error inserting media upload: {e}")
        return None

def get_all_temples():
    """Get all temples"""
    try:
        engine = get_supabase_client()
        if not engine:
            return pd.DataFrame()
        
        query = text("SELECT * FROM temples ORDER BY created_at DESC")
        
        with engine.connect() as conn:
            result = conn.execute(query)
            return pd.DataFrame(result.fetchall(), columns=result.keys())
    except Exception as e:
        print(f"Error fetching temples: {e}")
        return pd.DataFrame()

def get_all_contributions():
    """Get all content contributions"""
    try:
        engine = get_supabase_client()
        if not engine:
            return pd.DataFrame()
        
        query = text("SELECT * FROM content_contributions ORDER BY created_at DESC")
        
        with engine.connect() as conn:
            result = conn.execute(query)
            return pd.DataFrame(result.fetchall(), columns=result.keys())
    except Exception as e:
        print(f"Error fetching contributions: {e}")
        return pd.DataFrame()

def get_all_historical_events():
    """Get all historical events"""
    try:
        engine = get_supabase_client()
        if not engine:
            return pd.DataFrame()
        
        query = text("SELECT * FROM historical_events ORDER BY created_at DESC")
        
        with engine.connect() as conn:
            result = conn.execute(query)
            return pd.DataFrame(result.fetchall(), columns=result.keys())
    except Exception as e:
        print(f"Error fetching historical events: {e}")
        return pd.DataFrame()

def search_temples(search_term, architectural_style=None):
    """Search temples by name or other criteria"""
    try:
        engine = get_supabase_client()
        if not engine:
            return pd.DataFrame()
        
        where_clause = "WHERE name ILIKE :search_term OR description ILIKE :search_term OR location ILIKE :search_term"
        params = {"search_term": f"%{search_term}%"}
        
        query = text(f"""
            SELECT * FROM temples 
            {where_clause}
            ORDER BY created_at DESC
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query, params)
            return pd.DataFrame(result.fetchall(), columns=result.keys())
    except Exception as e:
        print(f"Error searching temples: {e}")
        return pd.DataFrame()

def get_temple_by_id(temple_id):
    """Get a specific temple by ID"""
    try:
        engine = get_supabase_client()
        if not engine:
            return None
        
        query = text("SELECT * FROM temples WHERE id = :temple_id")
        
        with engine.connect() as conn:
            result = conn.execute(query, {"temple_id": temple_id})
            return result.fetchone()
    except Exception as e:
        print(f"Error fetching temple: {e}")
        return None

def get_media_by_temple_id(temple_id):
    """Get all media for a specific temple"""
    try:
        engine = get_supabase_client()
        if not engine:
            return pd.DataFrame()
        
        query = text("SELECT * FROM media_uploads WHERE temple_id = :temple_id ORDER BY uploaded_at DESC")
        
        with engine.connect() as conn:
            result = conn.execute(query, {"temple_id": temple_id})
            return pd.DataFrame(result.fetchall(), columns=result.keys())
    except Exception as e:
        print(f"Error fetching media: {e}")
        return pd.DataFrame()
