import datetime
import logging
import os

from menu import MenuFrequency
from restaurant import Restaurant
from slack import send_slack_post

logging.basicConfig(
    level=logging.DEBUG,
    format='{asctime} {levelname} {process:d} --- [{threadName}] {name}:{lineno} {message}',
    style='{',
)

if __name__ == '__main__':
    logging.info(datetime.datetime.now())
    menu_frequency_env = os.environ.get('MENU_FREQUENCY')
    restaurant_env = os.environ.get('RESTAURANT')

    if restaurant_env:
        restaurants = [Restaurant[restaurant_env]]
    elif menu_frequency_env:
        menu_frequency = MenuFrequency[menu_frequency_env]
        restaurants = list(filter(lambda x: x.menu_frequency == menu_frequency, Restaurant))
    else:
        # Default behavior if nothing is specified
        menu_frequency = MenuFrequency.DAILY_LUNCH
        restaurants = list(filter(lambda x: x.menu_frequency == menu_frequency, Restaurant))

    slack_bot_token = os.environ.get('SLACK_BOT_TOKEN')
    slack_channel_id = os.environ.get('SLACK_CHANNEL_ID')

    for restaurant in restaurants:
        menu = restaurant.get_menu()
        logging.info(f'{restaurant.name} {menu}')
        if slack_bot_token and slack_channel_id:
            send_slack_post(
                bot_token=slack_bot_token,
                channel_id=slack_channel_id,
                username=restaurant.name,
                text=menu.text,
                image_urls=menu.image_urls or [],
            )
