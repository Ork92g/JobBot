import requests

BOT_TOKEN = "שים כאן את הטוקן שלך"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"

response = requests.get(url)

print(response.text)