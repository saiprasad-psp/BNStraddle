# -*- coding: utf-8 -*-
"""
Created on Fri Apr 16 11:21:15 2021

@author: Sai.Pydisetty
"""
import yfinance as yf
import os
import requests
import pandas as pd
from datetime import date
from datetime import time
import datetime
import time as t
import platform
from nsepy.derivatives import get_expiry_date
from fyers_api import fyersModel
#from nsepython import nse_quote_ltp
# NOTE Install fyers_api => python -m pip install fyers_api

fyers = None
qty = 25
parent_dir = os.path.normpath(os.getcwd() + os.sep + os.pardir)
current_dir = os.path.normpath(os.getcwd())
if platform.system() == 'Linux' :
    parent_dir = os.path.normpath(os.getcwd()) + '/Algo'
    current_dir = os.path.normpath(os.getcwd()) + '/Algo/BNFStraddle'
    
def telegram_bot_sendtext(bot_message):
    bot_token = open( os.path.join(parent_dir, 'bot_token.txt'), 'r').read().strip()
    bot_chatID = open(os.path.join(parent_dir, 'bot_chatID.txt'), 'r').read().strip()
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()

def get_current_price(symbol):
    ticker = yf.Ticker(symbol)
    todays_data = ticker.history(period='1d')
    #print(todays_data['Close'][0])
    return todays_data['Close'][0]
   
def place_order(symbol):
    ret = fyers.place_orders(
                    token = access_token,
                    data = {
                    "symbol" : symbol,
                    "qty" : qty,
                    "type" : 2,
                    "side" : -1,
                    "productType" : "INTRADAY",
                    "limitPrice" : 0,
                    "stopPrice" : 0,
                    "disclosedQty" : 0,
                    "validity" : "DAY",
                    "offlineOrder" : "False",
                    "stopLoss" : 0,
                    "takeProfit" : 0
                    })

    if ret['code'] != 200:
        print('error occurred: ',symbol + ' ' + ret["message"])
        resp = telegram_bot_sendtext('error occurred: '+ symbol + ' ' + ret["message"])
        return
    telegram_bot_sendtext(symbol + ' Sell ' + ret["message"])
    print(ret)
    
def place_sl_order(symbol, price ):
    ret = fyers.place_orders(
                    token = access_token,
                    data = {
                    "symbol" : symbol,
                    "qty" : qty,
                    "type" : 3,
                    "side" : 1,
                    "productType" : "INTRADAY",
                    "limitPrice" : 0,
                    "stopPrice" : price,
                    "disclosedQty" : 0,
                    "validity" : "DAY",
                    "offlineOrder" : "False",
                    "stopLoss" : 0,
                    "takeProfit" : 0
                    })
    if ret['code'] != 200:
        print('error occurred: ',symbol + ' ' + ret["message"])
        telegram_bot_sendtext('error occurred: '+ symbol + ' ' + ret["message"])
        return
    telegram_bot_sendtext(symbol + ' SL-M ' + ret["message"])
    print(ret)

def get_exp(mnth):
    weekly_expirys = get_expiry_date(year=today.year,stock = False, month=mnth)
    for weekly_exp in weekly_expirys:
        diff_days = (weekly_exp - today).days
        if diff_days >= 0 and diff_days < 7 :
            expiry = weekly_exp
            return(expiry)
        
def get_symbols():
    global today, expiry, symbol_ce, symbol_pe
    expiry = None
    expiry = get_exp(today.month)
    if expiry == None:
        expiry = get_exp(today.month+1)
        
    mnth_expirys = get_expiry_date(year=today.year,stock = True, month=today.month)
    for e_mnth_date in mnth_expirys:
        e_mnth_date = e_mnth_date
   
    strike_price = int(round(get_current_price('^NSEBANK'),-2))
    if e_mnth_date == expiry:
        symbol_ce = 'NSE:BANKNIFTY' + expiry.strftime("%y%b").upper() + str(strike_price) + 'CE'
        symbol_pe = 'NSE:BANKNIFTY' + expiry.strftime("%y%b").upper() + str(strike_price) + 'PE'
    else:
        if platform.system() == 'Linux' :
            symbol_ce = 'NSE:BANKNIFTY' + expiry.strftime("%y%-m%d") + str(strike_price) + 'CE'
            symbol_pe = 'NSE:BANKNIFTY' + expiry.strftime("%y%-m%d") + str(strike_price) + 'PE'
        else:
            symbol_ce = 'NSE:BANKNIFTY' + expiry.strftime("%y%#m%d") + str(strike_price) + 'CE'
            symbol_pe = 'NSE:BANKNIFTY' + expiry.strftime("%y%#m%d") + str(strike_price) + 'PE'
            
def main():
    global expiry, today, symbol_ce, symbol_pe
    global e_mnth_date
    global fyers
    global access_token
    access_token = open(os.path.join(parent_dir, 'access_token.txt'), 'r').read().strip()
    # is_async = False #(By default False, Change to True for asnyc API calls.)
    fyers = fyersModel.FyersModel()
    today = date.today()
    get_symbols()
    print(symbol_ce)
    print(symbol_pe)
    place_order(symbol_ce)
    place_order(symbol_pe)
    data = fyers.tradebook(token=access_token)
    trade_book = data['data']['tradeBook']

    df = pd.DataFrame(trade_book)
    for i in range(len(df)):
        #print(df.loc[i]['symbol'])
        if df.loc[i]['symbol'] == symbol_ce:
            place_sl_order(symbol_ce, round(df.loc[i]['tradePrice'] * 1.25 , 1))
        elif df.loc[i]['symbol'] == symbol_pe:
            place_sl_order(symbol_pe, round(df.loc[i]['tradePrice'] * 1.25 , 1))

if __name__ == '__main__':
    order_placed = False
    print("Script Running.")
    while datetime.datetime.now().time() < time(9,20) or datetime.datetime.now().time() >= time(9,25):
        t.sleep(10)
    print("Starting BNF Straddle.")
    try:
        while not order_placed:
            main()
            order_placed = True
    except Exception as e:
        msg = "Error occurred in main - " + str(e)
        print(msg)
        telegram_bot_sendtext(msg)
        