from django.core.management import BaseCommand

from backend import models

default_guacd_server_name = "guacd docker"
default_guacd_server_hostname = "guacd"
default_guacd_server_port = 4822


class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = "Create default guacd server"

    def handle(self, *args, **options):
        # Get or create default GuacdServer
        guacd_server, created = models.GuacdServer.objects \
            .get_or_create(name=default_guacd_server_name)

        self.stdout.write("\nChecking if we need to create '{}'."
                          .format(default_guacd_server_name))

        if created:
            self.stdout.write("'{}' not found, creating new with parameter:"
                              .format(default_guacd_server_name))
            self.stdout.write("name     = {}"
                              .format(default_guacd_server_name))
            self.stdout.write("hostname = {}"
                              .format(default_guacd_server_hostname))
            self.stdout.write("port     = {}"
                              .format(default_guacd_server_port.__str__()))
            guacd_server.hostname = default_guacd_server_hostname
            guacd_server.port = default_guacd_server_port
            guacd_server.save()
        else:
            self.stdout.write("'{}' exists. Skipping."
                              .format(default_guacd_server_name))

        # Load AppSettings (will be created if doesn't exist)
        app_settings = models.AppSettings.load()

        self.stdout.write("\nChecking if default Guacd server is set.")

        if app_settings.default_guacd_server is None:
            self.stdout.write("Default guacd not set. Setting to '{}'"
                              .format(guacd_server.name))
            app_settings.default_guacd_server = guacd_server
            app_settings.save()
        else:
            self.stdout.write("Default guacd is already set ('{}'). Skipping."
                              .format(app_settings.default_guacd_server.name))
