from subs.css_template import *
import requests
import json

def get_tokens():
    url =  f"{superset_domain}/api/v1/security/login"
    req = requests.post(url=url, json=connect_params, verify=False)
    j = req.json()
    access_token = j['access_token']
    refresh_token = j['refresh_token']
    print(f'access_token {access_token}')
    print(f'refresh_toke {refresh_token}')
    return access_token, refresh_token