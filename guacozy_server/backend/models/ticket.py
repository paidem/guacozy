from datetime import timedelta
from django.db import models
from django.utils import timezone
from backend.models import Connection
import uuid

from users.models import User


class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    sessionid = models.UUIDField(blank=True, null=True)
    connection = models.ForeignKey(Connection, on_delete=models.CASCADE, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, related_name='user_of_tickets')
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, related_name='author_of_tickets')
    created = models.DateTimeField(auto_now_add=True, blank=False)

    # if ticket has been shared to other user, this is original ticket
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name="shared")

    # if this ticket is shared (has parent), controlled shows if input is accepted from the user
    # control = False means that this session is "read-only"
    control = models.BooleanField(default=True)

    # how long from "created" should this ticket be valid
    validityperiod = models.DurationField(default=timedelta(days=1), blank=False)

    def __str__(self):
        return self.connection.name + " / " + \
               self.author.__str__() + " -> " + self.user.username + " /  " + \
               self.created.__str__() + " / " + \
               self.validityperiod.__str__()

    """
    This method checks if ticket is still valid and returns True/False
    If the ticket is invalid, ticket is deleted.
    """

    def check_validity(self):
        if self.created + self.validityperiod < timezone.now():
            self.delete()
            return False
        return True
