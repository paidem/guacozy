from django.contrib import admin

from backend.models import AppSettings


@admin.register(AppSettings)
class AppSettingsModelAdmin(admin.ModelAdmin):
    model = AppSettings

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
