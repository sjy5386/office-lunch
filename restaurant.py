import traceback
from enum import Enum

from menu import MenuSource, get_menu_from_kakao_profile, get_menu_from_kakao_post, MenuFrequency, \
    get_daily_menu_from_instagram_feed, get_weekly_menu_from_instagram_feed, Menu


class Restaurant(Enum):
    알찬푸드_구내식당 = (MenuSource.INSTAGRAM_FEED, 'your_table__', MenuFrequency.DAILY_LUNCH)
    알찬푸드_구내식당_저녁 = (MenuSource.INSTAGRAM_FEED, 'your_table__', MenuFrequency.DAILY_DINNER)
    알찬푸드_구내식당_주간식단표 = (MenuSource.INSTAGRAM_FEED, 'your_table__', MenuFrequency.WEEKLY)
    우림_더이룸푸드 = (MenuSource.INSTAGRAM_FEED, 'theirum_food', MenuFrequency.DAILY_LUNCH)
    우림_더이룸푸드_저녁 = (MenuSource.INSTAGRAM_FEED, 'theirum_food', MenuFrequency.DAILY_DINNER)
    우림_더이룸푸드_식단표 = (MenuSource.INSTAGRAM_FEED, 'theirum_food', MenuFrequency.WEEKLY)
    정원정_한식뷔페 = (MenuSource.KAKAO_PLUS_FRIEND_POST, '_Zlxgxhxj', MenuFrequency.DAILY)
    한신IT타워_구내식당 = (MenuSource.KAKAO_PLUS_FRIEND_PROFILE_IMAGE, '_QRALxb', MenuFrequency.DAILY)

    def __init__(self, menu_source: MenuSource, menu_source_id: str, menu_frequency: MenuFrequency):
        self.menu_source = menu_source
        self.menu_source_id = menu_source_id
        self.menu_frequency = menu_frequency

    def get_menu(self) -> Menu:
        try:
            if self.menu_source == MenuSource.INSTAGRAM_FEED:
                if self.menu_frequency in (MenuFrequency.DAILY, MenuFrequency.DAILY_LUNCH, MenuFrequency.DAILY_DINNER):
                    return get_daily_menu_from_instagram_feed(self.menu_source_id)
                elif self.menu_frequency == MenuFrequency.WEEKLY:
                    return get_weekly_menu_from_instagram_feed(self.menu_source_id)
            elif self.menu_source == MenuSource.KAKAO_PLUS_FRIEND_PROFILE_IMAGE:
                return get_menu_from_kakao_profile(self.menu_source_id)
            elif self.menu_source == MenuSource.KAKAO_PLUS_FRIEND_POST:
                return get_menu_from_kakao_post(self.menu_source_id)
            raise Exception(f'Unknown menu source {self.menu_source}')
        except Exception as e:
            print(''.join(traceback.format_exception(e)))
            return Menu(
                text=str(e),
                image_url=None,
            )
