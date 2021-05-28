# -*- coding: utf-8 -*-
"""
Created on Fri Apr 16 11:21:15 2021

@author: Sai.Pydisetty
"""

import requests
import csv
import re
import json
import os
import platform

from fyers_api import accessToken
# NOTE Install fyers_api => python -m pip install fyers_api

current_dir = '/home/ubuntu/Algo'
if platform.system() != 'Linux' :
    current_dir = os.path.normpath(os.getcwd())

def telegram_bot_sendtext(bot_message):
    bot_token = open(os.path.join(current_dir, 'bot_token.txt'), 'r').read().strip()
    bot_chatID = open(os.path.join(current_dir,'bot_chatID.txt'), 'r').read().strip()
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)
    return response.json()

def get_token(app_id, app_secret, fyers_id, password, pan_dob):
    appSession = accessToken.SessionModel(app_id, app_secret)
    response = appSession.auth()
    if response["code"] != 200:
        return response
        # sys.exit()

    auth_code = response["data"]["authorization_code"]

    appSession.set_token(auth_code)

    generateTokenUrl = appSession.generate_token()
    # webbrowser.open(generateTokenUrl, new=1)
    headers = {
        "accept": "*/*",
        "accept-language": "en-IN,en-US;q=0.9,en;q=0.8",
        "content-type": "application/json; charset=UTF-8",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "referrer": generateTokenUrl
    }
    payload = {"fyers_id": fyers_id, "password": password,
               "pan_dob": pan_dob, "appId": app_id, "create_cookie": False}
    result = requests.post("https://api.fyers.in/api/v1/token",
                           headers=headers, json=payload, allow_redirects=True)
    if result.status_code != 200:
        print('error occurred status code :: ', result.status_code)
        return
    print(result.json())
    result_url = result.json()["Url"]
    token_re = re.search(r'access_token=(.*?)&', result_url, re.I)
    if token_re:
        telegram_bot_sendtext("Token Generated Successfully.")
        return token_re.group(1)
    return "error"


def main():
    # access_token from the redirect url
    user = json.loads(open(os.path.join(current_dir,'userinfo.json'), 'r').read().strip())
    # NOTE Contents of userinfo.json
    # {
    #     "app_id": "<YourFyersAppID>",
    #     "app_secret": "<YourFyersAppSecretForAboveFyersID>",
    #     "fyers_id": "<YourFyersLoginID>",
    #     "password": "<YourPassword>",
    #     "pan_or_dob": "<YourPanNumberORDateOfBirthIn_dd-mm-yyyy_format>"
    # }
    access_token = get_token(app_id=user['app_id'], app_secret=user['app_secret'],
                             fyers_id=user['fyers_id'], password=user['password'], pan_dob=user['pan_or_dob'])
    
    with open(os.path.join(current_dir,'access_token.txt'), 'w') as wr1:
        wr = csv.writer(wr1)
        wr.writerow([access_token])

if __name__ == '__main__':
    token_gen = False
    while token_gen == False:
       main()
       token_gen = True
        