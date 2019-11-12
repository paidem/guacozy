from django.db import models

from backend.common.dictionaries import RDPSecurityDict
from backend.common.utils import model_choices_from_dictionary
from .connection import Connection


class ConnectionRdp(Connection):
    class Meta:
        verbose_name = "RDP Connection"
        verbose_name_plural = "RDP Connections"

    # Guacamole connectin settings are explained here:
    # https://guacamole.apache.org/doc/gug/configuring-guacamole.html#rdp

    # Security
    ignore_cert = models.BooleanField(blank=False, default=False)
    security = models.CharField(
        max_length=10,
        choices=model_choices_from_dictionary(RDPSecurityDict),
        default='any'
    )
    disable_auth = models.BooleanField(blank=False, default=False)

    # Session settings
    console = models.BooleanField(blank=False, default=False)
    initial_program = models.CharField(max_length=255, blank=True, null=True)
    server_layout = models.CharField(max_length=12,
                                     blank=False,
                                     choices=[
                                         ('en-us-qwerty',
                                          'English (US) keyboard'),
                                         ('en-gb-qwerty',
                                          'English (UK) keyboard'),
                                         ('de-de-qwertz',
                                          'German keyboard (qwertz)'),
                                         ('fr-fr-azerty',
                                          'French keyboard (azerty)'),
                                         ('fr-ch-qwertz',
                                          'Swiss French keyboard (qwertz)'),
                                         ('it-it-qwerty',
                                          'Italian keyboard'),
                                         ('ja-jp-qwerty',
                                          'Japanese keyboard'),
                                         ('pt-br-qwerty',
                                          'Portuguese Brazilian keyboard'),
                                         ('es-es-qwerty',
                                          'Spanish keyboard'),
                                         ('sv-se-qwerty',
                                          'Swedish keyboard'),
                                         ('tr-tr-qwerty',
                                          'Turkish-Q keyboard'),
                                         ('failsafe', 'Failsafe')
                                     ],
                                     default='en-us-qwerty')

    # Display settings
    color_depth = models.CharField(max_length=2,
                                   choices=[
                                       ('8', '8 bits'),
                                       ('16', '16 bits'),
                                       ('24', '24 bits'),
                                   ],
                                   default='16')

    resize_method = models.CharField(max_length=20,
                                     choices=[
                                         ('reconnect', 'Reconnect'),
                                         ('display-update', 'Display Update')
                                     ],
                                     default='reconnect')

    def save(self, *args, **kwargs):
        self.protocol = 'rdp'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name + " (RDP)"

    # Update Guacamole connection parameters with RDP specific parameters
    def get_guacamole_parameters(self, user):
        parameters = super().get_guacamole_parameters(user=user)

        if not self.port:
            parameters["port"] = 3389

        # Network settings
        parameters["ignore_cert"] = self.ignore_cert.__str__().lower()
        parameters["security"] = self.security
        parameters["disable_auth"] = self.disable_auth.__str__().lower()

        # Session settings
        parameters["console"] = self.console.__str__().lower()
        parameters["initial_program"] = self.initial_program
        parameters["server_layout"] = self.server_layout

        # Display
        parameters["color_depth"] = self.color_depth
        parameters["resize_method"] = self.resize_method

        return parameters
