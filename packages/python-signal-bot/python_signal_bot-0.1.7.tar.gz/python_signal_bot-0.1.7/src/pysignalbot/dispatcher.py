""""""
import asyncio
import json
import logging
import signal
import typing

from .exceptions import DispatcherError, SocketError
from .handlers import (Conversation, ConversationHandler, ErrorHandler,
                       ExceptionHandler, GeneralHandler, HandlerCollection,
                       HandlerContext, MessageHandler, PayloadHandler)
from .models import (DataMessage, ErrorResponse, Message, MessageResponse,
                     PrettyNamespace, ReceiptMessage, Response, ReceiveError,
                     TypingMessage)

class Dispatcher:
    """"""
    def __init__(self, bot: "SignalBot") -> None:
        """"""
        self.log = logging.getLogger(__name__)
        self.bot = bot
        self.stream_reader = None
        self.stream_writer = None
        self.conversation_handlers = []
        self.payload_handlers = HandlerCollection()
        self.message_handlers = HandlerCollection()
        self.error_handlers = HandlerCollection()
        self.exception_handlers = HandlerCollection()
        self.conversations = {}
        self.responses = {}
        self.connected = False
        self.running = False
        self.main_task = None
        self.dispatch_tasks = set()
        self.planned_disconnect = False

    async def disconnect(self) -> None:
        """"""
        self.planned_disconnect = True
        if self.connected is True:
            self.stream_writer.close()
            await self.stream_writer.wait_closed()
            self.connected = False
        self.planned_disconnect = False

    async def connect(self, retry_backoff: bool = True,
                      retries: int = 30) -> None:
        """"""
        tries = 1
        while self.connected is False:
            try:
                self.stream_reader, self.stream_writer = \
                    await asyncio.open_connection(self.bot.signalcli_host,
                                                  self.bot.signalcli_port)
                self.connected = True
            except OSError as exc:
                if retry_backoff is False:
                    raise exc
                if tries > retries:
                    raise SocketError("Socket connection failed to often!") \
                        from exc
                wait = tries * 2
                self.log.error("Socket connection failed, waiting %s " \
                               "seconds and retrying...", wait)
                await asyncio.sleep(wait)
                tries += 1
        self.log.info("Socket connected!")

    async def start(self) -> None:
        """"""
        self.main_task = asyncio.create_task(self.run())

    async def run(self) -> None:
        """"""
        try:
            if self.running is True:
                self.log.warning("Already running, not running again!")
                return
            if self.connected is False:
                await self.connect()
            while True:
                payload = await self.stream_reader.readline()
                if payload == b"":
                    if self.planned_disconnect is True:
                        self.log.warning("Manually disconnecting...")
                        return
                    self.log.error("Socket connection error! Reconnecting...")
                    await self.disconnect()
                    await self.connect()
                    continue
                task = asyncio.create_task(self.try_dispatch_payload(payload))
                self.dispatch_tasks.add(task)
                task.add_done_callback(self.dispatch_tasks.discard)
            self.running = True
        except asyncio.CancelledError:
            self.log.warning("Socket loop task cancelled, disconnecting...")
            await self.disconnect()

    def add_handler(self, handler: GeneralHandler) -> None:
        """"""
        if isinstance(handler, ConversationHandler):
            self.conversation_handlers.append(handler)
        elif isinstance(handler, PayloadHandler):
            self.payload_handlers.add(handler)
        elif isinstance(handler, MessageHandler):
            self.message_handlers.add(handler)
        elif isinstance(handler, ErrorHandler):
            self.error_handlers.add(handler)
        elif isinstance(handler, ExceptionHandler):
            self.exception_handlers.add(handler)
        else:
            raise DispatcherError("Invalid handler type!")

    async def send(self, payload: dict) -> None:
        """"""
        payload = bytes(f"{json.dumps(payload)}\n", encoding="utf-8")
        self.stream_writer.write(payload)
        await self.stream_writer.drain()

    async def try_dispatch_payload(self, raw_payload: bytes) -> None:
        """"""
        try:
            await self.dispatch_payload(raw_payload)
        except Exception as exc:
            await self.dispatch_exception(exc)

    async def dispatch_payload(self, raw_payload: bytes) -> None:
        """"""
        try:
            payload_dict = json.loads(raw_payload)
        except json.decoder.JSONDecodeError as exc:
            raise DispatcherError("Payload with invalid JSON: " \
                                  f"{raw_payload}") from exc
        payload = json.loads(raw_payload,
                             object_hook=lambda dct: PrettyNamespace(**dct))
        await self.payload_handlers.run(payload, HandlerContext(self.bot))
        if "error" in payload_dict and "id" in payload_dict:
            self.responses[payload.id] = ErrorResponse(payload)
            return
        if "result" in payload_dict:
            if "results" in payload_dict["result"]:
                self.responses[payload.id] = MessageResponse(payload)
            else:
                self.responses[payload.id] = Response(payload)
        elif "method" in payload_dict and payload.method == "receive":
            if "exception" in payload_dict["params"]:
                await self.dispatch_error(ReceiveError(payload.params))
                return
            envelope_dict = payload_dict["params"]["envelope"]
            if "receiptMessage" in envelope_dict:
                message = ReceiptMessage(payload.params)
            elif "typingMessage" in envelope_dict:
                message = TypingMessage(payload.params)
            elif "dataMessage" in envelope_dict:
                message = DataMessage(payload.params)
            else:
                message = Message(payload.params)
            await self.dispatch_message(message)

    async def dispatch_message(self, message: Message) -> None:
        """"""
        is_conversation = False
        if isinstance(message, DataMessage):
            is_conversation = await self.try_conversations(message)
        if is_conversation is False:
            await self.message_handlers.run(message, HandlerContext(self.bot))

    async def try_conversations(self, message: DataMessage) -> bool:
        """"""
        conversation = self.conversations.get(message.origin)
        if conversation is not None:
            await conversation.add_message(message)
            return True
        if len(message.origin) == 2:
            conversation = self.conversations.get(message.origin[:1])
            if conversation is not None \
                    and conversation.handler.allow_group is True:
                await conversation.add_message(message)
                return True
        for handler in self.conversation_handlers:
            if handler.is_enter(message) is True:
                conversation = Conversation(message, handler, self.bot)
                self.conversations[conversation.origin] = conversation
                conversation.enter()
                return True
        return False


    async def dispatch_error(self, error: typing.Any) -> None:
        """"""
        await self.error_handlers.run(error, HandlerContext(self.bot))

    async def dispatch_exception(self, exc: Exception) -> None:
        """"""
        await self.exception_handlers.run(exc, HandlerContext(self.bot))
