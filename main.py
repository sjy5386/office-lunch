import datetime
import logging
import os

from menu import MenuFrequency
from restaurant import Restaurant
from slack import send_slack_webhook, SlackWebhookPayload

SLACK_IMAGE_BLOCKS_PER_MESSAGE = 3

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

    slack_webhook_url = os.environ.get('SLACK_WEBHOOK_URL')

    for restaurant in restaurants:
        menu = restaurant.get_menu()
        logging.info(f'{restaurant.name} {menu}')
        if slack_webhook_url:
            image_urls = menu.image_urls or []
            image_url_chunks = [
                image_urls[index:index + SLACK_IMAGE_BLOCKS_PER_MESSAGE]
                for index in range(0, len(image_urls), SLACK_IMAGE_BLOCKS_PER_MESSAGE)
            ] or [[]]

            for index, image_url_chunk in enumerate(image_url_chunks):
                blocks = []
                if index == 0:
                    blocks.append(
                        SlackWebhookPayload.SectionBlock(
                            text=SlackWebhookPayload.TextObject(
                                type='plain_text',
                                text=menu.text,
                            ),
                        ),
                    )
                blocks.extend([
                    SlackWebhookPayload.ImageBlock(
                        alt_text=f'{menu.text} ({index * SLACK_IMAGE_BLOCKS_PER_MESSAGE + image_index + 1}/{len(image_urls)})',
                        image_url=image_url,
                    ) for image_index, image_url in enumerate(image_url_chunk)
                ])
                send_slack_webhook(
                    payload=SlackWebhookPayload(
                        text=menu.text,
                        username=restaurant.name,
                        blocks=blocks,
                    ),
                    webhook_url=slack_webhook_url,
                )
