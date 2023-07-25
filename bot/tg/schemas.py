from typing import List
from dataclasses import field

import marshmallow_dataclass
from marshmallow_dataclass import dataclass
from marshmallow import EXCLUDE



@dataclass
class MessageFrom:
    id: int
    is_bot: bool
    first_name: str | None
    # last_name: str | None
    username: str | None

    class Meta:
        unknown = EXCLUDE


@dataclass
class MessageChat:
    id: int
    first_name: str | None
    username: str | None
    # last_name: str | None
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
    message: Message

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


# class Chat:
#     def __init__(self, id: int, first_name: str = None, username: str = None):
#         self.id = id
#         self.first_name = first_name
#         self.username = username
#
#
# class Message:
#     def __init__(self, chat: Chat, text: str = None):
#         self.chat = chat
#         self.text = text
#
#     class Meta:
#         unknown = EXCLUDE
#
#
# class UpdateObj:
#     def __init__(self, update_id: int, message: Message = None, edited_message: Message = None):
#         self.update_id = update_id
#         self.message = message
#         self.edited_message = edited_message
#
#
# class SendMessageResponse:
#     def __init__(self, ok: bool, result: Message):
#         self.ok = ok
#         self.result = result
#
#     class Meta:
#         unknown = EXCLUDE
#
#
# class GetUpdatesResponse:
#     def __init__(self, ok: bool, result: list[UpdateObj]):
#         self.ok = ok
#         self.result = result
#
#     class Meta:
#         unknown = EXCLUDE
