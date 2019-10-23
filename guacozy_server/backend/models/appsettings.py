from django.db import models
from django.core.cache import cache
from django.db.models import QuerySet

from .guacdserver import GuacdServer


class AppSettingsQuerySet(QuerySet):
    # prevent deleting by queryset
    def delete(self):
        pass


class AppSettingsManager(models.Manager):
    def get_queryset(self):
        return AppSettingsQuerySet(self.model, using=self._db)


class AppSettings(models.Model):
    class Meta:
        verbose_name = 'Application Settings'
        verbose_name_plural = verbose_name

    objects = AppSettingsManager()

    default_guacd_server = models.ForeignKey(GuacdServer,
                                             blank=True,
                                             null=True,
                                             on_delete=models.SET_NULL)

    ignore_rdp_cert_by_default = models.BooleanField(blank=False, default=True)

    def __str__(self):
        return "Applications Settings"

    def set_cache(self):
        cache.set(self.__class__.__name__, self)

    def save(self, *args, **kwargs):
        self.pk = 1
        self.set_cache()
        super(AppSettings, self).save(*args, **kwargs)

    # prevent deleting one object
    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        if cache.get(cls.__name__) is None:
            obj, created = cls.objects.get_or_create(pk=1)
            if not created:
                obj.set_cache()
        return cache.get(cls.__name__)
