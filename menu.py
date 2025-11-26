from dataclasses import dataclass
from enum import Enum, auto

from instagram import get_instagram_web_profile_info
from kakao import get_kakao_plus_friend_profiles, get_kakao_plus_friend_posts


@dataclass
class Menu:
    text: str
    image_url: str | None


class MenuSource(Enum):
    INSTAGRAM_FEED = auto()
    KAKAO_PLUS_FRIEND_PROFILE_IMAGE = auto()
    KAKAO_PLUS_FRIEND_POST = auto()


class MenuFrequency(Enum):
    DAILY = auto()
    WEEKLY = auto()


def get_menu_from_instagram_feed(username: str) -> Menu:
    last_feed = map(lambda x: x.node,
                    get_instagram_web_profile_info(username).user.edge_owner_to_timeline_media.edges).__next__()
    menu_text = map(lambda x: x.node, last_feed.edge_media_to_caption.edges).__next__().text
    menu_image_url = last_feed.display_url
    return Menu(
        text=menu_text,
        image_url=menu_image_url,
    )


def get_menu_from_kakao_profile(pf_id: str) -> Menu:
    profile = get_kakao_plus_friend_profiles(pf_id)
    profile_card = filter(lambda x: x.type == 'profile', profile.cards).__next__()
    menu_image_url = profile_card.profile.profile_image.url
    return Menu(
        text=profile_card.profile.status_message,
        image_url=menu_image_url,
    )


def get_menu_from_kakao_post(pf_id: str) -> Menu:
    posts = get_kakao_plus_friend_posts(pf_id)
    item = sorted(posts.items, key=lambda x: x.created_at, reverse=True)[0]
    return Menu(
        text=item.title + '\n' + item.contents[0].v,
        image_url=None,
    )
