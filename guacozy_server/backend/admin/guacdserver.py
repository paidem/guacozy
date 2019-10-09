from django.contrib import admin

from backend.models import GuacdServer


@admin.register(GuacdServer)
class GuacdServerModelAdmin(admin.ModelAdmin):
    model = GuacdServer
    list_display = ['name', 'hostname', 'port']
