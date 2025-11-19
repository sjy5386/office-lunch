import datetime
import os

from restaurant import Restaurant
from slack import send_slack_webhook

if __name__ == '__main__':
    print(datetime.datetime.now())
    for restaurant in list(Restaurant):
        menu = restaurant.get_menu()
        print(restaurant.name, menu)
        slack_webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
        if slack_webhook_url:
            send_slack_webhook(
                username=restaurant.name,
                text=menu,
                webhook_url=slack_webhook_url,
            )
