#!/usr/bin/python3
import http.client
import requests
from urllib.parse import urlencode
import brotli
import json
from datetime import datetime
import time
import traceback


refresh_token = "CfDJ8LzM54WctflCqQQhUN6LfHpRRHUD8U68q8x8Sdf-sVWTn8juqUdjJT6gyq77sYL9vgPksYrczOOZlIzgE_ZK6zPyxiMoSMkIEo2X0lPR-VGkF9MQrQaia6rYmtzEO_Bi-sqIaJV9vSZT_H_m_giDzkSDb9EPsq7Qmqal5JlKxnlSH9iWEOqtrtZCiopUjYvl8D6eHUObZygU9YRiCzUeeabYIcjv-JZL9WLCCCGFUk06GY75L-OT_ZPvrhrXZne6oumGmcxyEMcanjlwW8gwk3lyesTXrGYtv02dMy3LW5ybDyYoSYAYA2DkjSaITMCbt3e0oSTzIX7r9Ss6hcl7q_QRyhpPElz7BSsKCXNsbHhvA08_Zro0TlvNtS57ttjRep5ub_TbETA5e9ZWKuqLmMri_2vZ7UaQMnto3Wd9ixZfSLZGFA6iKc0XoktvBobRYxFP-MYjCv1RStyeW_svJJm2yTEdrUxoOOffigJZGzRCzqwYCgxJKVTH8Iu3qxDKouiALQZfpEfN1Mol_VDwHqI"

earliest_date = datetime.strptime('2020-04-17', '%Y-%m-%d').date()

headers = {
        "Host": "commerce.frisco.pl",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0",
        "Accept": "application/json",
        "Accept-Language" : "en-GB,en;q=0.5",
        "Accept-Encoding" : "gzip, deflate, br",
        "Referer" : "https://www.frisco.pl/",
        "X-Frisco-Visitorid" : "b39c2a22-80da-44e1-91da-30bee282f03f",
        "Content-Type" : "application/json",
        "X-Frisco-Features" : "BalanceAmount=1",
        "X-Frisco-Division" : "WAW",
        "Origin": "https://www.frisco.pl",
        "Connection" : "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "Trailers"
    }



def main():
    print("FRISCO SCRIPT STARTED")
    last_refresh = datetime.strptime('2000-04-15', '%Y-%m-%d')
    while True:
        try:
            if (datetime.now()-last_refresh).total_seconds() >= 300:
                refreshToken()
                last_refresh = datetime.now()
            reservationD = getCurrentReservation()
            rWindow = getFirstAvailable()
            windowD = datetime.strptime(rWindow['startsAt'],'%Y-%m-%dT%H:%M:%S%z').date()
            if (reservationD-windowD).days > 0 and (windowD-earliest_date).days >= 0:
                makeReservation(rWindow)
        except Exception:
            print("ERROR at " + str(datetime.now()))
            traceback.print_exc()
        time.sleep(30)

def getFirstAvailable():
    conn = http.client.HTTPSConnection("www.frisco.pl")
    conn.request("GET", "/api/users/497682/calendar/Van", headers=headers, encode_chunked=False)
    
    response = conn.getresponse()
    decompressed = brotli.decompress(response.read())
    jsonResp = decompressed.decode('utf-8')
    respObj = json.loads(jsonResp)
    return {
        'startsAt' : respObj['firstOpenWindow']['deliveryWindow']['startsAt'],
        'endsAt' : respObj['firstOpenWindow']['deliveryWindow']['endsAt'],
        'warehouse' : respObj['firstOpenWindow']['deliveryWindow']['warehouse'],
        'deliveryMethod' : respObj['firstOpenWindow']['deliveryWindow']['deliveryMethod'],
        'closesAt' : respObj['firstOpenWindow']['deliveryWindow']['closesAt']
    }
    
def makeReservation(payload):
    conn = http.client.HTTPSConnection("commerce.frisco.pl")
    conn.request("POST", "/api/users/497682/cart/reservation", json.dumps(payload), headers=headers, encode_chunked=False)
    response = conn.getresponse()
    if response.status < 300:
        print("SUCCESS: time " + payload['startsAt'] + " reserverd!")
    else:
        print("ERROR during reservation of " + payload['startsAt'])
    
    
    
def getCurrentReservation():
    conn = http.client.HTTPSConnection("commerce.frisco.pl")
    conn.request("GET", "/api/users/497682/cart", headers=headers, encode_chunked=False)
    response = conn.getresponse()
    print(response.status)
    decompressed = brotli.decompress(response.read())
    jsonResp = decompressed.decode('utf-8')
    respObj = json.loads(jsonResp)
    
    print("current best = " + respObj['reservation']['deliveryWindow']['startsAt'] + " TICK: " + str(datetime.now()))
    return datetime.strptime(respObj['reservation']['deliveryWindow']['startsAt'],'%Y-%m-%dT%H:%M:%S%z').date()



def refreshToken():
    global refresh_token
    
    conn = http.client.HTTPSConnection("commerce.frisco.pl")

    refresh_headers = {
        'Host': 'commerce.frisco.pl',
        'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
        'Accept': 'application/json',
        'Accept-Language': 'en-GB,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.frisco.pl/',
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Frisco-Visitorid': 'b39c2a22-80da-44e1-91da-30bee282f03f',
        'Content-Length': 578,
        'Origin': 'https://www.frisco.pl',
        'Connection': 'keep-alive',
    }
    params = {
        'refresh_token' : refresh_token,
        'grant_type' : 'refresh_token'
    }
    conn.request("POST", "/connect/token", urlencode(params), headers=refresh_headers, encode_chunked=False)
    response = conn.getresponse()
    
    decompressed = brotli.decompress(response.read())
    jsonResp = decompressed.decode('utf-8')
    respObj = json.loads(jsonResp)
    
    refresh_token = respObj['refresh_token']
    access_token = respObj['access_token']
    headers['Authorization'] = 'Bearer ' + access_token
    
if __name__ == "__main__":
    main()
