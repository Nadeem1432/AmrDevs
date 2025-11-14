from supabase import create_client
from django.conf import settings
import os
from urllib.parse import unquote
from supabase import StorageException


class SupabaseCustomStorage:

    def __init__(self):
        self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.bucket = settings.SUPABASE_BUCKET
        

    def upload_file_to_supabase(self, file, bucket_name=None, folder_path=None, is_local_path=True):
        try:
            # If the file is provided as a local path, open it in binary mode
            if not bucket_name:
                bucket_name = self.bucket

            if is_local_path:
                with open(file, "rb") as f:
                    file_content = f.read()
                    file_name = os.path.basename(file)
            else:
                # If the file is provided from a form, use its content and name directly
                file_content = file.read()
                file_name = file.name

            # If a folder path is provided, prepend it to the file name
            if folder_path:
                file_name = f"{folder_path}/{file_name}"

            try:
                response = self.client.storage.from_(bucket_name).upload(file_name, file_content)
            except StorageException as e:
                print("file already exists, trying to overwrite it:", e)
                response = self.client.storage.from_(bucket_name).update(file_name, file_content)
                if not response or not hasattr(response, 'path'):
                    raise Exception("Upload failed or response is invalid")
                public_url = self.client.storage.from_(bucket_name).get_public_url(file_name)
                return public_url
            
            # Check if the upload was successful
            if not response or not hasattr(response, 'path'):
                raise Exception("Upload failed or response is invalid")
            
            # Ensure the bucket is public before generating the public URL
            self.client.storage.update_bucket(bucket_name, {"public": True})
            
            # Generate the public URL for the uploaded file
            public_url = self.client.storage.from_(bucket_name).get_public_url(file_name)
            return public_url
        except Exception as e:
            print("❌ File upload failed:", e)
            return None

    def delete_file_from_supabase(self, public_url):
        try:
            # Extract the bucket name and file name from the public URL
            parts = public_url.split("/")
            bucket_name = parts[7]
            file_name = '/'.join(parts[8:])
            
            # Decode the file name to handle URL-encoded characters
            file_name = unquote(file_name)
            
            # Delete the file from the specified bucket
            response = self.client.storage.from_(bucket_name).remove([file_name])
            
            # Check if the deletion was successful
            if not response or not isinstance(response, list) or len(response) == 0:
                raise Exception("Deletion failed or response is invalid")
            
            print(f"✅ File '{file_name}' deleted successfully from bucket '{bucket_name}'.")
            return True
        except Exception as e:
            print("❌ File deletion failed:", e)
            return False
        

# NOTE :  Example usage
# filepath = '/home/nadeem/Desktop/test.py'

# mngr = SupabaseCustomStorage()
# upload_file_to_supabase = mngr.upload_file_to_supabase(filepath,folder_path='checking')
# print(upload_file_to_supabase)
# uploded_file = 'https://oahmpwdnzwwunnwuwvla.supabase.co/storage/v1/object/public/amrdevs/checking/test.py'
# delete_file_from_supabase = mngr.delete_file_from_supabase(uploded_file)
# print(delete_file_from_supabase)
