from django.utils import timezone
from rest_framework import serializers

from backend.api.utils import user_allowed_folders_ids
from backend.models import Folder, Ticket, Connection
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
        fields = ['id', 'username', 'first_name',
                  'last_name', 'full_name']


class FolderFlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ['id', 'name', 'parent']

    def __init__(self, *args, **kwargs):
        super(FolderFlatSerializer, self).__init__(*args, **kwargs)

        try:
            user = kwargs['context']['request'].user

            # Limit parent dropdown list in API browser
            # to folders user is allowed to view
            self.fields['parent'].queryset = Folder.objects \
                .filter(id__in=user_allowed_folders_ids(user, require_view_permission=True))
        except KeyError:
            pass


class ConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connection
        fields = ['id', 'name', 'parent', 'protocol']
        read_only_fields = ['id', 'name', 'protocol']


class TicketSerializer(serializers.ModelSerializer):
    validto = serializers.SerializerMethodField()

    @staticmethod
    def get_validto(obj):
        validtime = obj.created + obj.validityperiod
        return timezone.localtime(validtime)

    class Meta:
        model = Ticket
        fields = ['id', 'created', 'user', 'author', 'validto',
                  'connection', 'validityperiod', 'parent', 'control']
        read_only_fields = ['created', 'user', 'author', 'validto',
                            'parent']

    def __init__(self, *args, **kwargs):
        super(TicketSerializer, self).__init__(*args, **kwargs)

        try:
            user = kwargs['context']['request'].user

            # Limit connection dropdown list in API browser
            # to connections user is allowed to view
            self.fields['connection'].queryset = Connection.objects \
                .filter(parent__in=user_allowed_folders_ids(user, require_view_permission=True))
        except KeyError:
            pass


class TicketReadSerializer(TicketSerializer):
    user = UserShortSerializer()
    author = UserShortSerializer()
    connection = serializers.SerializerMethodField()

    @staticmethod
    def get_connection(obj):
        return {'id': obj.connection.id, 'name': obj.connection.name,
                'protocol': obj.connection.protocol}
