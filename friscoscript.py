#!/usr/bin/python3
import http.client
import requests
from urllib.parse import urlencode
import brotli
import json
from datetime import datetime
import time
import traceback


#refresh_token =  "CfDJ8DuWbvEMiqhCk2GST7qFG6dknZCq0ILtlLwiGsFYeXea39IxOlPPOfhvEchdsvRDfAgv5nHuYn_T9OhRsA-D_-ONL4yXDfYx3j_KNhKLvCKTDOA8x-aQf6VA6G8Ur4QAff68ymXSCfJDFhQNBMB652mscchdlfgYA5EaBdWSbZBIXzrDNlmDF6bT_X_A-DD-Tse9Uq8_mm4YNQSnZ4sR0aHymNsd8G8ZglgaEE9BmlqTDgrEJQO-mWKZ0WyqjiFV3g1WGsUdg0jebLBd-SHCXPiNnhWYHQizAP2Ju7ewOAyKgysYQR-Ie7viJzqQGd8RfzKhK7MjQgLHK49RjEoolf56-lCj_g0Qh8-V-17qp4XUSOyHcU-QlEPoM5Ee3KTkazg3ei50ac9jogxXdI-hR2o"

#user_id = '497682'
#visitor_id = 'bc76629f-520d-4222-8201-a9e849075f19'


refresh_token =  "CfDJ8DuWbvEMiqhCk2GST7qFG6dk7tYNUM6_37msi8tBzL-2b94y1WDVrLxy7pr5xo-fqDVYVkHE7tsnLbCOKIbIpcNdG9z9MkEMgmBHuUu7Gf5iEmhv8jAKl_o9nkle33pDc1Shz0siPZxK1602wCu5c5qcHaCVEqUI0Y6Wik1fB3z_SK1lbe6Fmh6GS2zlOeJX4qTk-DohshvjFDptRqrRUXF9SrvYDl7WKY560Hxtgqj9Lk1jhCmFB6zKSxBHaYxrjz_gJVsQ9ETpr_h6WiDVI9s_8BkubXPq-ACUGKmdvww9Wx59DFH9dVgfltDA7sYM4y0BItE0vgHb9wEo6zATG5v0Fld5mRV6V3h-Zw_67zRtmTwfp8TWhshLyysFAzfsgwkJHfkDZivqyS9YOrGQQOA"

user_id = '511768'
visitor_id = '2cd92709-e160-4a3a-8ae3-571a33b0bc1e'


earliest_date = datetime.strptime('2020-10-26', '%Y-%m-%d').date()

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
    global refresh_token
    #with open("token.txt", "r") as f:
    #    refresh_token = f.read()
    
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
        time.sleep(15)

def getFirstAvailable():
    conn = http.client.HTTPSConnection("www.frisco.pl")
    conn.request("GET", f"/api/users/{user_id}/calendar/Van", headers=headers, encode_chunked=False)
    
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
    conn.request("POST", f"/api/users/{user_id}/cart/reservation", json.dumps(payload), headers=headers, encode_chunked=False)
    response = conn.getresponse()
    if response.status < 300:
        print("SUCCESS: time " + payload['startsAt'] + " reserverd!")
    else:
        print("ERROR during reservation of " + payload['startsAt'])
    
    
def getCurrentReservation():
    conn = http.client.HTTPSConnection("commerce.frisco.pl")
    conn.request("GET", f"/api/users/{user_id}/cart", headers=headers, encode_chunked=False)
    response = conn.getresponse()
    print(response.status)
    decompressed = brotli.decompress(response.read())
    jsonResp = decompressed.decode('utf-8')
    respObj = json.loads(jsonResp)
    
    print("current best = " + respObj['reservation']['deliveryWindow']['startsAt'] + " TICK: " + str(datetime.now()))
    return datetime.strptime(respObj['reservation']['deliveryWindow']['startsAt'],'%Y-%m-%dT%H:%M:%S%z').date()



def refreshToken():
    global refresh_token
    global visitor_id
    
    conn = http.client.HTTPSConnection("commerce.frisco.pl")

    refresh_headers = {
        'Host': 'commerce.frisco.pl',
        'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
        'Accept': 'application/json',
        'Accept-Language': 'en-GB,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.frisco.pl/',
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Frisco-Visitorid': visitor_id,
        'Content-Length': 450,
        'Origin': 'https://www.frisco.pl',
        'Connection': 'keep-alive',
    }
    params = {
        'refresh_token' : refresh_token,
        'grant_type' : 'refresh_token'
    }
    conn.request("POST", "/connect/token", urlencode(params), headers=refresh_headers, encode_chunked=False)
    response = conn.getresponse()
    
    response_body = response.read()
    
    if response.status >= 300:
        print(response_body)
    
    decompressed = brotli.decompress(response_body)
    jsonResp = decompressed.decode('utf-8')
    respObj = json.loads(jsonResp)
    
    refresh_token = respObj['refresh_token']
    access_token = respObj['access_token']
    headers['Authorization'] = 'Bearer ' + access_token
    with open("token.txt", "w") as f:
        f.write(refresh_token)
    
if __name__ == "__main__":
    main()
