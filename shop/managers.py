from django.db import models


class AvailableManager(models.Manager):
    def get_queryset(self):
        return super(AvailableManager, self).get_queryset().filter(is_available=True)
