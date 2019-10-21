from django.contrib import admin
from django.forms import ModelForm, PasswordInput, ModelChoiceField, TextInput
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin, PolymorphicChildModelFilter

from backend.models import Connection, ConnectionRdp, ConnectionVnc, Folder
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
            # VNC Specific
            'cursor_remote': 'If set, the mouse pointer will be rendered remotely, and the local position of the mouse pointer will be indicated by a small dot. A remote mouse cursor will feel slower than a local cursor, but may be necessary if the VNC server does not support sending the cursor image to the client.',
            'read_only': 'Whether this connection should be read-only. If set to "true", no input will be accepted on the connection at all. Users will only see the desktop and whatever other users using that same desktop are doing. ',
            'swap_red_blue': 'If the colors of your display appear wrong (blues appear orange or red, etc.), it may be that your VNC server is sending image data incorrectly, and the red and blue components of each color are swapped. If this is the case, set this parameter to "true" to work around the problem. This parameter is optional.',
            'repeater_dest_host': 'The destination host to request when connecting to a VNC proxy such as UltraVNC Repeater. This is only necessary if the VNC proxy in use requires the connecting user to specify which VNC server to connect to. If the VNC proxy automatically connects to a specific server, this parameter is not necessary.',
            'repeater_dest_port': 'The destination port to request when connecting to a VNC proxy such as UltraVNC Repeater. This is only necessary if the VNC proxy in use requires the connecting user to specify which VNC server to connect to. If the VNC proxy automatically connects to a specific server, this parameter is not necessary.',
            'reverse_connect': 'Whether reverse connection should be used. If set to "true", instead of connecting to a server at a given hostname and port, guacd will listen on the given port for inbound connections from a VNC server.',
            'listen_timeout': 'If reverse connection is in use, the maximum amount of time to wait for an inbound connection from a VNC server, in seconds.'

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


@admin.register(ConnectionVnc)
class ConnectionVncAdmin(ConnectionChildAdmin):
    base_model = ConnectionVnc

    fieldsets = (
        ('Base', {
            'classes': 'wide',
            'fields': ('parent', 'name', ('host', 'port'), 'guacdserver')
        }),
        ('Connection', {
            'fields': (
                ('password',
                 'autoretry',),
            )
        }),
        ('Display Settings', {
            'fields': (
                'color_depth',
                'swap_red_blue',
                'cursor_remote',
                'read_only',
            )
        }),
        ("VNC Repeater", {
            'classes': ('collapse',),
            'fields': (
                ('repeater_dest_host', 'repeater_dest_port')
            )
        }),
        ("Reverse Connect", {
            'classes': ('collapse',),
            'fields': (
                'reverse_connect',
                'listen_timeout',
            )
        }),
    )


@admin.register(Connection)
class ConnectionParentAdmin(PolymorphicParentModelAdmin):
    list_display = ('__str__', 'protocol', 'host', 'port')
    """ The parent model admin """
    base_model = Connection  # Optional, explicitly set here.
    child_models = (ConnectionRdp, ConnectionSsh, ConnectionVnc)
    list_filter = (PolymorphicChildModelFilter,)
