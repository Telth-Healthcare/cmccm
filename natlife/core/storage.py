from django.core.files.storage import Storage
from supabase import create_client, Client
from django.conf import settings

from .services import CoreService

MEDIA_ROOT = getattr(settings, "MEDIA_ROOT")


# -------------------------
# SUPABASE STORAGE
# -------------------------
class SupabaseMediaStorage(Storage):
    config: dict = getattr(settings, "SUPABASE_CONFIG", {})

    def __init__(self):
        self.client: Client = create_client(
            self.config["SUPABASE_URL"],
            self.config["SUPABASE_KEY"]
        )

        self.bucket_exists = (
            self.client.storage.list_buckets() and
            self.config["SUPABASE_BUCKET"] in [b.name for b in self.client.storage.list_buckets()]
        )
        if not self.bucket_exists:
            self.client.storage.create_bucket(
                self.config["SUPABASE_BUCKET"],
                options={"public": True}
            )
            self.bucket = self.config["SUPABASE_BUCKET"]
        else:
            self.bucket = self.config["SUPABASE_BUCKET"]

    def _save(self, name, content):
        filename = f"{MEDIA_ROOT}{CoreService.create_uuid_filename(name)}"

        # Must read bytes
        file_bytes = content.read()

        res = self.client.storage.from_(self.bucket).upload(
            filename,
            file_bytes,
            {
                "content-type": getattr(content, "content_type", None)
            }
        )

        if res and isinstance(res, dict) and res.get("error"):
            raise Exception(res["error"]["message"])

        return filename

    def exists(self, name):
        """
        Django checks if filename already exists.
        Supabase `.list()` only lists top-level,
        but that's enough since we generate UUID file names.
        """
        try:
            files = self.client.storage.from_(self.bucket).list()
            return any(f["name"] == name for f in files)
        except Exception:
            return False

    def url(self, name):
        return self.client.storage.from_(self.bucket).get_public_url(name)
