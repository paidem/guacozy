import asyncio
import uuid
from urllib.parse import parse_qsl

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from guacamole.client import GuacamoleClient
from guacamole.exceptions import GuacamoleError
from guacamole.instruction import GuacamoleInstruction

from backend.models import Ticket, Connection, AppSettings, TicketLog


class GuacamoleConsumer(AsyncWebsocketConsumer):
    gclient = None
    ticket = None
    allow_control = False

    async def connect(self):
        """
        Handles Websocket connect event
        Given ticket uuid should 
        - initiate connection with guacd using parameters from ticket's connection
        - accept websocket connection and start infinite polling loop proxying guacamole instructions between
          browser guacamole client ant guacd server 
        """

        # check if client indicated 'guacamole' as supported subprotocols
        if 'guacamole' not in self.scope['subprotocols']:
            await self.close()
            return

        params = {'audio': []}

        parsed_query = parse_qsl(self.scope["query_string"].decode('utf8'))

        for p in parsed_query:
            if p[0] == 'width':
                params['width'] = p[1]
            if p[0] == 'height':
                params['height'] = p[1]
            if p[0] == 'audio':
                params['audio'] = [p[1]]

        try:
            ticket = await database_sync_to_async(Ticket.objects.get)(id=self.scope["url_route"]["kwargs"]["ticket"])
            self.allow_control = ticket.control
        except Ticket.DoesNotExist:
            # https://guacamole.apache.org/doc/gug/protocol-reference.html#status-codes
            # 771	CLIENT_FORBIDDEN
            # Permission was denied, and logging in will not solve the problem.
            await self.accept_and_send_error("Ticket does not exist", 771)
            return

        # check that user is the proper owner of ticket
        if ticket.user != self.scope['user']:
            # https://guacamole.apache.org/doc/gug/protocol-reference.html#status-codes
            # 771	CLIENT_FORBIDDEN
            # Permission was denied, and logging in will not solve the problem.
            await self.accept_and_send_error("You are not allowed to use this ticket", 771)
            return

        # check ticket validity and do not proceed if it is not valid
        if not ticket.check_validity():
            # https://guacamole.apache.org/doc/gug/protocol-reference.html#status-codes
            # 523	SESSION_CLOSED
            # The session within the upstream server has been forcibly closed.
            await self.accept_and_send_error("Ticket is no longer valid", 523)
            return

        sessionid = await self.get_ticket_sessionid(ticket)

        connection = await self.get_ticket_connection(ticket)

        # Try getting guacd server from connection
        guacd = connection.guacdserver

        # If connection has no guacd specified, try default
        if guacd is None:
            guacd = await self.get_default_guacd_server()

        if guacd is None:
            await self.accept_and_send_error(
                "Connection has no guacd server specified "
                "and no default guacd server specified in app settings", 512)
            return None

        self.gclient = GuacamoleClient(guacd.hostname, guacd.port)

        # Check if ticket has session id.
        # This means that session is already in progress and we connect to it
        if sessionid:
            try:
                await sync_to_async(self.gclient.handshake)(connectionid="$" + sessionid.__str__(), **params)
            except (AttributeError, GuacamoleError):
                # connection to existing sessioni failed
                # reset existing sessionid in ticket
                await self.update_ticket_sessionid(ticket, None)

        # If no existing session in progress (or reconnecting to it failed,
        # indicating as setting None above) we can try creating a new one
        sessionid = await self.get_ticket_sessionid(ticket)

        if not sessionid:
            # parameters = ticket.connection.get_guacamole_parameters()
            parameters = Connection.objects.get(
                pk=ticket.connection.pk).get_guacamole_parameters(
                self.scope['user'])

            if parameters['passthrough_credentials']:
                try:
                    parameters['username'] = self.scope['session']['username']
                    parameters['password'] = self.scope['session']['password']
                except KeyError:
                    await self.accept_and_send_error(
                        "Exception! Username/passord not found in session.\n. "
                        , 999)

            if parameters['protocol'] == 'rdp' \
                    and (not parameters['password'] or not parameters['username']) \
                    and parameters['security'] not in ['rdp', 'tls']:
                await self.accept_and_send_error(
                    "No credentials found for this connection \n. "
                    "If you want to use RDP login screen, "
                    "please explicitly specify security as RDP or TLS", 999)

            await sync_to_async(self.gclient.handshake)(**parameters, **params)
            await self.update_ticket_sessionid(ticket, self.gclient.id)

        #  If we have successfully connected,
        #  Guacamole Client should have an instance id
        if not self.gclient.id:
            await self.close()
            return

        # Save ticket reference (so we can update on disconnect) and log event
        self.ticket = ticket
        await self.log_ticket_action(ticket, 'connect', self.scope)

        # start polling loop function,
        asyncio.create_task(self.data_polling())

        # After we finish handshake and initiated polling loop
        # we accept connection
        await self.accept(subprotocol='guacamole')

    async def disconnect(self, code):
        """
        Websocket disconnect event handler, which closes session with guacd on  websocket disconnect
        """
        # socket disconnected - inform server that we are out
        await self.log_ticket_action(self.ticket, 'disconnect', self.scope)
        await sync_to_async(self.gclient.close)()

    async def accept_and_send_error(self, error_text, error_code):
        """
        Handle errors during connect with a reason and code
        In order for client side guacamole client to receive error code/text
        we need to accept connection and immediately send error instruction
        """
        await self.accept(subprotocol='guacamole')
        await self.send(text_data=GuacamoleInstruction("error", error_text,
                                                       error_code).encode())

    async def receive(self, text_data=None, bytes_data=None):
        """
        Webscocket receive even handler - send everything to associated guacd session
        """
        if self.allow_control is False and (text_data[0:7] == "5.mouse" or text_data[0:5] == "3.key"):
            return
        if text_data is not None:
            await sync_to_async(self.gclient.send)(text_data)

    async def data_polling(self):
        """
        Polling loop - receives data from GuacamoleClient and passes to websocket
        """
        while True:
            content = await sync_to_async(self.gclient.receive)()
            if content:
                # this is dirty workaround for problem.
                # If we reconnect, servers sends layer size 0x0
                # after this it sends normal size, but this causes
                # GuacamoleClient to update redraw "olddata"
                # which has become for a moment 0x0. Ant this causes
                #
                # Uncaught DOMException:
                # Failed to execute 'drawImage' on 'CanvasRenderingContext2D':
                #
                # The image argument is a canvas element with a width or
                # height of 0. so if content is "Set size of layer 1 to 0x0"
                # we just skip this command.
                if content == "4.size,1.1,1.0,1.0;":
                    continue
                await self.send(text_data=content)

    @database_sync_to_async
    def update_ticket_sessionid(self, ticket, sessionid):
        """
        Update session id of ticket or it's parent in case this is a shared ticket
        """
        if not ticket.parent:
            ticket_to_update = ticket
        else:
            ticket_to_update = ticket.parent

        if sessionid is None:
            ticket_to_update.sessionid = None
        else:
            # remove first character, because guacd sessionid has '$' as it's first symbol
            newuuid = sessionid.__str__()[1:37]
            ticket_to_update.sessionid = uuid.UUID(newuuid)

        ticket_to_update.save()

    @database_sync_to_async
    def log_ticket_action(self, ticket, action, scope):
        TicketLog.addlog(ticket, action, scope=scope)

    @database_sync_to_async
    def get_ticket_sessionid(self, ticket):
        """
        Gets session id associated with ticket or with it's parent if this is a shared ticket
        """
        if not ticket.parent:
            return ticket.sessionid
        return ticket.parent.sessionid

    @database_sync_to_async
    def get_ticket_connection(self, ticket):
        """
        Get connection definition from ticket or from tickets's parent if this is a shared ticket
        """
        if not ticket.parent:
            return ticket.connection
        return ticket.parent.connection

    @database_sync_to_async
    def get_default_guacd_server(self):
        return AppSettings.load().default_guacd_server
