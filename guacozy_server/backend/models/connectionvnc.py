from django.db import models

from .connection import Connection


class ConnectionVnc(Connection):
    class Meta:
        verbose_name = "VNC Connection"
        verbose_name_plural = "VNC Connections"

    # Settings are explained here:
    # https://guacamole.apache.org/doc/gug/configuring-guacamole.html#vnc

    # Network parameters
    autoretry = models.IntegerField(default=10)

    # Display settings
    #
    # these could be also implemented later:
    # color_scheme
    # font_name

    color_depth = models.CharField(max_length=2,
                                   choices=[
                                       ('8', '8 bits'),
                                       ('16', '16 bits'),
                                       ('24', '24 bits'),
                                       ('32', '32 bits'),
                                   ],
                                   default='8')

    swap_red_blue = models.BooleanField(default=False)

    cursor_remote = models.BooleanField(default=False)

    read_only = models.BooleanField(default=False)

    # VNC Repeater
    repeater_dest_host = models.CharField(max_length=60, blank=True)
    repeater_dest_port = models.IntegerField(default=0)

    # Reverse connection
    reverse_connect = models.BooleanField(default=False)
    listen_timeout = models.IntegerField(default=5)

    # Clipboard encoding

    clipboard_encoding = models.CharField(max_length=16,
                                          choices=[('ISO8859-1', 'ISO8859-1'),
                                                   ('UTF-8', 'UTF-8'),
                                                   ('UTF-16', 'UTF-16'),
                                                   ('CP1252', 'CP1252'),
                                                   ],
                                          default='ISO8859-1'
                                          )

    def save(self, *args, **kwargs):
        self.protocol = 'vnc'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name + " (VNC)"

    # Update Guacamole connection parameters with SSH specific parameters
    def get_guacamole_parameters(self, user):
        parameters = super().get_guacamole_parameters(user=user)

        parameters["color_depth"] = self.color_depth.__str__()
        parameters["swap_red_blue"] = self.swap_red_blue.__str__().lower()

        if self.cursor_remote:
            parameters['cursor'] = "remote"

        parameters["read_only"] = self.read_only.__str__().lower()

        if self.repeater_dest_host:
            parameters['dest_host'] = self.repeater_dest_host

        if self.repeater_dest_port > 0:
            parameters['dest_port'] = self.repeater_dest_port

        if self.reverse_connect:
            parameters['reverse_connect'] = "true"
            parameters['listen_timeout'] = (self.listen_timeout * 1000).__str__()

        if self.clipboard_encoding != 'ISO8859-1':
            parameters['clipboard_encoding'] = self.clipboard_encoding

        return parameters
