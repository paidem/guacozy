from django.contrib.auth.models import Group, Permission
from django.core.management import BaseCommand

from backend import models

GROUPS_PERMISSIONS = {
    'ConnectionsAdmin': {
        models.StaticCredentials: ['add', 'change', 'delete', 'view'],
        models.NamedCredentials: ['add', 'change', 'delete', 'view'],
        models.PersonalNamedCredentials: ['add', 'change', 'delete', 'view'],
        models.Folder: ['add', 'change', 'delete', 'view'],
        models.FolderPermission: ['add', 'change', 'delete', 'view'],
        models.ConnectionRdp: ['add', 'change', 'delete', 'view'],
        models.ConnectionSsh: ['add', 'change', 'delete', 'view'],
        models.Connection: ['add', 'change', 'delete', 'view'],
        models.GuacdServer: ['add', 'change', 'delete', 'view'],
        models.AppSettings: ['view'],
    },
}


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = "Create default groups"

    def handle(self, *args, **options):
        # Loop groups
        for group_name in GROUPS_PERMISSIONS:

            # Get or create group
            group, created = Group.objects.get_or_create(name=group_name)

            if created:
                self.stdout.write("Created group {}".format(group.__str__()))

            # Loop models in group
            for model_cls in GROUPS_PERMISSIONS[group_name]:

                # Loop permissions in group/model
                for perm_index, perm_name in enumerate(GROUPS_PERMISSIONS[group_name][model_cls]):

                    # Generate permission name as Django would generate it
                    codename = perm_name + "_" + model_cls._meta.model_name

                    try:
                        # Find permission object and add to group
                        perm = Permission.objects.get(codename=codename)
                        group.permissions.add(perm)

                    except Permission.DoesNotExist:
                        self.stdout.write("{} permission not found".format(codename))
