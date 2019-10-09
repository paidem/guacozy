from django.contrib import admin
from django_mptt_admin.admin import DjangoMpttAdmin

from backend.models import FolderPermission, Folder


class FolderPermissionInline(admin.TabularInline):
    model = FolderPermission


@admin.register(Folder)
class FolderModelAdmin(DjangoMpttAdmin):
    list_display = ['name', 'breadcrumbs']
    readonly_fields = ('breadcrumbs',)
    inlines = (
        FolderPermissionInline,
    )
