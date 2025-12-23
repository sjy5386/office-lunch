import datetime
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
    DAILY_LUNCH = auto()
    DAILY_DINNER = auto()
    WEEKLY = auto()


class MenuNotFoundException(Exception):
    pass


def get_daily_menu_from_instagram_feed(username: str) -> Menu:
    last_feed = sorted(filter(lambda x: not x.pinned_for_users,
                              map(lambda x: x.node,
                                  get_instagram_web_profile_info(username).user.edge_owner_to_timeline_media.edges)),
                       key=lambda x: x.taken_at_timestamp, reverse=True)[0]
    taken_at_timestamp = datetime.datetime.fromtimestamp(last_feed.taken_at_timestamp)
    if datetime.datetime.now() - taken_at_timestamp > datetime.timedelta(hours=6):
        raise MenuNotFoundException('Not found instagram feed')
    menu_text = next(map(lambda x: x.node,
                         last_feed.edge_media_to_caption.edges)).text if last_feed.edge_media_to_caption.edges else username
    menu_image_url = last_feed.display_url
    return Menu(
        text=menu_text,
        image_url=menu_image_url,
    )


def get_weekly_menu_from_instagram_feed(username: str) -> Menu:
    last_feed = next(filter(lambda x: x.pinned_for_users,
                            map(lambda x: x.node,
                                get_instagram_web_profile_info(username).user.edge_owner_to_timeline_media.edges)))
    taken_at_timestamp = datetime.datetime.fromtimestamp(last_feed.taken_at_timestamp)
    if datetime.datetime.now() - taken_at_timestamp > datetime.timedelta(weeks=1):
        print(taken_at_timestamp)
        raise MenuNotFoundException('Not found instagram feed')
    menu_text = next(map(lambda x: x.node,
                         last_feed.edge_media_to_caption.edges)).text if last_feed.edge_media_to_caption.edges else username
    menu_image_url = last_feed.display_url
    return Menu(
        text=menu_text,
        image_url=menu_image_url,
    )


def get_menu_from_kakao_profile(pf_id: str) -> Menu:
    profile = get_kakao_plus_friend_profiles(pf_id)
    profile_card = next(filter(lambda x: x.type == 'profile', profile.cards))
    menu_image_url = profile_card.profile.profile_image.url
    return Menu(
        text=profile_card.profile.status_message,
        image_url=menu_image_url,
    )


def get_menu_from_kakao_post(pf_id: str) -> Menu:
    posts = get_kakao_plus_friend_posts(pf_id)
    item = sorted(posts.items, key=lambda x: x.created_at, reverse=True)[0]
    created_at = datetime.datetime.fromtimestamp(item.created_at / 1000)
    if datetime.datetime.now() - created_at > datetime.timedelta(hours=6):
        print(created_at)
        raise MenuNotFoundException('Not found kakao talk channel post')
    return Menu(
        text=item.title + '\n' + item.contents[0].v,
        image_url=None,
    )
