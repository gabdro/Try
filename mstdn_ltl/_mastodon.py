# -*- coding: utf-8 -*-

#Library
import requests
import oauthlib
import oauthlib.oauth2
import json
from requests_oauthlib import OAuth2Session
import urllib

import operator
from urllib.parse import urljoin

def register_app(client_name, host, redirect_uris='urn:ietf:wg:oauth:2.0:oob', scopes='read write follow'):
    data = {
        'client_name': client_name,
        'redirect_uris': redirect_uris,
        'scopes': scopes,
    }
    resp = requests.post("https://{host}/api/v1/apps".format(host=host), data=data)
    resp.raise_for_status()
    return resp.json()


def fetch_token(client_id, client_secret, email, password, host, scope=('read', 'write', 'follow')):
    token_url = "https://{host}/oauth/token".format(host=host)
    client = oauthlib.oauth2.LegacyApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(token_url=token_url, username=email, password=password,
                              client_id=client_id, client_secret=client_secret, scope=scope)
    return token


class Mstdn:
    def __init__(self, token, scheme='https', host='friends.nico'):
        self.scheme = scheme
        self.host = host
        self.session = requests.Session()
        self.session.headers.update({'Authorization': 'Bearer ' + token['access_token']})

    def _build_url(self, path):
        return urllib.parse.urlunsplit([self.scheme, self.host, path, '', ''])

    def _request(self, method, url, data=None, params=None):
        kwargs = {
            'data': data or {},
            'params': params or {}
        }
        resp = self.session.request(method, url, **kwargs)
        resp.raise_for_status()
        return resp

    def home_timeline(self):
        url = self._build_url('/api/v1/timelines/home')
        return self._request('get', url)

    def toot(self, status):
        url = self._build_url('/api/v1/statuses')
        return self._request('post', url, data={'status': status})


class MstdnStream:
    """Mastodon Steam Class

    Usage::

        >>> from mstdn import MstdnStream, MstdnStreamListner
        >>> listener = MstdnStreamListner()
        >>> stream = MstdnStream('https://pawoo.net', 'your-access-token', listener)
        >>> stream.public()

    """
    def __init__(self, base_url, access_token, listener):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Authorization': 'Bearer ' + access_token})
        self.listener = listener

    def public(self):
        url = urljoin(self.base_url, '/api/v1/streaming/public/local')
        resp = self.session.get(url, stream=True)
        resp.raise_for_status()
        event = {}
        for line in resp.iter_lines():
            line = line.decode('utf-8')

            if not line:
                # End of content.
                method_name = "on_{event}".format(event=event['event'])
                print(method_name)
                f = operator.methodcaller(method_name, event['data'])
                #print("(´･ω･｀)",event['content'])
                f(self.listener)
                # refreash
                event = {}
                continue

            if line.startswith(':'):
                # TODO: Handle heatbeat
                print('startwith ":" {line}'.format(line=line))
            else:
                key, value = line.split(': ', 1)
                if key in event:
                    event[key] += value
                else:
                    event[key] = value


class MstdnStreamListner:

    def on_update(self, data):
        #res = json.dumps(data)
        f = open("log/"+data[6:13]+".json",'w')
        print(data,file=f)
        f.close()
        #pass


    def on_notification(self, data):
        f = open("log/"+data[6:13]+".json",'w')
        print(data,file=f)
        f.close()
        #print(data["content"])

    def on_delete(self, data):
        print("Deleted: {id}".format(id=data))
