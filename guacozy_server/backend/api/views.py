import rules
from django.db.models import F, Q
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError, ParseError
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rules.contrib.rest_framework import AutoPermissionViewSetMixin

from backend.api.utils import user_allowed_folders, folder_to_object, user_allowed_folders_ids
from backend.models import Folder, Ticket, Connection
from users.models import User
from .serializers import UserSerializer, FolderFlatSerializer, TicketSerializer, TicketReadSerializer, \
    ConnectionSerializer


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
        if request.method in ["GET", 'HEAD', 'OPTIONS', 'POST']:
            return True

        # Check that user has view permission to a parent if we want to show modification ui
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            if obj.id in user_allowed_folders_ids(request.user, require_view_permission=True):
                return True

        return False


class FolderFlatViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated & FolderAccessPermission]
    serializer_class = FolderFlatSerializer

    def get_queryset(self):
        return Folder.objects.filter(id__in=user_allowed_folders_ids(self.request.user))

    # Override to check that user can create folder only inside of folder where user has view permission
    def perform_create(self, serializer):
        if serializer.validated_data['parent'] not in user_allowed_folders_ids(self.request.user, require_view_permission=True):
            raise PermissionDenied(detail="You are not allowed to create folder here")
        super(FolderFlatViewSet, self).perform_create(serializer)

    # Override to check that user can only update folder if he has view permission to it
    def perform_update(self, serializer):
        allowed_to_view_folders = user_allowed_folders_ids(self.request.user, require_view_permission=True)
        allowed_to_view_folders_ids = user_allowed_folders_ids(self.request.user, require_view_permission=True)

        if serializer.instance.id not in allowed_to_view_folders_ids:
            raise PermissionDenied(detail="You are not allowed to update this folder")

        if serializer.validated_data['parent'].id not in allowed_to_view_folders_ids:
            raise PermissionDenied(detail="You are not allowed to move folder here")

        super(FolderFlatViewSet, self).perform_update(serializer)

    def perform_destroy(self, instance):
        if instance.id not in user_allowed_folders_ids(self.request.user, require_view_permission=True):
            raise PermissionDenied(detail="You are not delete this folder")
        super(FolderFlatViewSet, self).perform_destroy(instance)


@api_view(['GET'])
def folders_objects_treeview(request, include_objects=True):
    root_folders = Folder.objects.all().filter(parent=None)
    allowed_to_list = user_allowed_folders(request.user)

    result = []

    for folder in root_folders:
        if folder in allowed_to_list:
            result += [folder_to_object(folder=folder,
                                        user=request.user,
                                        allowed_to_list=allowed_to_list,
                                        include_objects=include_objects)]

    return Response(result)


class ConnectionViewSet(viewsets.ModelViewSet, AutoPermissionViewSetMixin):
    serializer_class = ConnectionSerializer

    # Limit queryset to only include connections located in allowed to view folders
    def get_queryset(self):
        allowed_to_view_folders = user_allowed_folders_ids(self.request.user, require_view_permission=True)
        return Connection.objects.filter(parent__in=allowed_to_view_folders)


# Ticket part


@api_view(['GET', 'POST'])
def duplicate_ticket_view(request, uuid):
    """
    Create duplicate of a given ticket (found by uuid) i
    The result is a new ticket, which has the same connection and validity_period
    Does not allow duplicating shared tickets.
    Does not allow to duplicate if you are not the author of ticket.

    """

    try:
        original_ticket = Ticket.objects.get(pk=uuid)

        # Raise exception if this ticket is a shared ticket
        if original_ticket.parent is not None:
            raise PermissionDenied(detail="This is a shared ticket and cannot be duplicated.")

        # Raise exception if this ticket's author is not request user
        if original_ticket.author != request.user:
            raise PermissionDenied(detail="You are not the author of ticket, you cannot duplicate it.")

        if request.method == 'GET':
            return Response("Ticket found. Use POST method to with empty body to duplicate.")

        ticket = Ticket.objects.create(
            author=request.user,
            user=request.user,
            connection=original_ticket.connection,
            validityperiod=original_ticket.validityperiod)

        return Response(TicketSerializer(ticket).data, status=status.HTTP_202_ACCEPTED)

    except Ticket.DoesNotExist:
        raise NotFound(detail="Ticket not found")


@api_view(['GET', 'POST'])
def share_ticket_view(request, uuid):
    """
    Shares given ticket (<uuid:uuid>) with user ("userid" param in request data)
    The result is a new ticket, which is linked to original ticket using "parent" property.

    """
    try:
        original_ticket = Ticket.objects.get(pk=uuid)

        # Raise exception if this ticket is a shared ticket
        if original_ticket.parent is not None:
            raise PermissionDenied(detail="This is a shared ticket and cannot be shared.")

        if request.method == 'GET':
            return Response("Ticket found. Use POST method")

        try:
            receiving_user = User.objects.get(pk=request.data['userid'])
        except User.DoesNotExist:
            raise NotFound("User {} not found".format(request.data['userid']))
        except KeyError:
            raise ParseError("'userid' argument not provided.")

        ticket = Ticket.objects.create(
            author=request.user,
            # receiving_user - User provided in request data, who gets
            # access to same session and can interact with session
            user=receiving_user,
            connection=original_ticket.connection,
            parent=original_ticket,
            validityperiod=original_ticket.validityperiod)

        return Response(TicketSerializer(ticket).data, status=status.HTTP_202_ACCEPTED)

    except Ticket.DoesNotExist:
        raise NotFound(detail="Ticket not found")


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    # Override perform_create to set author and user
    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            user=self.request.user,
        )

    # Override get_queryset to filter
    def get_queryset(self):

        # delete all invalid (old) tickets
        # this will delete all invalid tickets of all users
        super().get_queryset().filter(created__lt=timezone.now() - F('validityperiod')).delete()

        # get original QuerySet
        qs = super().get_queryset()

        # filter to include only tickets assigned to current user
        qs = qs.filter(Q(user=self.request.user) | Q(author=self.request.user))

        #  filter to include only tickets which are valid
        # disabling now as we have already deleted them before
        # leaving original version here for reference and in case delete()
        # will be removed
        # qs = qs.filter(created__gt=timezone.now() - F('validityperiod'))
        return qs

    # override create to return existing ticket if exists
    def create(self, request, *args, **kwargs):
        ticket_serializer = TicketSerializer(data=request.data)

        if not ticket_serializer.is_valid():
            raise ValidationError(ticket_serializer.errors)

        # Check that user is allowed to use this connection
        if ticket_serializer.validated_data['connection'].parent.id not in \
                user_allowed_folders_ids(request.user, require_view_permission=True):
            raise ValidationError("Wrong connection specified")

        try:
            existing_tickets = Ticket.objects.filter(
                connection=request.data['connection'],
                user=request.user,
                author=request.user).order_by('created')

            # check tickets validity period and return first valid ticket found
            for ticket in existing_tickets:
                if ticket.check_validity():
                    # return valid ticket
                    return Response(TicketSerializer(ticket).data, status=status.HTTP_202_ACCEPTED)

            # if there are no valid tickets
            raise Ticket.DoesNotExist

        except Ticket.DoesNotExist:
            self.perform_create(ticket_serializer)
            # ticket = Ticket.objects.create(serializer.data)
            headers = self.get_success_headers(ticket_serializer.data)

            # return new ticket
            return Response(ticket_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # Override get_serializer_class
    # on list/retrieve operation provide TicketReadSerializer which will have expanded details of connection
    # on other operations (e.g. create) use more simple serializer
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return TicketReadSerializer

        return TicketSerializer