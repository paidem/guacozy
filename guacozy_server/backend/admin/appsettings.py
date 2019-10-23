from django.contrib import admin
from django.forms import ModelForm

from backend.models import AppSettings


class AppSettingsForm(ModelForm):
    class Meta:
        fields = '__all__'

        model = AppSettings

        help_texts = {
            'default_guacd_server':
                'guacd server which will be used if not overriden in Connection settings',
            'ignore_rdp_cert_by_default':
                'Default setting for "ignore_cert" field when creating RDP Connection in admin page',
        }


@admin.register(AppSettings)
class AppSettingsModelAdmin(admin.ModelAdmin):
    model = AppSettings

    form = AppSettingsForm

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
