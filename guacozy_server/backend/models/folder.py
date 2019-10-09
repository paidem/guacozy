from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import models
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from users.models import User


class FolderPermission(models.Model):
    folder = models.ForeignKey('Folder', blank=False, null=True,
                               on_delete=models.CASCADE)
    group = models.ForeignKey(Group, blank=True, null=True,
                              on_delete=models.CASCADE)
    user = models.ForeignKey(User, blank=True, null=True,
                             on_delete=models.CASCADE)

    def clean(self):
        super().clean()
        if self.group is None and self.user is None:
            raise ValidationError('Group or User has to be set')
        if self.group is not None and self.user is not None:
            raise ValidationError('Only one of Group or User can be set')


class Folder(MPTTModel):
    name = models.CharField(max_length=50, blank=False)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True,
                            blank=True, related_name='children')

    users = models.ManyToManyField(User, through=FolderPermission,
                                   through_fields=('folder', 'user'))
    groups = models.ManyToManyField(Group, through=FolderPermission,
                                    through_fields=('folder', 'group'))

    class MPTTMeta:
        order_insertion_by = ['name']

    @property
    def breadcrumbs(self):
        ancestors = self.get_ancestors(ascending=False, include_self=True)
        result = ""
        for a in ancestors:
            if result != '':
                result += " / "
            result += a.__str__()
        return result

    @property
    def shifted_str(self):
        ret = ""
        if self.get_level() > 0:
            ret = '\u2001' * self.get_level() + '\u2515'
        # for i in range [1, self.get_level()]:
        #     ret += "-"
        return ret + self.name

    def __str__(self):
        return self.name
