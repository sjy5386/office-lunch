import logging
import os
from dataclasses import dataclass

import dacite
import requests


@dataclass
class InstagramApiResponse:
    data: InstagramProfileInfo | None
    message: str | None
    status: str


@dataclass
class InstagramProfileInfo:
    user: User

    @dataclass
    class User:
        edge_owner_to_timeline_media: EdgeOwnerToTimelineMedia


@dataclass
class EdgeOwnerToTimelineMedia:
    count: int
    edges: list[Edge]

    @dataclass
    class Edge:
        node: Node

        @dataclass
        class Node:
            id: str
            shortcode: str
            display_url: str
            accessibility_caption: str
            edge_media_to_caption: EdgeMediaToCaption
            taken_at_timestamp: int
            thumbnail_resources: list[ThumbnailResource]
            pinned_for_users: list[PinnedForUser]

            @dataclass
            class ThumbnailResource:
                src: str
                config_width: int
                config_height: int

            @dataclass
            class PinnedForUser:
                id: str
                is_verified: bool
                profile_pic_url: str
                username: str


@dataclass
class EdgeMediaToCaption:
    edges: list[Edge]

    @dataclass
    class Edge:
        node: Node

        @dataclass
        class Node:
            text: str


def get_instagram_web_profile_info(
        username: str,
        instagram_app_id: str = os.environ.get('INSTAGRAM_APP_ID', '936619743392459'),
) -> InstagramProfileInfo:
    url = 'https://www.instagram.com/api/v1/users/web_profile_info/'
    res = requests.get(url, params={
        'username': username,
    }, headers={
        'X-IG-App-ID': instagram_app_id,  # useragent mismatch
    })
    logging.info(f'{res.status_code}: {res.text}')
    res.raise_for_status()
    return dacite.from_dict(InstagramApiResponse, res.json()).data
