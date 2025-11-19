from enum import Enum, auto

import easyocr

from kakao import get_kakao_plus_friend_profiles, get_kakao_plus_friend_posts


class MenuSource(Enum):
    KAKAO_PLUS_FRIEND_PROFILE_IMAGE = auto()
    KAKAO_PLUS_FRIEND_POST = auto()


def ocr(image_url: str):
    reader = easyocr.Reader(['ko'])
    text = reader.readtext(image_url)
    return ' '.join(map(lambda x: x[1], text))


def get_menu_from_kakao_profile(pf_id: str):
    profile = get_kakao_plus_friend_profiles(pf_id)
    profile_card = filter(lambda x: x.type == 'profile', profile.cards).__next__()
    menu_image_url = profile_card.profile.profile_image.url
    menu_text = ocr(menu_image_url)
    return menu_text + ' ' + menu_image_url


def get_menu_from_kakao_post(pf_id: str) -> str:
    posts = get_kakao_plus_friend_posts(pf_id)
    item = sorted(posts.items, key=lambda x: x.created_at, reverse=True)[0]
    return item.contents[0].v
