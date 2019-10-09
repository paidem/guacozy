from django.db import models

from .connection import Connection


class ConnectionSsh(Connection):
    class Meta:
        verbose_name = "SSH Connection"
        verbose_name_plural = "SSH Connections"

    # Settings are explained here:
    # https://guacamole.apache.org/doc/gug/configuring-guacamole.html#ssh

    # Network parameters

    # Host Key to check servers identity
    host_key = models.TextField(verbose_name="Host Key", blank=True)

    # SSH Keepalive interval. By default not used.
    server_alive_interval = models.IntegerField(
        verbose_name="Keepalive interval", null=False, default=0)

    # Authentication
    # Private key for users identity
    private_key = models.TextField(verbose_name="Private Key", blank=True,
                                   null=True)

    # Passprhase do decode private key
    passphrase = models.CharField(max_length=100, blank=True, null=True)

    # Display settings
    #
    # these could be also implemented later:
    # color_scheme
    # font_name

    font_size = models.IntegerField(default=8, blank=True)

    # other

    # Command to run instead of default shell
    command = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.protocol = 'ssh'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name + " (SSH)"

    # Update Guacamole connection parameters with SSH specific parameters
    def get_guacamole_parameters(self, user):
        parameters = super().get_guacamole_parameters(user=user)

        parameters["font_size"] = self.font_size

        if self.command:
            parameters["command"] = self.command

        # check if private_key and passphrase were provided from superclass
        # if not, try to add them from connections
        if 'private_key' not in parameters:
            parameters['private_key'] = self.private_key if self.private_key else ""

        if 'passphrase' not in parameters:
            parameters['passphrase'] = self.passphrase if self.passphrase else ""

        # this is needed so servers do not see us as "dumb terminal"
        # by default "linux" is sent
        parameters['terminal_type'] = 'xterm'

        # becaus we are hax0rs
        # parameters['color_scheme'] = 'green-black'
        parameters['color_scheme'] = \
            'foreground: rgb:FF/D7/00; background: rgb:30/30/30;'

        return parameters
