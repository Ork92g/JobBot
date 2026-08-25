import requests


# ==========================================
# TELEGRAM TEST
# ==========================================

BOT_TOKEN = "8699881487:AAGypXS3cY_AtFlZ-cSFM-JpAsVHLffclEE"
CHAT_ID = "504100909"


def send_test_message():

    url = (
        f"https://api.telegram.org/"
        f"bot{BOT_TOKEN}/sendMessage"
    )

    message = (
        "🧪 SOC JOB HUNTER TEST\n\n"
        "Telegram connection is working.\n\n"
        "Next step: automatic job alerts."
    )

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:

        response = requests.post(
            url,
            data=data,
            timeout=20
        )

        print(
            "HTTP STATUS:",
            response.status_code
        )

        print(
            "RESPONSE:"
        )

        print(
            response.text
        )

        if response.status_code == 200:

            print()
            print(
                "✅ TELEGRAM TEST SUCCESS"
            )

        else:

            print()
            print(
                "❌ TELEGRAM TEST FAILED"
            )

    except requests.RequestException as error:

        print(
            "❌ REQUEST ERROR:"
        )

        print(error)


if __name__ == "__main__":

    send_test_message()