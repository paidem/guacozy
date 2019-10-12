from django.urls import include, path
from rest_framework import routers

from backend.models import Folder, Connection
from . import views

router = routers.DefaultRouter()
router.register(r'connections', views.ConnectionViewSet, basename=Connection)
router.register(r'folders', views.FolderFlatViewSet, basename=Folder)
router.register(r'tickets', views.TicketViewSet)
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # Returns hierarchical list of folders available to user
    path('folders/tree', views.folders_objects_treeview, {'include_objects': False}),

    # Returns list of connections available to user
    # in hierarchical folder structure
    path('connections/tree', views.folders_objects_treeview, {'include_objects': True}),

    # duplicataes ticket with given uuid
    # sessian id will be new, it means it is a new guacd session for same user
    path('tickets/duplicate/<uuid:uuid>/', views.duplicate_ticket_view),

    # Shares ticket with given uuid with user
    # determined by "username" in POST data
    # this uses same guacd session, so it means "screen sharing"
    path('tickets/share/<uuid:uuid>/', views.share_ticket_view),

]
