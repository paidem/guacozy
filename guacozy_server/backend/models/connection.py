import uuid

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.decorators import classproperty
from model_utils.managers import InheritanceManager
from polymorphic.models import PolymorphicModel

from backend.common.dictionaries import ProtocolsDict
from .guacdserver import GuacdServer
from .folder import Folder


class Connection(PolymorphicModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Tree location setting
    parent = models.ForeignKey(Folder, blank=True, null=True,
                               on_delete=models.SET_NULL,
                               related_name='connections')

    # General settings
    name = models.CharField(blank=False, max_length=60)
    host = models.CharField(blank=False, max_length=60)
    port = models.IntegerField(null=True, blank=True)
    protocol = models.CharField(max_length=10, blank=True, default="n/a",
                                editable=False)

    guacdserver = models.ForeignKey(GuacdServer,
                                    blank=True,
                                    null=True,
                                    related_name="connections",
                                    on_delete=models.SET_NULL)
    # User login settings
    username = models.CharField(
        verbose_name="Username",
        max_length=50,
        blank=True,
        null=True)

    password = models.CharField(
        verbose_name="Password",
        max_length=50,
        blank=True,
        null=True)

    domain = models.CharField(
        verbose_name="Domain",
        max_length=50,
        blank=True,
        null=True)

    passthrough_credentials = models.BooleanField(
        verbose_name="Passthrough app login credentials",
        default=False)

    def uri(self):
        return self.name + " (" + self.protocol + "://" + self.host + ":" + \
               self.port.__str__() + ")"

    def __str__(self):
        return self.uri()

    # check if provided password is blank. If it is, save old password
    def save(self, *args, **kwargs):
        if not self.port:
            self.port = ProtocolsDict[self.protocol]['port']

        super(Connection, self).save(*args, **kwargs)

    def get_guacamole_parameters(self, user):
        parameters = {
            "protocol": self.protocol,
            "hostname": self.host,
            "port": self.port,
        }

        parameters["username"] = self.username \
            if self.username else ""
        parameters["password"] = self.password \
            if self.password else ""
        parameters["domain"] = self.domain \
            if self.domain else ""

        return parameters
