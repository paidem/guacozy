from backend.models import Connection

from users.models import User
from .models import Ticket, TicketLog
from django.db.models.signals import post_save, pre_save, pre_delete, post_delete
from django.dispatch import receiver


@receiver(post_save, sender=Ticket)
def log_ticket_created(sender, instance, created, **kwargs):
    if created:
        TicketLog.addlog(instance, "create")
    else:
        TicketLog.addlog(instance, "update")


@receiver(pre_delete, sender=Ticket)
def log_ticket_deleted(sender, instance, **kwargs):
    TicketLog.addlog(instance, "delete")
