import requests


BOT_TOKEN = "8699881487:AAGypXS3cY_AtFlZ-cSFM-JpAsVHLffclEE"

CHAT_ID = "504100909"


def send_message(message):

    url = (
        f"https://api.telegram.org/bot"
        f"{BOT_TOKEN}/sendMessage"
    )

    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": False
    }

    response = requests.post(
        url,
        data=data,
        timeout=20
    )

    print(
        "Telegram:",
        response.status_code
    )

    print(
        response.text
    )


if __name__ == "__main__":

    send_message(
        "🚀 SOC Job Hunter עובד!\n\n"
        "Telegram connection successful."
    )