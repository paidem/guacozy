from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response

from backend.api.utils import user_allowed_folders, folder_to_object, user_allowed_folders_ids
from backend.models import Folder
from users.models import User
from .serializers import UserSerializer, FolderFlatSerializer


# Users


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def dispatch(self, request, *args, **kwargs):
        if kwargs.get('pk') == 'current' and request.user:
            kwargs['pk'] = request.user.pk
        return super(UserViewSet, self).dispatch(request, *args, **kwargs)


# Folders / Connections part


class FolderAccessPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in ["GET", 'HEAD', 'OPTIONS'] or request.user.is_staff:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in ["GET", 'HEAD', 'OPTIONS']:
            return True
        if obj.id in user_allowed_folders_ids(request.user):
            return True
        return False


class FolderFlatViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated & FolderAccessPermission]
    serializer_class = FolderFlatSerializer

    def get_queryset(self):
        return Folder.objects.filter(id__in=user_allowed_folders_ids(self.request.user))


@api_view(['GET'])
def folders_objects_treeview(request, include_objects=True):
    root_folders = Folder.objects.all().filter(parent=None)
    allowed_to_list_folders = user_allowed_folders(request.user)

    result = []

    for folder in root_folders:
        if folder in allowed_to_list_folders:
            result += [folder_to_object(folder, user=request.user,
                                     folders_allowed_to_list=allowed_to_list_folders,
                                     include_objects=include_objects)]

    return Response(result)
