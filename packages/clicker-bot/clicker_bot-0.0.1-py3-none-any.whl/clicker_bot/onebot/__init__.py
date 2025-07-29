import datetime
import json
from datetime import timezone, timedelta
from typing import Literal

from pydantic import BaseModel, field_validator


class Post(BaseModel):
    time: datetime.datetime
    self_id: int

    @field_validator("time", mode="before")
    @classmethod
    def time_offset(cls, v):
        if isinstance(v, (int, float)):
            return datetime.datetime.fromtimestamp(v, timezone(timedelta(hours=8)))


class MessageSegment(BaseModel):
    type: str
    data: dict


class Sender(BaseModel):
    user_id: int
    nickname: str


class MessagePost(Post):
    post_type: Literal["message"]
    message_type: Literal["group", "public"]
    sub_type: Literal["friend", "normal", "anonymous", "group_self", "notice"]
    message_id: int
    user_id: int
    message: list[MessageSegment]
    raw_message: str
    font: int
    sender: Sender


def validate_post(s) -> Post:
    post_type = json.loads(s).get("post_type")

    post_type_mapping = {
        "message": MessagePost
    }

    if post_type is not None:
        if post_type in post_type_mapping:
            return post_type_mapping[post_type].model_validate_json(s)
    raise ValueError
