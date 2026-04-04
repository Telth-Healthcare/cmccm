from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage

from .models import SHG, Document

import logging

logger = logging.getLogger(__name__)


def _delete_file(file_field):
    if not file_field or not file_field.name:
        return
    try:
        if default_storage.exists(file_field.name):
            default_storage.delete(file_field.name)
            logger.info(f"Deleted file: {file_field.name}")
        else:
            logger.warning(f"File not found in storage: {file_field.name}")
    except Exception as e:
        logger.error(f"Failed to delete file {file_field.name}: {e}")


@receiver(pre_delete, sender=SHG)
def delete_shg_documents_files(sender, instance, **kwargs):
    """Fires before SHG cascade-deletes its Documents."""
    for document in instance.documents.all():
        _delete_file(document.file)


@receiver(post_delete, sender=Document)
def delete_document_file(sender, instance, **kwargs):
    """Fires when a Document is deleted directly (not via cascade)."""
    _delete_file(instance.file)