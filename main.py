import datetime
import os

from menu import MenuFrequency
from restaurant import Restaurant
from slack import send_slack_webhook, SlackWebhookPayload

if __name__ == '__main__':
    print(datetime.datetime.now())
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
        print(restaurant.name, menu)
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
