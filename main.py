import datetime
import os

from menu import MenuFrequency
from restaurant import Restaurant
from slack import send_slack_webhook, SlackWebhookPayload

if __name__ == '__main__':
    print(datetime.datetime.now())
    menu_frequency = MenuFrequency[os.environ.get('MENU_FREQUENCY', MenuFrequency.DAILY.name)]
    for restaurant in filter(lambda x: x.menu_frequency == menu_frequency, Restaurant):
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
