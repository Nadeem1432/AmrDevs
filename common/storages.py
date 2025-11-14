from django.core.files.storage import Storage
from supabase import create_client
import mimetypes
from django.conf import settings

class SupabaseStorage(Storage):
    def __init__(self):
        self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.bucket = settings.SUPABASE_BUCKET

    def _save(self, name, content):
        file_data = content.read()
        mime_type, _ = mimetypes.guess_type(name)
        self.client.storage.from_(self.bucket).upload(name, file_data, {"content-type": mime_type})
        return name

    def url(self, name):
        return f"{settings.SUPABASE_URL}/storage/v1/object/public/{self.bucket}/{name}"