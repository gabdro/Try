#Library
import requests
import oauthlib
import oauthlib.oauth2
import json
from requests_oauthlib import OAuth2Session
import urllib

import operator
from urllib.parse import urljoin

import passwd

from _mastodon import *

d = register_app(passwd.account_id,passwd.host)
#辞書で{client_id,client_secret,id,redirect_uri}

ci,cs,email,host =d['client_id'],d['client_secret'],passwd.email,passwd.host
pwd=passwd.passwd
host = passwd.host
token = fetch_token(ci,cs,email,pwd,host)


masdn = Mstdn(token)
hosturl = passwd.hosturl

listener = MstdnStreamListner()
stream = MstdnStream(hosturl, token['access_token'], listener)

import os
if os.path.exists("log/") == False:
    os.mkdir("log")

while(True):
    listener = MstdnStreamListner()
    stream = MstdnStream(hosturl, token['access_token'], listener)
    try:
        stream.public()
    except:
        print("止まったのでリスタートかけるのです(´･ω･｀)")
