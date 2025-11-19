import requests


def send_slack_webhook(text: str, username: str, webhook_url: str):
    requests.post(webhook_url, json={
        'text': text,
        'username': username,
    })
