""""""
import datetime
import json
import os
import re
import shutil
import types
import typing
import uuid

from .exceptions import RecipientsError



class Printable:
    """"""
    def __repr__(self):
        """"""
        return str(self.__dict__)

class PrettyNamespace(types.SimpleNamespace):
    """"""
    def __str__(self):
        """"""
        return self.to_json()

    def __repr__(self):
        """"""
        return self.to_json()

    def to_json(self):
        """"""
        return json.dumps(self, default=lambda obj: obj.__dict__)


class Message(Printable):
    """"""
    def __init__(self, params):
        """"""
        self.account = params.account
        envelope = params.envelope
        self.parsed_datetime = datetime.datetime.now()
        self.envelope_datetime = get_datetime(envelope.timestamp)
        self.envelope_timestamp = envelope.timestamp
        self.user = SourceUser(envelope)

class ReceiveError(Message):
    """"""
    def __init__(self, params):
        """"""
        super().__init__(params)
        self.message = params.exception.message
        self.type = params.exception.type

class DataMessage(Message):
    """"""
    def __init__(self, params):
        """"""
        super().__init__(params)
        data = params.envelope.dataMessage
        self.datetime = get_datetime(data.timestamp)
        self.timestamp = data.timestamp
        self.id = data.timestamp
        self.text = data.message
        self.expiry = data.expiresInSeconds
        self.view_once = data.viewOnce

        self.origin = None
        self.group = None
        try:
            group_data = data.groupInfo
            self.group = SourceGroup(group_data)
            self.origin = (self.group.id, self.user.uuid)
        except AttributeError:
            pass
        if self.origin is None:
            self.origin = (self.user.uuid,)
        self.quote = None
        try:
            quote_data = data.quote
            self.quote = Quote(quote_data)
        except AttributeError:
            pass
        self.reaction = None
        try:
            reaction_data = data.reaction
            self.reaction = Reaction(reaction_data)
        except AttributeError:
            pass
        self.attachments = []
        try:
            for attachment_data in data.attachments:
                self.attachments.append(Attachment(attachment_data))
        except AttributeError:
            pass
        self.shortened = False
        self.full_text = None
        for attachment in self.attachments:
            if attachment.type != "text/x-signal-plain":
                continue
            if attachment.content is None:
                self.shortened = True
            else:
                self.full_text = attachment.content.decode("utf-8")
        self.mentions = []
        try:
            for mention_data in data.mentions:
                self.mentions.append(Mention(mention_data))
        except AttributeError:
            pass
        self.command = None
        self.text_without_command = None
        if self.text is not None:
            match = re.search(r"^\/([^\s]+)\s?([\s\S]*)", self.text)
            if match is not None:
                self.command = match.group(1)
                self.text_without_command = match.group(2)

class Attachment:
    """"""
    def __init__(self, data):
        """"""
        self.id = data.id
        self.type = data.contentType
        self.filename = data.filename
        self.size = data.size
        self.content = None

class QuoteAttachment:
    """"""
    def __init__(self, data):
        """"""
        self.type = data.contentType
        self.filename = data.filename
        try:
            self.thumbnail = data.thumbnail
        except AttributeError:
            self.thumbnail = None

class Mention(Printable):
    """"""
    def __init__(self, data):
        """"""
        self.user = MentionUser(data)
        self.start = data.start
        self.length = data.length

    def string(self):
        """"""
        return f"{self.start}:{self.length}:{self.user.uuid}"


class Reaction(Printable):
    """"""
    def __init__(self, data):
        """"""
        self.emoji = data.emoji
        self.target_user = ReactionUser(data)
        self.target_utc_timestamp = get_datetime(data.targetSentTimestamp)
        self.removed = data.isRemove


class Quote(Printable):
    """"""
    def __init__(self, data):
        """"""
        self.user = QuoteUser(data)
        self.id = data.id
        self.text = data.text
        self.attachments = []
        try:
            for attachment_data in data.attachments:
                self.attachments.append(QuoteAttachment(attachment_data))
        except AttributeError:
            pass
        self.shortened = False
        self.full_text = None
        for attachment in self.attachments:
            if attachment.type != "text/x-signal-plain":
                continue
            if attachment.content is None:
                self.shortened = True
            else:
                self.full_text = attachment.content.decode("utf-8")
        self.mentions = []
        try:
            for mention_data in data.mentions:
                self.mentions.append(Mention(mention_data))
        except AttributeError:
            pass


class ReceiptMessage(Message):
    """"""
    def __init__(self, params):
        """"""
        super().__init__(params)
        data = params.envelope.receiptMessage
        self.delivered = data.isDelivery
        self.read = data.isRead
        self.viewed = data.isViewed
        self.utc_message = get_datetime(data.when)
        self.utc_dates = [get_datetime(timestamp) \
                          for timestamp in data.timestamps]


class TypingMessage(Message):
    """"""
    def __init__(self, params):
        """"""
        super().__init__(params)
        data = params.envelope.typingMessage
        self.utc_timestamp = get_datetime(data.timestamp)
        if data.action == "STOPPED":
            self.typing = False
        else:
            self.typing = True


class SourceUser(Printable):
    """"""
    def __init__(self, envelope):
        """"""
        self.name = envelope.sourceName
        self.number = envelope.sourceNumber
        self.uuid = envelope.sourceUuid
        self.device = envelope.sourceDevice


class MentionUser(Printable):
    """"""
    def __init__(self, mention):
        """"""
        self.name = mention.name
        self.number = mention.number
        self.uuid = mention.uuid


class QuoteUser(Printable):
    """"""
    def __init__(self, quote):
        """"""
        self.name = quote.author
        self.number = quote.authorNumber
        self.uuid = quote.authorUuid

class ReactionUser(Printable):
    """"""
    def __init__(self, reaction):
        """"""
        self.name = reaction.targetAuthor
        self.number = reaction.targetAuthorNumber
        self.uuid = reaction.targetAuthorUuid


class SourceGroup(Printable):
    """"""
    def __init__(self, data):
        """"""
        self.id = data.groupId
        self.type = data.type

class Response(Printable):
    """"""
    def __init__(self, data):
        """"""
        self.id = data.id
        self.result = data.result

class MessageResponse(Response):
    """"""
    def __init__(self, data):
        """"""
        super().__init__(data)
        self.timestamp = self.result.timestamp
        self.datetime = get_datetime(self.result.timestamp)

class ErrorResponse(Printable):
    """"""
    def __init__(self, data):
        """"""
        self.id = data.id
        self.code = data.error.code
        self.message = data.error.message
        self.data = data.error.data




class Stickerpack:
    """"""
    def __init__(self, manifest):
        """"""
        self.id = manifest.id
        self.title = manifest.title
        self.author = manifest.author
        self.stickers = manifest.stickers

    def get_id(self, emoji):
        """"""
        for sticker in self.stickers:
            if sticker.emoji == emoji:
                return f"{self.id}:{sticker.id}"
        return None


class SendAttachment:
    """"""
    def __init__(self, data, local_data_path, signalcli_data_path):
        """"""
        if isinstance(data, str):
            self.filename = data
            with open(data, "rb") as file:
                self.content = file.read()
        else:
            self.filename, self.content = data
        self.uuid = str(uuid.uuid4())
        self.local_dirpath = os.path.join(local_data_path, "attachments",
                                          self.uuid)
        self.local_filepath = os.path.join(self.local_dirpath, self.filename)
        self.signalcli_filepath = os.path.join(signalcli_data_path,
                                               "attachments", self.uuid,
                                               self.filename)
        os.mkdir(self.local_dirpath)
        with open(self.local_filepath, "wb") as file:
            file.write(self.content)

    def remove(self):
        """"""
        shutil.rmtree(self.local_dirpath)


class Recipients:
    """"""
    def __init__(self, uuids: list[str] | None = None,
                 group_id: str | None = None) -> None:
        """"""
        if (uuids is None and group_id is None) \
                or uuids is not None and group_id is not None:
            raise RecipientsError("Uuid XOR group id required!")
        self.uuids = uuids
        self.group_id = group_id

    @classmethod
    def from_response(cls, response: Response) -> "Recipients":
        """"""
        try:
            return cls(group_id=response.result.results[0].groupId)
        except AttributeError:
            pass
        return cls(uuids=[result.recipientAddress.uuid \
            for result in response.result.results])

    @classmethod
    def from_message(cls, message: DataMessage) -> "Recipients":
        """"""
        if message.group is not None:
            return cls(group_id=message.group.id)
        return cls(uuids=[message.user.uuid])

    @classmethod
    def from_guess(cls, obj: typing.Any) -> "Recipients":
        """"""
        if isinstance(obj, Response):
            return cls.from_response(obj)
        if isinstance(obj, DataMessage):
            return cls.from_message(obj)
        if isinstance(obj, list):
            return cls(uuids=obj)
        if isinstance(obj, tuple):
            obj = obj[0]
        if re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}" \
                        r"-[0-9a-f]{4}-[0-9a-f]{12}", obj) is None:
            return cls(group_id=obj)
        return cls(uuids=[obj])

    def payload(self) -> dict:
        """"""
        if self.group_id is not None:
            return {"groupId":self.group_id}
        return {"recipient":self.uuids}

    def single(self) -> str:
        """"""
        if self.group_id is not None:
            return self.group_id
        if len(self.uuids) == 1:
            return self.uuids[0]
        raise RecipientsError("More than one recipient!")


def get_datetime(timestamp):
    """"""
    return datetime.datetime.utcfromtimestamp(timestamp / 1000)
