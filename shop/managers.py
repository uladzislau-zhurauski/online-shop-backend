from django.db import models


class AvailableManager(models.Manager):
    def get_queryset(self):
        return super(AvailableManager, self).get_queryset().filter(is_available=True)


class ModeratedManager(models.Manager):
    def get_queryset(self):
        return super(ModeratedManager, self).get_queryset().filter(is_moderated=True)
