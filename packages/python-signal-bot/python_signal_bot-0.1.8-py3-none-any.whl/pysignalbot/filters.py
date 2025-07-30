""""""
import re

from .models import DataMessage, Message, ReceiptMessage, TypingMessage



class MessageFilter:
    """"""
    def __init__(self, category: str | None = None, content: str | None = None,
                 source: str | None = None) -> None:
        """"""
        self.category = category
        self.content = content
        if source is None:
            self.source = None
        else:
            self.source = source.split(":", 1)

    def check(self, message: Message) -> bool:
        """"""
        if self.source is not None and self.check_source(message) is False:
            return False
        if self.category is None:
            return True
        if self.category == "receipt":
            return self.check_receipt(message)
        if self.category == "typing":
            return self.check_typing(message)
        if isinstance(message, DataMessage):
            if self.category == "text":
                return self.check_text(message)
            if self.category == "command":
                return self.check_command(message)
            if self.category == "reaction":
                return self.check_reaction(message)
            if self.category == "quote":
                return self.check_quote(message)
            if self.category == "mention":
                return self.check_mention(message)
            if self.category == "attachment":
                return self.check_attachment(message)
        return False

    def check_source(self, message: Message) -> bool:
        """"""
        if self.source[0] == "number" \
                and message.user.number == self.source[1]:
            return True
        if self.source[0] == "uuid" and message.user.uuid == self.source[1]:
            return True
        if self.source[0] == "name" and message.user.name == self.source[1]:
            return True
        if self.source[0] == "group" and message.group is not None \
                and message.group.id == self.source[1]:
            return True
        return False

    def check_receipt(self, message: ReceiptMessage) -> bool:
        """"""
        if not isinstance(message, ReceiptMessage):
            return False
        if self.content is None:
            return True
        if self.content == "delivered" and message.delivered is True:
            return True
        if self.content == "read" and message.read is True:
            return True
        if self.content == "viewed" and message.viewed is True:
            return True
        return False

    def check_typing(self, message: TypingMessage) -> bool:
        """"""
        if not isinstance(message, TypingMessage):
            return False
        if self.content is None:
            return True
        if self.content == "started" and message.typing is True:
            return True
        if self.content == "stopped" and message.typing is False:
            return True
        return False

    def check_text(self, message: DataMessage) -> bool:
        """"""
        if message.text is None:
            return False
        if self.content is None:
            return True
        if re.search(self.content, message.text) is not None:
            return True
        return False

    def check_command(self, message: DataMessage) -> bool:
        """"""
        if message.command is None:
            return False
        if self.content is None:
            return True
        if self.content == message.command:
            return True
        return False

    def check_reaction(self, message: DataMessage) -> bool:
        """"""
        if message.reaction is None:
            return False
        if self.content is None:
            return True
        content = self.content.split()
        if content[-1] == message.reaction.emoji:
            if len(content) > 1 and content[0] == "removed" \
                    and message.reaction.removed is True:
                return True
            if len(content) == 1 and message.reaction.removed is False:
                return True
        return False

    def check_quote(self, message: DataMessage) -> bool:
        """"""
        if message.quote is None:
            return False
        if self.content is None:
            return True
        if self.content == "me" \
                and message.quote.user.number == message.account:
            return True
        if self.content == message.quote.user.number:
            return True
        return False

    def check_mention(self, message: DataMessage) -> bool:
        """"""
        if len(message.mentions) == 0:
            return False
        if self.content is None:
            return True
        for mention in message.mentions:
            if self.content == "me" and mention.user.number == message.account:
                return True
            if self.content == mention.user.number:
                return True
        return False

    def check_attachment(self, message: DataMessage) -> bool:
        """"""
        if len(message.attachments) == 0:
            return False
        if self.content is None:
            return True
        for attachment in message.attachments:
            if re.search(self.content, attachment.type) is not None:
                return True
        return False


class AND:
    """"""
    def __init__(self, *filters: MessageFilter) -> None:
        """"""
        self.filters = filters
    def check(self, message: Message) -> bool:
        """"""
        for filter_ in self.filters:
            if filter_.check(message) is False:
                return False
        return True


class OR:
    """"""
    def __init__(self, *filters: MessageFilter) -> None:
        """"""
        self.filters = filters
    def check(self, message: Message) -> bool:
        """"""
        for filter_ in self.filters:
            if filter_.check(message) is True:
                return True
        return False


class NOT:
    """"""
    def __init__(self, filter_) -> None:
        """"""
        self.filter = filter_
    def check(self, message: Message) -> bool:
        """"""
        return self.filter.check(message) is False
