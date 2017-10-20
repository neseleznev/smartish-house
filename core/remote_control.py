import urllib.request
from urllib.error import URLError

from core.common import Singleton

API_ROOT = 'http://127.0.0.1:8081/requests/'
API_COMMAND = API_ROOT + 'status.json?command='


class VLC(metaclass=Singleton):

    def __init__(self):
        # create a password manager
        password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()

        # Add the username and password.
        # If we knew the realm, we could use it instead of None.
        password_mgr.add_password(None, API_ROOT, '', 'pass')
        handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
        self.opener = urllib.request.build_opener(handler)

    def open(self, url):
        try:
            self.opener.open(url)
        except URLError as ex:
            print(ex)

    def fullscreen(self):
        self.open(API_COMMAND + 'fullscreen')

    # interval could be +1M -1M +5S -5S, etc.
    def seek(self, interval: str):
        self.open(API_COMMAND + 'seek&val=' + interval)

    def pause(self):
        self.open(API_COMMAND + 'pl_pause')

    def stop(self):
        self.open(API_COMMAND + 'pl_stop')

    # interval could be +5 -5 30%, etc.
    def volume(self, interval: str):
        self.open(API_COMMAND + 'volume&val=' + interval)
