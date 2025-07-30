""""""
import asyncio
import glob
import json
import os
import re
import typing
import uuid

import async_timeout

from .dispatcher import Dispatcher
from .exceptions import (GroupSendError, RpcCallError, RpcCallTimeoutError,
                         SendError, SignalBotError)
from .models import (DataMessage, ErrorResponse, PrettyNamespace, Recipients,
                     Response, SendAttachment, Stickerpack)

# TODO
# - Add syncMessage support

# Might implement in the future:
# - Operations on profile, group, contacts and configuration; blocking
# - Some kind of script for linking, registration and verification

# Not working/not implemented/undocumented in signal-cli:
# - Quoting message with sticker/image won't show sticker/image thumbnail in the quote
# - Quoting image/sticker only message will lead to no quote at all
# - Sending images with "view once"
# - Sometimes the about_emoji seems to get set in a weird way when using update_profile


class SignalBot:
    """"""
    def __init__(self, signalcli_host: str,
                 signalcli_port: typing.Union[str, int],
                 remote_data_path: str = "/data",
                 local_data_path: str = "/data",
                 call_timeout: float = 5.0,
                 call_delay: float = 0.3) -> None:
        """"""
        self.signalcli_host = signalcli_host
        self.signalcli_port = int(signalcli_port)
        self.remote_data_path = remote_data_path
        self.local_data_path = local_data_path
        self.call_timeout = call_timeout
        self.call_delay = call_delay
        self.stickerpacks = []
        self.refresh_stickerpacks()
        self.dispatcher = Dispatcher(self)

    async def rpc_call(self, method: str, params: dict | None = None,
                       timeout: float | None = None, delay: float | None = None) -> Response:
        """"""
        request_id = str(uuid.uuid4())
        payload = {"jsonrpc":"2.0", "method":method, "params":params,
                   "id":request_id}
        if timeout is None:
            timeout = self.call_timeout
        if delay is None:
            delay = self.call_delay
        await self.dispatcher.send(payload)
        try:
            async with async_timeout.timeout(timeout):
                while True:
                    await asyncio.sleep(delay)
                    try:
                        response = self.dispatcher.responses.pop(request_id)
                        break
                    except KeyError:
                        pass
        except asyncio.TimeoutError as exc:
            raise RpcCallTimeoutError("Timeout while waiting for response; " \
                                      f"call payload: {payload}") from exc
        if isinstance(response, ErrorResponse):
            try:
                error_type = response.data.response.results[0].type
                if error_type in ("UNREGISTERED_FAILURE", "IDENTITY_FAILURE"):
                    raise SendError("Sending to recipient failed!",
                                    response.data.response.results)
            except (AttributeError, IndexError):
                pass
            try:
                if "User is not a member in group" in response.message \
                        or "Invalid group id" in response.message \
                        or "Group not found" in response.message:
                    raise GroupSendError("Sending to group failed!",
                                         response)
            except (AttributeError, TypeError):
                pass

            raise RpcCallError("Calling failed with error!", response)
        try:
            for result in response.result.results:
                if result.type != "SUCCESS":
                    raise SendError("Sending failed for some recipients!",
                                    response.result.results)
        except AttributeError:
            pass
        return response

    async def send_message(self, recipient: list[str] | str,
                           text: str | None = None,
                           attachment: list[str] | str | None = None,
                           quote: DataMessage | None = None,
                           replace_mentions: bool = True) -> Response:
        """"""
        params = {**Recipients.from_guess(recipient).payload(), "message":text}
        if attachment is not None:
            if not isinstance(attachment, list):
                attachment = [attachment]
            attachment = [SendAttachment(item, self.local_data_path,
                                         self.remote_data_path) \
                          for item in attachment]
            params["attachments"] = [item.signalcli_filepath \
                                     for item in attachment]
        if quote is not None:
            params["quoteTimestamp"] = quote.timestamp
            params["quoteAuthor"] = quote.user.uuid
            params["quoteMessage"] = quote.text
            if len(quote.mentions) > 0:
                params["quoteMention"] = [mention.string() \
                                          for mention in quote.mentions]
        if replace_mentions is True and text is not None:
            params["mention"] = [f"{match.start(0)}:{len(match.group(0))}:" \
                                 f"{match.group(1)}" \
                                 for match in \
                                 re.finditer(
                                     r"@([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}" \
                                     r"-[0-9a-f]{4}-[0-9a-f]{12})", text)]
        response = await self.rpc_call("send", params)
        if attachment is not None:
            map(lambda item: item.remove())
        return response

    async def send_reply(self, message: DataMessage, text: str,
                         attachment: list[str] | str | None = None,
                         quote: bool = True,
                         replace_mentions: bool = True) -> Response:
        """"""
        if not isinstance(message, DataMessage):
            raise SignalBotError("Responding is only works for DataMessage!")
        recipient = Recipients.from_message(message).single()
        if quote is True:
            quote_message = message
        else:
            quote_message = None
        return await self.send_message(recipient, text, attachment, quote_message,
                                 replace_mentions)

    async def send_sticker(self, recipient: list[str] | str, pack_title: str,
                           emoji: str) -> Response:
        """"""
        for stickerpack in self.stickerpacks:
            if stickerpack.title == pack_title:
                sticker = stickerpack.get_id(emoji)
                break
        else:
            raise SignalBotError(f"No sticker for {emoji} found in " \
                                 "stickerpack {pack_title} or " \
                                 "even stickerpack not found!")
        params = {**Recipients.from_guess(recipient).payload(),
                  "sticker":sticker}
        return await self.rpc_call("send", params)

    async def send_reaction(self, message: DataMessage, emoji: str,
                            remove: bool = False) -> Response:
        """"""
        if not isinstance(message, DataMessage):
            raise SignalBotError("Reacting is only possible for DataMessage!")
        params = {**Recipients.from_message(message).payload(), "emoji":emoji,
                  "targetAuthor":message.user.uuid,
                  "targetTimestamp":message.timestamp, "remove":remove}
        return await self.rpc_call("sendReaction", params)

    async def send_receipt(self, message: DataMessage,
                           viewed: bool = False) -> Response:
        """"""
        params = {"recipient":message.user.uuid,
                  "targetTimestamp":message.timestamp}
        if viewed is True:
            params["type"] = "viewed"
        else:
            params["type"] = "read"
        return await self.rpc_call("sendReceipt", params)

    async def send_typing(self, recipient: list[str] | str, stop: bool = False,
                          timeout: int | None = None) -> Response:
        """"""
        params = Recipients.from_guess(recipient).payload()
        if timeout is None:
            params["stop"] = stop
            return await self.rpc_call("sendTyping", params)
        schedule = [*([10] * int(timeout // 10)), timeout % 10]
        for seconds in schedule:
            await self.rpc_call("sendTyping", params)
            await asyncio.sleep(seconds)
        params["stop"] = True
        return await self.rpc_call("sendTyping", params)

    async def remote_delete(self, response: Response) -> Response:
        """"""
        params = {**Recipients.from_response(response).payload(),
                  "targetTimestamp":response.timestamp}
        return await self.rpc_call("remoteDelete", params)

    async def join_group(self, uri: str) -> Response:
        """"""
        params = {"uri":uri}
        return await self.rpc_call("joinGroup", params)

    async def list_contacts(self) -> Response:
        """"""
        return await self.rpc_call("listContacts")

    async def list_groups(self) -> Response:
        """"""
        return await self.rpc_call("listGroups")

    async def list_identities(self,
                              number: str | None = None) -> Response:
        """"""
        params = {"number":number}
        return await self.rpc_call("listIdentities", params)

    async def update_profile(self, first_name: str | None = None,
                             last_name: str | None = None,
                             about: str | None = None,
                             about_emoji: str | None = None,
                             avatar: str | None = None,
                             remove_avatar: bool = False) -> Response:
        """"""
        params = {"givenName":first_name, "familyName":last_name,
                  "about":about, "aboutEmoji":about_emoji,
                  "removeAvatar":remove_avatar}
        if avatar is not None and remove_avatar is False:
            avatar = SendAttachment(avatar, self.local_data_path,
                                    self.remote_data_path)
            params["avatar"] = avatar.signalcli_filepath
        response = await self.rpc_call("updateProfile", params)
        if avatar is not None:
            avatar.remove()
        return response

    async def update_contact(self, number: str, name: str | None = None,
                             expiration_seconds: int | None = None) \
                                 -> Response:
        """"""
        params = {"recipient":number, "name":name,
                  "expiration":expiration_seconds}
        return await self.rpc_call("updateContact", params)

    async def remove_contact(self, number: str,
                             forget: bool = True) -> Response:
        """"""
        params = {"recipient":number, "forget": forget}
        return await self.rpc_call("removeContact", params)

    async def trust(self, number: str, safety_number: str | None = None,
                    all_keys: bool = False) -> Response:
        """"""
        params = {"recipient":number, "trustAllKnownKeys":all_keys,
                  "verifiedSafetyNumber":safety_number}
        return await self.rpc_call("trust", params)

    def refresh_stickerpacks(self) -> None:
        """"""
        manifests = glob.glob(os.path.join(self.local_data_path,
                                           "stickers/*/manifest.json"))
        parsed = []
        for manifest_path in manifests:
            with open(manifest_path, encoding="utf8") as file:
                manifest = json.load(file, object_hook= \
                    lambda dct: PrettyNamespace(**dct))
                manifest.id = manifest_path.split("/")[-2]
                parsed.append(Stickerpack(manifest))
        self.stickerpacks = parsed

    def load_attachments(self, message: DataMessage) -> list["Attachment"]:
        """"""
        for attachment in message.attachments:
            path = os.path.join(self.local_data_path, "attachments",
                                attachment.id)
            with open(path, "rb", encoding="utf8") as file:
                attachment.content = file.read()
        return message.attachments
