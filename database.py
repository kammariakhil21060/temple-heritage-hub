import sqlite3
import pandas as pd
from datetime import datetime
import os
from sqlalchemy import create_engine, text
from utils.supabase_client import get_supabase_client

def init_database():
    """Initialize the database with required tables"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return False
        
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            return False
        engine = create_engine(database_url)
        
        # Create tables if they don't exist
        with engine.connect() as conn:
            # Temples table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS temples (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    location_address TEXT,
                    latitude DECIMAL(10, 8),
                    longitude DECIMAL(11, 8),
                    deity VARCHAR(255),
                    architectural_style VARCHAR(255),
                    built_year INTEGER,
                    history TEXT,
                    contributor_name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Temple media table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS temple_media (
                    id SERIAL PRIMARY KEY,
                    temple_id INTEGER REFERENCES temples(id),
                    media_type VARCHAR(50),
                    filename VARCHAR(255),
                    file_url TEXT,
                    title VARCHAR(255),
                    description TEXT,
                    latitude DECIMAL(10, 8),
                    longitude DECIMAL(11, 8),
                    contributor_name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Historical events table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS historical_events (
                    id SERIAL PRIMARY KEY,
                    temple_id INTEGER REFERENCES temples(id),
                    event_date DATE,
                    event_title VARCHAR(255),
                    event_description TEXT,
                    latitude DECIMAL(10, 8),
                    longitude DECIMAL(11, 8),
                    contributor_name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Content contributions table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS content_contributions (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    content_type VARCHAR(50),
                    description TEXT,
                    file_url TEXT,
                    latitude DECIMAL(10, 8),
                    longitude DECIMAL(11, 8),
                    location_address TEXT,
                    contributor_name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            conn.commit()
        
        return True
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False

def get_temple_count():
    """Get total number of temples"""
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            return 0
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM temples")).fetchone()
            return result[0] if result else 0
    except:
        return 0

def get_contribution_count():
    """Get total number of contributions"""
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            return 0
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM content_contributions")).fetchone()
            return result[0] if result else 0
    except:
        return 0

def get_recent_contributions(limit=5):
    """Get recent contributions"""
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            return pd.DataFrame()
        engine = create_engine(database_url)
        query = text("""
            SELECT title, content_type, description, location_address, 
                   contributor_name, created_at
            FROM content_contributions 
            ORDER BY created_at DESC 
            LIMIT :limit
        """)
        return pd.read_sql(query, engine, params={"limit": limit})
    except Exception as e:
        print(f"Error fetching recent contributions: {e}")
        return pd.DataFrame()

def insert_temple(name, location_address, latitude, longitude, deity, 
                  architectural_style, built_year, history, contributor_name):
    """Insert a new temple"""
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            return None
        engine = create_engine(database_url)
        with engine.connect() as conn:
            query = text("""
                INSERT INTO temples (name, location_address, latitude, longitude, 
                                   deity, architectural_style, built_year, history, 
                                   contributor_name)
                VALUES (:name, :location_address, :latitude, :longitude, :deity,
                        :architectural_style, :built_year, :history, :contributor_name)
                RETURNING id
            """)
            result = conn.execute(query, {
                "name": name,
                "location_address": location_address,
                "latitude": latitude,
                "longitude": longitude,
                "deity": deity,
                "architectural_style": architectural_style,
                "built_year": built_year,
                "history": history,
                "contributor_name": contributor_name
            })
            conn.commit()
            return result.fetchone()[0]
    except Exception as e:
        print(f"Error inserting temple: {e}")
        return None

def insert_content_contribution(title, content_type, description, file_url,
                               latitude, longitude, location_address, contributor_name):
    """Insert a new content contribution"""
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            return None
        engine = create_engine(database_url)
        with engine.connect() as conn:
            query = text("""
                INSERT INTO content_contributions (title, content_type, description, 
                                                 file_url, latitude, longitude, 
                                                 location_address, contributor_name)
                VALUES (:title, :content_type, :description, :file_url,
                        :latitude, :longitude, :location_address, :contributor_name)
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

def get_all_temples():
    """Get all temples"""
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            return pd.DataFrame()
        engine = create_engine(database_url)
        query = text("""
            SELECT * FROM temples ORDER BY created_at DESC
        """)
        return pd.read_sql(query, engine)
    except Exception as e:
        print(f"Error fetching temples: {e}")
        return pd.DataFrame()

def get_all_contributions():
    """Get all content contributions"""
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            return pd.DataFrame()
        engine = create_engine(database_url)
        query = text("""
            SELECT * FROM content_contributions ORDER BY created_at DESC
        """)
        return pd.read_sql(query, engine)
    except Exception as e:
        print(f"Error fetching contributions: {e}")
        return pd.DataFrame()

def search_temples(search_term, architectural_style=None):
    """Search temples by name or other criteria"""
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            return pd.DataFrame()
        engine = create_engine(database_url)
        where_clause = "WHERE name ILIKE :search_term OR deity ILIKE :search_term OR location_address ILIKE :search_term"
        params = {"search_term": f"%{search_term}%"}
        
        if architectural_style:
            where_clause += " AND architectural_style = :style"
            params["style"] = architectural_style
        
        query = text(f"""
            SELECT * FROM temples 
            {where_clause}
            ORDER BY created_at DESC
        """)
        return pd.read_sql(query, engine, params=params)
    except Exception as e:
        print(f"Error searching temples: {e}")
        return pd.DataFrame()
