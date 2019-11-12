from django.contrib import admin
from django.forms import ModelForm, PasswordInput, ModelChoiceField, TextInput
from django.urls import reverse
from django.utils.html import format_html
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin, PolymorphicChildModelFilter

from backend.models import Connection, ConnectionRdp, ConnectionVnc, Folder, AppSettings
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
            'credentials': 'If selected, will override username, password, domain and host key / passphrase fields.',
            'private_key': 'Private RSA key to connect to host.',
            'passphrase': 'IF passphrase is used to protect private key enter it here.',
            'host_key': 'Server''s host key to verify host identity before connecting.',
            'guacdserver': 'Override default guacd server.',
            # RDP specific
            'server_layout': 'failsafe will work on any keyboard but has a problem with Ctrl key',
            'ignore_cert': 'Ignore server certificates.',
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

    def get_form(self, request, obj=None, **kwargs):
        form = super(ConnectionRdpAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['ignore_cert'].initial = AppSettings.load().ignore_rdp_cert_by_default
        return form


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
    # Move filter to sidebar
    change_list_template = "admin/change_list_filter_sidebar.html"

    def duplicate_connections(modeladmin, request, queryset):
        # Get instances of ConnectionSSH, ConnectionRDP instead of Connection
        qs = Connection.objects.get_real_instances(queryset)

        for connection in qs:
            # This is a polymorhic model, that's why we have to set both pk and id to None if we want to clone
            connection.pk = None
            connection.id = None

            # Queryset of connections, where name is similar to that we want
            similar_qs = Connection.objects.filter(name__icontains=connection.name)

            candidate_number = 0

            while True:
                candidate_number += 1
                candidate_name = "{} ({})".format(connection.name, candidate_number)
                # check if we have connection with that name
                if similar_qs.filter(name=candidate_name).count() == 0:
                    # nothing found, can use candidate name
                    break

            connection.name = candidate_name
            connection.save()

    actions = [duplicate_connections]

    ordering = ('name',)

    search_fields = ['name', 'host']

    # Add field "location" with breadcrumbs
    def location(self, obj):
        if obj.parent is not None:
            link = reverse("admin:backend_folder_change", args=[obj.parent.id])
            return format_html('<a href="{}" title="Edit folder">{}</a>',
                               link, obj.parent.breadcrumbs)
        else:
            return "n/a"

    # Sort by MPTT's lft when sorting by location. This will give order resembling tree.
    location.admin_order_field = 'parent__lft'

    # Override queryset to select related field "parent" to minimize queries to DB
    def get_queryset(self, request):
        return super(ConnectionParentAdmin, self).get_queryset(request).select_related('parent')

    list_display = ('name', 'uri', 'credentials', 'location',)

    """ The parent model admin """
    base_model = Connection  # Optional, explicitly set here.
    child_models = (ConnectionRdp, ConnectionSsh, ConnectionVnc)

    list_filter = (PolymorphicChildModelFilter,
                   ('credentials', RelatedDropdownFilter),
                   )
