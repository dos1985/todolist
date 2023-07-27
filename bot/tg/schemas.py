from typing import List, Optional
from dataclasses import field

import marshmallow_dataclass
from marshmallow_dataclass import dataclass
from marshmallow import EXCLUDE


@dataclass
class MessageFrom:
    id: int
    is_bot: bool
    first_name: str | None
    username: str | None

    class Meta:
        unknown = EXCLUDE


@dataclass
class MessageChat:
    id: int
    first_name: str | None
    username: str | None
    type: str
    title: str | None


    class Meta:
        unknown = EXCLUDE


@dataclass
class Message:
    message_id: int
    msg_from: MessageFrom = field(metadata={'data_key': 'from'})
    chat: MessageChat
    date: int
    text: str | None

    class Meta:
        unknown = EXCLUDE


@dataclass
class GetUpdatesResponse:
    message_id: int
    msg_from: MessageFrom = field(metadata={'data_key': 'from'})
    chat: MessageChat
    date: int
    text: str | None

    class Meta:
        unknown = EXCLUDE


@dataclass
class SendMessageResponse:
    ok: bool
    result: Message  # todo

    class Meta:
        unknown = EXCLUDE


@dataclass
class UpdateObj:
    update_id: int
    message: Optional[Message] = None

    class Meta:
        unknown = EXCLUDE


@dataclass
class GetUpdatesResponse:
    ok: bool
    result: list[UpdateObj]

    class Meta:
        unknown = EXCLUDE


GET_UPDATES_SCHEMA = marshmallow_dataclass.class_schema(GetUpdatesResponse)()
SEND_MESSAGE_RESPONSE_SCHEMA = marshmallow_dataclass.class_schema(SendMessageResponse)()

