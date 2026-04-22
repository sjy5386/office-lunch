import json
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

import requests


@dataclass
class SlackMessagePayload:
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
        text: SlackMessagePayload.TextObject
        type: str = 'section'

    @dataclass
    class TextObject:
        type: str
        text: str


def send_slack_message(payload: SlackMessagePayload, bot_token: str, channel_id: str):
    body = json.loads(json.dumps(payload, default=lambda x: x.__dict__))
    body['channel'] = channel_id
    response = requests.post(
        'https://slack.com/api/chat.postMessage',
        headers={
            'Authorization': f'Bearer {bot_token}',
            'Content-Type': 'application/json; charset=utf-8',
        },
        json=body,
    )
    response.raise_for_status()
    data = response.json()
    if not data.get('ok'):
        raise RuntimeError(f'Slack API error: {data.get("error")}')
