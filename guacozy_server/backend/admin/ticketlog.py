from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django_admin_listfilter_dropdown.filters import DropdownFilter
from rules.contrib.admin import ObjectPermissionsModelAdmin

from backend.models import TicketLog, Connection
from users.models import User


@admin.register(TicketLog)
class TicketLogAdmin(ObjectPermissionsModelAdmin):
    # Move filter to sidebar
    change_list_template = "admin/change_list_filter_sidebar.html"

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return False

    def uri(self, obj):
        return "{}://{}:{}".format(obj.connection_protocol, obj.connection_host, obj.connection_port)

    def connection_link(self, obj):
        try:
            link = reverse("admin:backend_connection_change", args=[obj.connection.id])
            return format_html('<a href="?connection_name={}" title="Filter connection={}">{}</a>'
                               '&nbsp;&nbsp;&nbsp;'
                               '<a href="{}" title="Edit connection">\N{memo}</a>',
                               obj.connection.name,
                               obj.connection.name,
                               obj.connection.name,
                               link)
        except Connection.DoesNotExist:
            return format_html('<strike><a href="?connection_name={}" title="Filter connection={}">{}</a></strike>',
                               obj.connection_name,
                               obj.connection_name,
                               obj.connection_name,
                               )

    connection_link.short_description = "Connection"

    def user_link(self, obj):
        try:
            link = reverse("admin:users_user_change", args=[obj.user.id])
            return format_html('<a href="?username={}" title="Filter user={}">{}</a>'
                               '&nbsp;&nbsp;&nbsp;'
                               '<a href="{}" title="Edit user">\N{memo}</a>',
                               obj.user.username,
                               obj.user.username,
                               obj.user.username,
                               # obj.user.username if obj.author_username != obj.username else "self",
                               link,
                               )
        except User.DoesNotExist:
            return format_html('<strike><a href="?username={}" title="Filter user={}">{}</a></strike>',
                               obj.author_username,
                               obj.author_username,
                               obj.author_username,
                               # obj.username if obj.author_username != obj.username else "self",
                               )

    user_link.short_description = "Ticket User"

    def author_link(self, obj):
        try:
            link = reverse("admin:users_user_change", args=[obj.author.id])
            return format_html(
                '<a href="?author_username={}" title="Filter author={}">{}</a>'
                '&nbsp;&nbsp;&nbsp;'
                '<a href="{}" title="Edit user">\N{memo}</a>',
                obj.author.username,
                obj.author.username,
                obj.author.username,
                link,
            )
        except User.DoesNotExist:
            return format_html(
                '<strike><a href="?author_username={}" title="Filter author={}">{}</a></strike>',
                obj.author_username,
                obj.author_username,
                obj.author_username
            )

    author_link.short_description = "Ticket Author"

    def ticketid_short(self, obj):
        shortid = obj.ticketid.__str__()[0:8]
        return format_html('<a href="{}" title="Filter by ticket">{}</a>',
                           "?ticketid=" + obj.ticketid.__str__(), shortid)

    ticketid_short.short_description = "Ticket"

    def sessionid_short(self, obj):
        if obj.sessionid is not None:
            shortid = obj.sessionid.__str__()[0:8]
            return format_html('<a href="{}" title="Filter by session id">{}</a>',
                               "?sessionid=" + obj.sessionid.__str__(), shortid)
        return "None"

    sessionid_short.short_description = "Session"

    def ip_link(self, obj):
        return format_html('<a href="{}" title="Filter by IP">{}</a>', "?ip=" + obj.ip.__str__(), obj.ip)

    ip_link.short_description = "IP"

    # list_display = [field.name for field in TicketLog._meta.get_fields()]
    list_display = [
        'id',
        'ip_link',
        'date',
        'action',
        'author_link',
        'user_link',
        'connection_link',
        'uri',
        'ticketid_short',
        'sessionid_short',
        'shared',
        'control',
    ]

    # list_filter = (
    #     'action',
    # )

    list_filter = (
        'action',
        ('username', DropdownFilter),
        ('author_username', DropdownFilter),
        ('connection_name', DropdownFilter),
        ('shared', admin.BooleanFieldListFilter),
    )

    search_fields = ['username', 'full_name',
                     'author_username', 'author_full_name',
                     'connection_name', 'connection_host',
                     'ticketid', 'sessionid'
                     ]
    readonly_fields = [field.name for field in TicketLog._meta.get_fields()]
