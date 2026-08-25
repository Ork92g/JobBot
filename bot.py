import requests

BOT_TOKEN = "8699881487:AAGypXS3cY_AtFlZ-cSFM-JpAsVHLffclEE"
CHAT_ID = "504100909"

message = "🤖 הבוט עובד! קיבלתי את ההודעה שלך."

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

response = requests.post(
    url,
    data={
        "chat_id": CHAT_ID,
        "text": message
    }
)

print(response.text)