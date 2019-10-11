from rest_framework import serializers

from backend.api.utils import user_allowed_folders_ids
from backend.models import Folder
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    @staticmethod
    def get_full_name(obj):
        return obj.first_name + " " + obj.last_name

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'groups', 'first_name',
                  'last_name', 'full_name', 'is_staff', 'is_superuser']


class UserShortSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    @staticmethod
    def get_full_name(obj):
        return obj.first_name + " " + obj.last_name

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name']


class FolderFlatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Folder
        fields = ['id', 'name', 'parent']

    def __init__(self, *args, **kwargs):
        super(FolderFlatSerializer, self).__init__(*args, **kwargs)

        try:
            user = kwargs['context']['request'].user

            # Limit folder
            allowed_folders = user_allowed_folders_ids(user)
            self.fields['parent'].queryset = Folder.objects.filter(id__in=allowed_folders)

        except KeyError:
            pass
