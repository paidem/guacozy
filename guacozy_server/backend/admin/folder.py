from django.contrib import admin
from django.forms import BaseInlineFormSet
from django_mptt_admin.admin import DjangoMpttAdmin

from backend.models import FolderPermission, Folder


class FolderPermissionInline(admin.TabularInline):
    model = FolderPermission


class FolderInheritedPermissionInlineFormSet(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        super(FolderInheritedPermissionInlineFormSet, self).__init__(*args, **kwargs)
        # Get FolderPermission objects which reference any ancestor folders
        # .order_by('folder__lft') make use of MPTT lft to make them appear in same order as in tree
        instance = kwargs['instance']
        if instance.parent:
            ancestors = instance.parent.get_ancestors(include_self=True)
            self.queryset = FolderPermission.objects.filter(folder__in=ancestors).order_by('folder__lft')



class FolderInheritedPermissionInline(admin.TabularInline):
    model = FolderPermission
    extra = 0

    verbose_name_plural = 'Inherited permissions'

    fields = ['get_folderbc', 'group', 'user', ]
    readonly_fields = ['get_folderbc', ]

    def get_folderbc(self, obj):
        if obj.pk:
            return FolderPermission.objects.get(pk=obj.pk).folder.breadcrumbs
        else:
            return ""

    get_folderbc.short_description = "Defined in"
    get_folderbc.allow_tags = True

    formset = FolderInheritedPermissionInlineFormSet

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return list(super().get_fields(request, obj))


@admin.register(Folder)
class FolderModelAdmin(DjangoMpttAdmin):
    list_display = ['name', 'breadcrumbs']
    readonly_fields = ('breadcrumbs',)
    inlines = (
        FolderPermissionInline,
        FolderInheritedPermissionInline,
    )

    def render_change_form(self, request, context, *args, **kwargs):
        context['after_related_objects'] = "Hello there"
        return super(FolderModelAdmin, self).render_change_form(request, context, args, kwargs)
