import uuid

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from encrypted_model_fields.fields import EncryptedCharField
from polymorphic.models import PolymorphicModel

from backend.common.dictionaries import ProtocolsDict
from .credentials import Credentials, StaticCredentials, NamedCredentials, PersonalNamedCredentials
from .folder import Folder
from .guacdserver import GuacdServer


class Connection(PolymorphicModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Tree location setting
    parent = models.ForeignKey(Folder, blank=True, null=True,
                               on_delete=models.SET_NULL,
                               related_name='connections')

    # General settings
    name = models.CharField(blank=False, unique=True, max_length=60)
    host = models.CharField(blank=False, max_length=60)
    port = models.IntegerField(null=True, blank=True)
    protocol = models.CharField(max_length=10, blank=True, default="n/a",
                                editable=False)

    credentials = models.ForeignKey(Credentials,
                                    verbose_name="Credentials",
                                    on_delete=models.SET_NULL,
                                    null=True,
                                    blank=True)

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

    password = EncryptedCharField(
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
        return self.protocol + "://" + self.host + ":" + self.port.__str__()

    def __str__(self):
        return "{} [{}]".format(self.name, self.uri())

    # save password as it was on load
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cred_password_original = self.password

    def save(self, *args, **kwargs):
        if not self.port:
            self.port = ProtocolsDict[self.protocol]['port']

        # check if provided password is blank. If it is, save old password
        if not self.password:
            self.password = self.cred_password_original

        super(Connection, self).save(*args, **kwargs)

    def get_guacamole_parameters(self, user):
        parameters = {
            "protocol": self.protocol,
            "hostname": self.host,
            "port": self.port,
        }

        parameters["username"] = parameters['password'] = parameters['domain'] = ""

        parameters["passthrough_credentials"] = self.passthrough_credentials

        # If connection is specified to use passthrough credentials - don't try to get credentials
        # guacdproxy will have to determine credentials from session
        if self.passthrough_credentials:
            # Domain should be specified in connection
            parameters['domain'] = self.domain if self.domain else ""
            return parameters

        credentials_object = self.get_credentials_object(user)

        if credentials_object is not None:
            parameters["username"] = credentials_object.username \
                if credentials_object.username else ""
            parameters["password"] = credentials_object.password \
                if credentials_object.password else ""
            parameters["domain"] = credentials_object.domain \
                if credentials_object.domain else ""
            parameters["private_key"] = credentials_object.private_key \
                if credentials_object.private_key else ""
            parameters["passphrase"] = credentials_object.passphrase \
                if credentials_object.passphrase else ""
        else:
            parameters["username"] = self.username \
                if self.username else ""
            parameters["password"] = self.password \
                if self.password else ""
            parameters["domain"] = self.domain \
                if self.domain else ""

        return parameters

    def get_credentials_object(self, user):
        if self.credentials is None:
            return None

        try:
            # Check if credentials is StaticCredentials. Return if it is
            static_credentials = StaticCredentials.objects.get(pk=self.credentials.pk)
            return static_credentials
        except ObjectDoesNotExist:
            pass

        try:
            # Then check if this is a NamedCredentials
            named_credentials = NamedCredentials.objects.get(pk=self.credentials.pk)
            # If it is NamedCredentials, we need user-specific instance
            named_credentials_instance = PersonalNamedCredentials.objects.get(reference=named_credentials,
                                                                              owner=user)
            return named_credentials_instance
        except (NamedCredentials.DoesNotExist, PersonalNamedCredentials.DoesNotExist):
            pass

        return None
