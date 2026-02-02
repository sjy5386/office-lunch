import logging
from dataclasses import dataclass

import dacite
import requests


@dataclass
class KakaoPlusFriendProfiles:
    cards: list[Card]

    @dataclass
    class Card:
        seq: int
        type: str
        profile: Profile | None

        @dataclass
        class Profile:
            id: int
            name: str | None
            status_message: str | None
            profile_image: ProfileImage | None

            @dataclass
            class ProfileImage:
                id: int
                type: str
                url: str
                xlarge_url: str
                large_url: str
                medium_url: str
                small_url: str


def get_kakao_plus_friend_profiles(pf_id: str) -> KakaoPlusFriendProfiles:
    url = f'https://pf.kakao.com/rocket-web/web/v2/profiles/{pf_id}'
    res = requests.get(url)
    logging.info(f'{res.status_code}: {res.text}')
    res.raise_for_status()
    return dacite.from_dict(KakaoPlusFriendProfiles, res.json())


@dataclass
class KakaoPlusFriendPosts:
    items: list[Item]

    @dataclass
    class Item:
        id: int
        title: str
        contents: list[Content]
        is_private: bool
        created_at: int
        updated_at: int | None
        published_at: int

        @dataclass
        class Content:
            t: str
            v: str


def get_kakao_plus_friend_posts(pf_id: str) -> KakaoPlusFriendPosts:
    url = f'https://pf.kakao.com/rocket-web/web/profiles/{pf_id}/posts'
    res = requests.get(url, params={
        'includePinnedPost': 'true',
    })
    logging.info(f'{res.status_code}: {res.text}')
    res.raise_for_status()
    return dacite.from_dict(KakaoPlusFriendPosts, res.json())
