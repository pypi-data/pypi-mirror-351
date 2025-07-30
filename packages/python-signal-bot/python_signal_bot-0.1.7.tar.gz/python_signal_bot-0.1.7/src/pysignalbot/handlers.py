""""""
import asyncio
import dataclasses
import inspect
import typing

import async_timeout

from .exceptions import ConversationError



@dataclasses.dataclass
class GeneralHandler:
    """"""
    func: typing.Callable
    filter_: typing.Optional["MessageFilter"] = None

    async def run(self, obj: typing.Any,
                  context: "HandlerContext", use_filter=True) -> typing.Any:
        """"""
        if use_filter is True and self.match_filter(obj) is False:
            return False
        result = self.func(obj, context)
        if inspect.isawaitable(result):
            result = await result
        return result

    def match_filter(self, obj: typing.Any) -> bool:
        """"""
        return self.filter_ is None or self.filter_.check(obj)

class MessageHandler(GeneralHandler):
    """"""
class ErrorHandler(GeneralHandler):
    """"""
class ExceptionHandler(GeneralHandler):
    """"""
class PayloadHandler(GeneralHandler):
    """"""


@dataclasses.dataclass
class HandlerContext:
    """"""
    bot: "SignalBot"
    conversation: typing.Optional["Conversation"] = None


class HandlerCollection:
    """"""
    def __init__(self) -> None:
        """"""
        self.handlers = []

    def add(self, handler: GeneralHandler) -> None:
        """"""
        self.handlers.append(handler)

    async def run(self, obj: typing.Any, context: HandlerContext) -> None:
        """"""
        await self.start(obj, context)

    def start(self, obj: typing.Any,
              context: HandlerContext) -> typing.Awaitable[typing.Any]:
        """"""
        async def in_task() -> typing.Any:
            """"""
            result = None
            for handler in self.handlers:
                result = await handler.run(obj, context)
                if result is not False:
                    break
            return result
        return asyncio.create_task(in_task())


@dataclasses.dataclass
class ConversationHandler:
    """"""
    PREDEFINED_STATES = ["abort", "end", "ended", "timeout"]

    states: dict[str, GeneralHandler]
    enter_handler: MessageHandler
    abort_handler: MessageHandler | None = None
    end_handler: GeneralHandler | None = None
    timeout_handler: GeneralHandler | None = None
    outer_state_handler: GeneralHandler | None = None
    timeout: int = 600
    allow_group: bool = False

    def __post_init__(self) -> None:
        for state in self.states:
            if state in self.PREDEFINED_STATES:
                raise ConversationError(f"ConversationHandler state '{state}' \
                                        is one of the predefined states!")

    def is_enter(self, message: "DataMessage") -> bool:
        """"""
        return self.enter_handler.match_filter(message)

    def is_abort(self, message: "DataMessage") -> bool:
        """"""
        return self.abort_handler.match_filter(message)

    async def handle_enter(self, message: "DataMessage",
                           context: HandlerContext) -> str:
        """"""
        return await self.enter_handler.run(message, context, False)

    async def handle_timeout(self, context: HandlerContext) -> None:
        """"""
        if self.timeout_handler is not None:
            await self.timeout_handler.run(None, context)

    async def handle_end(self, context: HandlerContext) -> None:
        """"""
        if self.end_handler is not None:
            await self.end_handler.run(None, context)

    async def handle_outer_state(self, context: HandlerContext) -> str:
        """"""
        if self.outer_state_handler is not None:
            return await self.outer_state_handler.run(None, context)
        return None

    async def handle_abort(self, message: "DataMessage",
                           context: HandlerContext) -> None:
        """"""
        if self.abort_handler is not None:
            await self.abort_handler.run(message, context, False)

    def has_state(self, state: str) -> bool:
        """"""
        return state in self.states or state in self.PREDEFINED_STATES

    async def handle_message(self, message: "DataMessage",
                             context: HandlerContext) -> str:
        """"""
        conversation_state = context.conversation.state
        for handler in self.states[conversation_state]:
            if isinstance(handler, ConversationHandler):
                if handler.is_enter(message):
                    conversation = Conversation(message, handler, context.bot,
                                                context.conversation)
                    context.conversation.inner_conversation = conversation
                    conversation.enter()
                    return context.conversation.state
                continue
            result = await handler.run(message, context)
            if result is None:
                break
            if result is not False:
                return result
        return conversation_state


class Conversation:
    """"""
    def __init__(self, enter_message: "DataMessage",
                 handler: ConversationHandler, bot: "Bot",
                 outer_conversation: typing.Optional["Conversation"] = None) -> None:
        """"""
        self.enter_message = enter_message
        self.handler = handler
        self.origin = self.enter_message.origin
        if self.handler.allow_group is True and len(self.origin) == 2:
            self.origin = self.origin[:1]
        self.context = HandlerContext(bot, self)
        self.outer_conversation = outer_conversation
        self.inner_conversation = None
        self.message_queue = asyncio.Queue()
        self.state = None
        self.custom_state = None
        self.background_task = None

    def is_running(self) -> bool:
        """"""
        return self.state != "ended"

    async def exit(self) -> None:
        """"""
        if self.inner_conversation is not None:
            self.inner_conversation.exit()
        if self.outer_conversation is not None:
            outer_state = await self.handler.handle_outer_state(self.context)
            if outer_state is not None:
                self.outer_conversation.state = outer_state
            self.outer_conversation.inner_conversation = None
        else:
            self.context.bot.dispatcher.conversations.pop(self.origin)
        self.state = "ended"

    async def add_message(self, message: "DataMessage") -> None:
        """"""
        await self.message_queue.put(message)

    def enter(self) -> None:
        """"""
        async def try_in_task() -> None:
            try:
                await in_task()
            except Exception as exc:
                await self.context.bot.dispatcher.dispatch_exception(exc)

        async def in_task() -> None:
            """"""
            self.state = await self.handler.handle_enter(self.enter_message,
                                                         self.context)
            while True:
                if self.state == "end":
                    await self.handler.handle_end(self.context)
                    await self.exit()
                    return
                try:
                    async with async_timeout.timeout(self.handler.timeout):
                        message = await self.message_queue.get()
                except asyncio.TimeoutError:
                    self.state = "timeout"
                    await self.handler.handle_timeout(self.context)
                    await self.exit()
                    return
                if self.inner_conversation is not None:
                    await self.inner_conversation.add_message(message)
                    continue
                if self.handler.abort_handler is not None \
                        and self.handler.is_abort(message) is True:
                    self.state = "abort"
                    await self.handler.handle_abort(message, self.context)
                    await self.exit()
                    return
                self.state = await self.handler.handle_message(message,
                                                               self.context)
                if not self.handler.has_state(self.state):
                    raise ConversationError(
                        "Undefined conversation state " \
                        f"'{self.state}' returned by handler!")
        self.background_task = asyncio.create_task(try_in_task())
