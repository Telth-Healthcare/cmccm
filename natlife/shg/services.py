from .models import SHG


class SHGService:

    @staticmethod
    def get_shg(user):
        return SHG.objects.filter(user=user).first()
