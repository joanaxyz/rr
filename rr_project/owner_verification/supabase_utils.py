from supabase import create_client
from django.conf import settings
import os

def get_supabase_client():
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

def upload_to_supabase(file_obj, bucket_name, file_path):
    try:
        client = get_supabase_client()
        file_data = file_obj.read()
        
        response = client.storage.from_(bucket_name).upload(
            file_path,
            file_data,
            {"contentType": file_obj.content_type}
        )
        
        public_url = client.storage.from_(bucket_name).get_public_url(file_path)
        return public_url
    except Exception as e:
        print(f"Supabase upload error: {e}")
        return None
