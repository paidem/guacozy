from django.contrib import admin

from backend.models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    readonly_fields = ["uuid", "created", "sessionid", 'user', "author", 'parent']
    list_display = ('__str__', )

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        obj.user = request.user
        obj.save()
