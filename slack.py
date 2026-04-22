import json
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

import requests

SLACK_REPLY_IMAGES_PER_MESSAGE = 3


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


def send_slack_message(
        payload: SlackMessagePayload,
        bot_token: str,
        channel_id: str,
        thread_ts: str | None = None,
) -> str:
    body = json.loads(json.dumps(payload, default=lambda x: x.__dict__))
    body['channel'] = channel_id
    if thread_ts:
        body['thread_ts'] = thread_ts
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
    return data['ts']


def send_slack_post(
        bot_token: str,
        channel_id: str,
        username: str,
        text: str,
        image_urls: list[str],
):
    total = len(image_urls)
    parent_blocks: list[SlackMessagePayload.Block] = [
        SlackMessagePayload.SectionBlock(
            text=SlackMessagePayload.TextObject(type='plain_text', text=text),
        ),
    ]
    if image_urls:
        parent_blocks.append(
            SlackMessagePayload.ImageBlock(
                alt_text=f'{text} (1/{total})',
                image_url=image_urls[0],
            ),
        )
    parent_ts = send_slack_message(
        payload=SlackMessagePayload(text=text, username=username, blocks=parent_blocks),
        bot_token=bot_token,
        channel_id=channel_id,
    )

    reply_image_urls = image_urls[1:]
    for chunk_start in range(0, len(reply_image_urls), SLACK_REPLY_IMAGES_PER_MESSAGE):
        chunk = reply_image_urls[chunk_start:chunk_start + SLACK_REPLY_IMAGES_PER_MESSAGE]
        send_slack_message(
            payload=SlackMessagePayload(
                text=text,
                username=username,
                blocks=[
                    SlackMessagePayload.ImageBlock(
                        alt_text=f'{text} ({chunk_start + offset + 2}/{total})',
                        image_url=image_url,
                    )
                    for offset, image_url in enumerate(chunk)
                ],
            ),
            bot_token=bot_token,
            channel_id=channel_id,
            thread_ts=parent_ts,
        )
