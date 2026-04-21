import logging
import os
from dataclasses import dataclass

import dacite
import requests
from fake_useragent import UserAgent


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
            accessibility_caption: str | None
            edge_media_to_caption: EdgeMediaToCaption
            taken_at_timestamp: int
            thumbnail_resources: list[ThumbnailResource]
            pinned_for_users: list[PinnedForUser]
            edge_sidecar_to_children: EdgeSidecarToChildren | None = None

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
class EdgeSidecarToChildren:
    edges: list[Edge]

    @dataclass
    class Edge:
        node: Node

        @dataclass
        class Node:
            display_url: str


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
    ua = UserAgent()
    res = requests.get(url, params={
        'username': username
    }, headers={
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'X-IG-App-ID': instagram_app_id,
        'Referer': f'https://www.instagram.com/',
    })
    logging.info(f'{res.status_code}: {res.text}')
    res.raise_for_status()
    profile_info = dacite.from_dict(InstagramApiResponse, res.json()).data
    if profile_info is None:
        raise ValueError(f'Instagram profile info not found: {username}')
    return profile_info


def get_instagram_post_image_urls(post: EdgeOwnerToTimelineMedia.Edge.Node) -> list[str]:
    if post.edge_sidecar_to_children and post.edge_sidecar_to_children.edges:
        return [child.node.display_url for child in post.edge_sidecar_to_children.edges]
    return [post.display_url]
