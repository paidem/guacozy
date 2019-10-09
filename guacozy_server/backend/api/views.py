from rest_framework import viewsets

from users.models import User

from .serializers import UserSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def dispatch(self, request, *args, **kwargs):
        if kwargs.get('pk') == 'current' and request.user:
            kwargs['pk'] = request.user.pk
        return super(UserViewSet, self).dispatch(request, *args, **kwargs)
