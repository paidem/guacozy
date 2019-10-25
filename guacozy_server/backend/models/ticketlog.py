from django.db import models
from django.db.models import QuerySet
from ipware import get_client_ip
from .appsettings import AppSettings
from .guacdserver import GuacdServer
from .connection import Connection

from users.models import User


class TicketLog(models.Model):
    ip = models.GenericIPAddressField(unpack_ipv4=True, null=True)

    date = models.DateTimeField(auto_now_add=True)

    ticketid = models.UUIDField(null=True)

    action = models.CharField(max_length=20)

    # Specify if the ticket is shared
    shared = models.BooleanField(default=False)

    # Specify if the ticket session sould be controlled (not a read-only)
    control = models.BooleanField(default=True, verbose_name="Control")

    sessionid = models.UUIDField(blank=True, null=True)

    # Foreign key to connection.
    connection = models.ForeignKey(Connection,
                                   on_delete=models.DO_NOTHING,
                                   null=True,
                                   blank=True,
                                   db_constraint=False)

    # Connection may be deleted later, so preserve main info
    connection_name = models.CharField(max_length=60)
    connection_host = models.CharField(max_length=60)
    connection_port = models.IntegerField(default=0)
    connection_protocol = models.CharField(max_length=10)

    # Foreign key to user
    user = models.ForeignKey(User,
                             on_delete=models.DO_NOTHING,
                             null=True,
                             blank=True,
                             related_name='user_in_ticketlogs',
                             db_constraint=False)

    # User may be deleted later, so preserve username
    username = models.CharField(max_length=60, blank=True, null=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)

    # Foreign key to author of ticket
    author = models.ForeignKey(User,
                               on_delete=models.DO_NOTHING,
                               null=True,
                               blank=True,
                               related_name='author_in_ticketlogs',
                               db_constraint=False)

    # Author may be deleted later, so preserve username
    author_username = models.CharField(max_length=60, blank=True, null=True)
    author_full_name = models.CharField(max_length=100, blank=True, null=True)

    # guacd server
    guacdserver = models.ForeignKey(GuacdServer,
                                    on_delete=models.DO_NOTHING,
                                    null=True,
                                    blank=True,
                                    db_constraint=False)

    # guacdserver may be deleted later, so preserve info
    guacdserver_hostname = models.CharField(max_length=64, blank=False,
                                            default="localhost")

    guacdserver_port = models.PositiveIntegerField()

    def populate(self, ticket, action, ip):
        self.ip = ip
        self.ticketid = ticket.id

        self.action = action

        self.shared = ticket.parent is not None

        self.control = ticket.control

        if ticket.sessionid:
            self.sessionid = ticket.sessionid

        self.connection = ticket.connection

        if ticket.connection:
            self.connection_name = ticket.connection.name
            self.connection_host = ticket.connection.host
            self.connection_port = ticket.connection.port
            self.connection_protocol = ticket.connection.protocol

        self.user = ticket.user
        self.username = self.user.username
        self.full_name = self.user.get_full_name()

        self.author = ticket.author
        self.author_username = self.author.username
        self.author_full_name = self.author.get_full_name()

        if ticket.connection is not None and ticket.connection.guacdserver is not None:
            self.guacdserver = ticket.connection.guacdserver
        else:
            self.guacdserver = AppSettings.load().default_guacd_server

        if self.guacdserver is not None:
            self.guacdserver_hostname = self.guacdserver.hostname
            self.guacdserver_port = self.guacdserver.port

    @classmethod
    def addlog(cls, ticket, action, **kwargs):

        if 'request' in kwargs:
            ip, ip_routeable = get_client_ip(kwargs['request'], request_header_order=['X_FORWARDED_FOR', 'REMOTE_ADDR'])
        elif 'scope' in kwargs:
            ip = kwargs['scope']['client'][0]
        else:
            ip = None

        tl = cls()
        tl.populate(ticket, action, ip)
        tl.save()
