import requests

url = "https://test.api.amadeus.com/v1/security/oauth2/token"
headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}
data = {
    "grant_type": "client_credentials",
    "client_id": "EcGG2CCqQeWtbWPpBURxOa27xsCh64KN",
    "client_secret": "GPLXA8d3ccDr67FA"
}

response = requests.post(url, headers=headers, data=data)
if response.status_code == 200:
    access_token = response.json().get("access_token")
    print("Access Token:", access_token)
else:
    print("Error:", response.json())
