import datetime
import logging
import os

import requests

from menu import MenuFrequency
from restaurant import Restaurant
from slack import send_slack_webhook, SlackWebhookPayload

logging.basicConfig(
    level=logging.DEBUG,
    format='{asctime} {levelname} {process:d} --- [{threadName}] {name}:{lineno} {message}',
    style='{',
)

if __name__ == '__main__':
    logging.info(datetime.datetime.now())
    logging.info(requests.get('https://icanhazip.com').text)
    menu_frequency_env = os.environ.get('MENU_FREQUENCY')
    restaurant_env = os.environ.get('RESTAURANT')

    if restaurant_env:
        restaurants = [Restaurant[restaurant_env]]
    elif menu_frequency_env:
        menu_frequency = MenuFrequency[menu_frequency_env]
        restaurants = list(filter(lambda x: x.menu_frequency == menu_frequency, Restaurant))
    else:
        # Default behavior if nothing is specified
        menu_frequency = MenuFrequency.DAILY
        restaurants = list(filter(lambda x: x.menu_frequency == menu_frequency, Restaurant))

    for restaurant in restaurants:
        menu = restaurant.get_menu()
        logging.info(f'{restaurant.name} {menu}')
        slack_webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
        if slack_webhook_url:
            send_slack_webhook(
                payload=SlackWebhookPayload(
                    text=menu.text,
                    username=restaurant.name,
                    blocks=[
                        SlackWebhookPayload.SectionBlock(
                            text=SlackWebhookPayload.TextObject(
                                type='plain_text',
                                text=menu.text,
                            ),
                        ),
                        SlackWebhookPayload.ImageBlock(
                            alt_text=menu.text,
                            image_url=menu.image_url,
                        ),
                    ] if menu.image_url else None,
                ),
                webhook_url=slack_webhook_url,
            )
