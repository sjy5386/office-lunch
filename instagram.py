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
            display_url: str
            edge_media_to_caption: EdgeMediaToCaption


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
    if not res.ok:
        print(res.json())
    return dacite.from_dict(InstagramApiResponse, res.json()).data
