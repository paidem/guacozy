from django.contrib import admin
from django.forms import ModelForm, PasswordInput, ModelChoiceField, TextInput
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin, PolymorphicChildModelFilter

from backend.models import Connection, ConnectionRdp, Folder
from backend.models.connectionssh import ConnectionSsh


class FolderChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.shifted_str


class ConnectionChildForm(ModelForm):
    class Meta:
        fields = '__all__'

        model = Connection

        help_texts = {
            'port': 'If not specified, will use default port for selected protocol.',
            'ignore_cert': 'Ignore server certificates.',
            'credentials': 'If specified, will override username, password, domain and host key fields.',
            'private_key': 'Private RSA key to connect to host.',
            'passphrase': 'IF passphrase is used to protect private key enter it here.',
            'host_key': 'Server''s host key to verify host identity before connecting.',
            'guacdserver': 'Override default guacd server.',
        }

        widgets = {
            'name': TextInput(attrs={'autocomplete': 'off', 'data-lpignore': 'true'}),
            'username': TextInput(attrs={'autocomplete': 'off', 'data-lpignore': 'true'}),
            'domain': TextInput(attrs={'autocomplete': 'off', 'data-lpignore': 'true'}),
            'password': PasswordInput(attrs={'autocomplete': 'off', 'data-lpignore': 'true'}),
            'passphrase': TextInput(attrs={'autocomplete': 'off', 'data-lpignore': 'true'}),
        }


class ConnectionChildAdmin(PolymorphicChildModelAdmin):
    base_model = Connection
    base_form = ConnectionChildForm
    base_fieldsets = (
        ('Base', {
            'classes': 'wide',
            'fields': ('parent', 'name', ('host', 'port'), 'guacdserver')
        }),
        ('Authentication', {
            'fields': (
                'credentials',
                ('username',
                 'password',
                 'domain',
                 ),
                # 'credentials',
                'passthrough_credentials',
            )
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'parent':
            return FolderChoiceField(queryset=Folder.objects.all())
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(ConnectionRdp)
class ConnectionRdpAdmin(ConnectionChildAdmin):
    base_model = ConnectionRdp

    fieldsets = (
        ('Connection Security', {
            'classes': 'wide ',
            'fields': (
                'disable_auth',
                'security',
                'ignore_cert',

            )
        }),
        ('Connection Settings', {
            'classes': ('wide',),
            'fields': ('console',
                       'initial_program',
                       'server_layout',
                       'color_depth',
                       'resize_method'
                       ),
        })
    )

    def get_fieldsets(self, request, obj=None):
        parent_fieldsets = super(ConnectionChildAdmin, self).get_base_fieldsets(request, obj)
        return parent_fieldsets + self.fieldsets


@admin.register(ConnectionSsh)
class ConnectionSshAdmin(ConnectionChildAdmin):
    base_model = ConnectionSsh

    fieldsets = (
        ('PKI Authentication', {
            'fields': (
                ('private_key', 'passphrase',),
                'host_key',
            )
        }),
        ('Display settings', {
            'fields': (
                'font_size',
            )
        }),
        ("Other", {
            'fields': (
                'command',
            )
        }),
    )

    def get_fieldsets(self, request, obj=None):
        parent_fieldsets = super(ConnectionChildAdmin, self).get_base_fieldsets(request, obj)
        return parent_fieldsets + self.fieldsets


@admin.register(Connection)
class ConnectionParentAdmin(PolymorphicParentModelAdmin):
    list_display = ('__str__', 'protocol', 'host', 'port')
    """ The parent model admin """
    base_model = Connection  # Optional, explicitly set here.
    child_models = (ConnectionRdp, ConnectionSsh)
    list_filter = (PolymorphicChildModelFilter,)
