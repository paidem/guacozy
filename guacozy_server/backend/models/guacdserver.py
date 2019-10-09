from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class GuacdServer(models.Model):
    class Meta:
        verbose_name = "Guacd Server"
        verbose_name_plural = "Guacd Servers"

    name = models.CharField(max_length=64, blank=False, unique=True,
                            default="guacd server")

    hostname = models.CharField(max_length=64, blank=False,
                                default="localhost")

    port = models.PositiveIntegerField(blank=False, default=4822,
                                       validators=[MinValueValidator(1),
                                                   MaxValueValidator(65535)])

    def __str__(self):
        return self.name
