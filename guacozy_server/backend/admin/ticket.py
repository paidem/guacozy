from django.contrib import admin
from rules.contrib.admin import ObjectPermissionsModelAdmin

from backend.models import Ticket


@admin.register(Ticket)
class TicketAdmin(ObjectPermissionsModelAdmin):
    readonly_fields = ["created", "sessionid", 'user', "author", 'parent']
    list_display = ('__str__', )

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        obj.user = request.user
        obj.save()
