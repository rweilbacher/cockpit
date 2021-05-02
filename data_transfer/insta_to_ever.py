from urllib.parse import parse_qs
import requests
from requests_oauthlib import OAuth1
# Access to my personal secrets
from credentials import instapaper

oauth = OAuth1(instapaper.clientId, instapaper.clientSecret)
baseUrl = 'https://www.instapaper.com'

params = {}
params["x_auth_username"] = instapaper.username
params["x_auth_password"] = instapaper.password
params["x_auth_mode"] = 'client_auth'

authEndpoint = '/api/1/oauth/access_token'

r = requests.post(url=baseUrl+authEndpoint, auth=oauth, data=params)
credentials = parse_qs(r.content)
oauth_token = credentials.get(b'oauth_token')[0].decode("utf-8")
oauth_secret = credentials.get(b'oauth_token_secret')[0].decode("utf-8")

oauth = OAuth1(instapaper.clientId, instapaper.clientSecret+"&"+oauth_secret, oauth_token)
verify_url = baseUrl + "/api/1/account/verify_credentials"
r = requests.post(verify_url, auth=oauth)
# list_url = 'https://www.instapaper.com/api/1/bookmarks/list'
# r = requests.post(list_url, auth=oauth)
print(r)