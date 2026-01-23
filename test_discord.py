import requests

url = "https://discord.com/api/webhooks/1416784239919235152/_4pHEPgqs8Jx3DbFEvFkbU_90cbyIQd0E8Elvypk5scV8asMUSYgkPRP4fPeeQ8W5jkb"

response = requests.post(
    url,
    json={"content": "✅ TEST MESSAGE FROM LOCAL"}
)

print("status:", response.status_code)
print("body:", response.text)
