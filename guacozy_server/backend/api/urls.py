from django.urls import include, path
from rest_framework import routers

from backend.models import Folder
from . import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'folders', views.FolderFlatViewSet, basename=Folder)

urlpatterns = [
    path('', include(router.urls)),

    # Returns hierarchical list of folders available to user
    path('folders/tree', views.folders_objects_treeview, {'include_objects': False}),

    # Returns list of connections available to user
    # in hierarchical folder structure
    path('connections/tree', views.folders_objects_treeview, {'include_objects': True}),
]
