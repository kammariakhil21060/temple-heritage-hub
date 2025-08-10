import streamlit as st
import os
import uuid
from datetime import datetime
import mimetypes
from typing import Optional
from io import BytesIO
from utils.supabase_client import get_supabase_storage_client, upload_file_to_storage
import requests

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

def upload_file_to_supabase(uploaded_file, content_type: str) -> Optional[str]:
    """
    Upload file to Supabase storage bucket
    Returns: Public URL of uploaded file or None if failed
    """
    try:
        # Validate file
        if not validate_file(uploaded_file, content_type):
            return None
        
        # Generate unique filename
        file_path = generate_unique_filename(uploaded_file.name, content_type)
        
        # Get file content
        file_content = uploaded_file.read()
        
        # Get content type
        content_type_mime = uploaded_file.type or mimetypes.guess_type(uploaded_file.name)[0] or 'application/octet-stream'
        
        # Upload to Supabase storage
        file_url = upload_file_to_storage(file_content, file_path, content_type_mime)
        
        if file_url:
            st.success(f"✅ File uploaded successfully!")
            return file_url
        else:
            st.error("❌ Failed to upload file to storage")
            return None
    
    except Exception as e:
        st.error(f"File upload error: {str(e)}")
        return None

def delete_file_from_supabase(file_path: str) -> bool:
    """
    Delete file from Supabase storage
    Returns: True if successful, False otherwise
    """
    try:
        config = get_supabase_storage_client()
        if not config:
            return False
        
        bucket = "heritage-files"
        delete_url = f"{config['url']}/storage/v1/object/{bucket}/{file_path}"
        
        headers = {
            "Authorization": f"Bearer {config['key']}"
        }
        
        response = requests.delete(delete_url, headers=headers)
        return response.status_code == 200
    
    except Exception as e:
        st.error(f"File deletion error: {str(e)}")
        return False

def get_file_info(file_path: str) -> Optional[dict]:
    """
    Get file information from Supabase storage
    Returns: Dictionary with file info or None if failed
    """
    try:
        config = get_supabase_storage_client()
        if not config:
            return None
        
        bucket = "heritage-files"
        info_url = f"{config['url']}/storage/v1/object/info/{bucket}/{file_path}"
        
        headers = {
            "Authorization": f"Bearer {config['key']}"
        }
        
        response = requests.get(info_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'name': data.get('name'),
                'size': data.get('metadata', {}).get('size'),
                'content_type': data.get('metadata', {}).get('mimetype'),
                'created_at': data.get('created_at'),
                'updated_at': data.get('updated_at')
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
        config = get_supabase_storage_client()
        if not config:
            return []
        
        bucket = "heritage-files"
        list_url = f"{config['url']}/storage/v1/object/list/{bucket}"
        
        headers = {
            "Authorization": f"Bearer {config['key']}"
        }
        
        params = {"prefix": prefix} if prefix else {}
        response = requests.get(list_url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            return []
    
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
