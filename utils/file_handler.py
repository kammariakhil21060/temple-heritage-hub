import streamlit as st
import os
import uuid
from datetime import datetime
import mimetypes
from typing import Optional
from io import BytesIO
from supabase import create_client, Client

def get_file_type(filename: str) -> str:
    """
    Determine file type based on extension
    """
    extension = filename.lower().split('.')[-1] if '.' in filename else ''
    
    image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']
    audio_extensions = ['mp3', 'wav', 'm4a', 'ogg', 'flac', 'aac']
    document_extensions = ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt']
    
    if extension in image_extensions:
        return 'image'
    elif extension in audio_extensions:
        return 'audio'
    elif extension in document_extensions:
        return 'document'
    else:
        return 'unknown'

def validate_file(uploaded_file, content_type: str) -> bool:
    """
    Validate uploaded file based on content type and size
    """
    if not uploaded_file:
        return False
    
    # Check file size (max 50MB)
    max_size = 50 * 1024 * 1024  # 50MB in bytes
    if uploaded_file.size > max_size:
        st.error(f"File size ({uploaded_file.size / 1024 / 1024:.1f}MB) exceeds maximum allowed size (50MB)")
        return False
    
    # Check file type
    file_type = get_file_type(uploaded_file.name)
    
    expected_types = {
        'Photo/Image': 'image',
        'Audio Recording': 'audio',
        'Document': 'document'
    }
    
    expected_type = expected_types.get(content_type, 'unknown')
    
    if expected_type != 'unknown' and file_type != expected_type:
        st.error(f"File type mismatch. Expected {expected_type} file for {content_type}")
        return False
    
    return True

def generate_unique_filename(original_filename: str, content_type: str) -> str:
    """
    Generate a unique filename to avoid conflicts
    """
    # Get file extension
    extension = original_filename.split('.')[-1] if '.' in original_filename else ''
    
    # Generate unique identifier
    unique_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Clean content type for folder structure
    content_folder = content_type.lower().replace('/', '_').replace(' ', '_')
    
    # Create new filename
    base_name = original_filename.rsplit('.', 1)[0] if '.' in original_filename else original_filename
    safe_base_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    
    if extension:
        new_filename = f"{content_folder}/{timestamp}_{unique_id}_{safe_base_name}.{extension}"
    else:
        new_filename = f"{content_folder}/{timestamp}_{unique_id}_{safe_base_name}"
    
    return new_filename

def get_supabase_storage_client() -> Optional[Client]:
    """Get Supabase client for storage operations"""
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            return None
        
        # Extract Supabase URL and create storage client
        # DATABASE_URL format: postgresql://postgres:[password]@db.[ref].supabase.co:6543/postgres
        if "supabase.co" in database_url:
            # Extract the project reference from the database URL
            parts = database_url.split("@db.")[1].split(".supabase.co")[0]
            supabase_url = f"https://{parts}.supabase.co"
            
            # For now, we'll use a placeholder key - this would need to be configured
            # In a real deployment, you'd need SUPABASE_ANON_KEY
            supabase_key = "placeholder"  # This needs to be properly configured
            
            return create_client(supabase_url, supabase_key)
        
        return None
    except Exception as e:
        st.error(f"Error creating Supabase storage client: {str(e)}")
        return None

def upload_file_to_supabase(uploaded_file, content_type: str) -> Optional[str]:
    """
    Upload file to Supabase storage bucket
    Returns: Public URL of uploaded file or None if failed
    """
    try:
        # Validate file
        if not validate_file(uploaded_file, content_type):
            return None
        
        # For now, we'll disable file storage since it requires additional Supabase configuration
        # In a real deployment, you would configure SUPABASE_URL and SUPABASE_ANON_KEY
        st.warning("File storage is not configured. Files cannot be uploaded at this time.")
        st.info("To enable file uploads, you would need to configure Supabase storage with proper API keys.")
        
        # Return a placeholder URL to allow the rest of the application to function
        return f"placeholder://file/{uploaded_file.name}"
    
    except Exception as e:
        st.error(f"File upload error: {str(e)}")
        return None

def delete_file_from_supabase(file_path: str) -> bool:
    """
    Delete file from Supabase storage
    Returns: True if successful, False otherwise
    """
    try:
        supabase = get_supabase_client()
        if not supabase:
            return False
        
        bucket_name = "heritage-files"
        
        result = supabase.storage.from_(bucket_name).remove([file_path])
        return result is not None
    
    except Exception as e:
        st.error(f"File deletion error: {str(e)}")
        return False

def get_file_info(file_path: str) -> Optional[dict]:
    """
    Get file information from Supabase storage
    Returns: Dictionary with file info or None if failed
    """
    try:
        supabase = get_supabase_client()
        if not supabase:
            return None
        
        bucket_name = "heritage-files"
        
        # Get file metadata
        result = supabase.storage.from_(bucket_name).info(file_path)
        
        if result:
            return {
                'name': result.get('name'),
                'size': result.get('metadata', {}).get('size'),
                'content_type': result.get('metadata', {}).get('mimetype'),
                'created_at': result.get('created_at'),
                'updated_at': result.get('updated_at')
            }
    
    except Exception as e:
        st.error(f"Error getting file info: {str(e)}")
    
    return None

def list_files_in_bucket(prefix: str = "") -> list:
    """
    List files in Supabase storage bucket
    Returns: List of file objects
    """
    try:
        supabase = get_supabase_client()
        if not supabase:
            return []
        
        bucket_name = "heritage-files"
        
        result = supabase.storage.from_(bucket_name).list(prefix)
        return result if result else []
    
    except Exception as e:
        st.error(f"Error listing files: {str(e)}")
        return []

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"

def is_image_file(filename: str) -> bool:
    """
    Check if file is an image based on extension
    """
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
    return any(filename.lower().endswith(ext) for ext in image_extensions)

def is_audio_file(filename: str) -> bool:
    """
    Check if file is an audio file based on extension
    """
    audio_extensions = ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac']
    return any(filename.lower().endswith(ext) for ext in audio_extensions)

def is_document_file(filename: str) -> bool:
    """
    Check if file is a document based on extension
    """
    document_extensions = ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt']
    return any(filename.lower().endswith(ext) for ext in document_extensions)
