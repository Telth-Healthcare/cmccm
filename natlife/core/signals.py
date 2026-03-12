from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.core.files.storage import default_storage


# -------------------------
# DELETE FILE WHEN OBJECT DELETED
# -------------------------
@receiver(post_delete)
def delete_file_on_model_delete(sender, instance, **kwargs):
    """
    Deletes Supabase file when model instance is deleted.
    Runs only if instance has a FileField/ImageField.
    """
    for field in instance._meta.fields:
        if field.get_internal_type() in ['FileField', 'ImageField']:
            file = getattr(instance, field.name)
            if file and file.name:
                default_storage.delete(file.name)


# -------------------------
# DELETE OLD FILE ON UPDATE
# -------------------------
@receiver(pre_save)
def delete_old_file_on_change(sender, instance, **kwargs):
    """
    Deletes the old file if a new one is uploaded to this field.
    """
    if not instance.pk:
        return  # new object, nothing to delete yet

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    for field in instance._meta.fields:
        if field.get_internal_type() in ['FileField', 'ImageField']:
            old_file = getattr(old_instance, field.name)
            new_file = getattr(instance, field.name)

            if old_file and old_file.name != (new_file.name if new_file else None):
                default_storage.delete(old_file.name)
