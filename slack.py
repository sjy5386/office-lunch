import json
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

import requests


@dataclass
class SlackWebhookPayload:
    text: str
    username: str | None
    blocks: list[Block] | None = None

    @dataclass
    class Block(metaclass=ABCMeta):
        @property
        @abstractmethod
        def type(self) -> str:
            pass

    @dataclass
    class ImageBlock(Block):
        alt_text: str
        image_url: str
        type: str = 'image'

    @dataclass
    class SectionBlock(Block):
        text: SlackWebhookPayload.TextObject
        type: str = 'section'

    @dataclass
    class TextObject:
        type: str
        text: str


def send_slack_webhook(payload: SlackWebhookPayload, webhook_url: str):
    requests.post(webhook_url, json=json.loads(json.dumps(payload, default=lambda x: x.__dict__)))
