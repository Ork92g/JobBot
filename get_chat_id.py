import requests

BOT_TOKEN = "8699881487:AAGypXS3cY_AtFlZ-cSFM-JpAsVHLffclEE"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

response = requests.get(url)

print(response.text)