import sys
from os.path import dirname, join

root_path = dirname(__file__)
sys.path.insert(0, join(root_path, 'lib'))

# import httplib
import tornado
import tornado.gen
import tornado.httpclient
import tornado.ioloop
import tornado.web
from tornado.httpclient import HTTPRequest

try:
    from shlex import quote  # For Python 3
    from urllib.request import urlopen, Request  # Python 3
except ImportError:
    from urllib2 import urlopen, Request  # Python 2
    from pipes import quote  # For Python 2

try:
    from tornado.curl_httpclient import CurlAsyncHTTPClient as AsyncHTTPClient
except ImportError:
    from tornado.simple_httpclient import SimpleAsyncHTTPClient as AsyncHTTPClient


class Proxy(object):
    def __init__(self):
        print('init')

    def _on_proxy(self, response):
        print('proxy callback')
        if response.error:
            print("proxy failed , error: %s" % response.error)
        else:
            print("%s" % response.body)


    def doproxy(self, url):
        try:
            AsyncHTTPClient().fetch(
                HTTPRequest(url = url,
                            headers = {'X-ACCESS-TOKEN': 'ZkFpU25rWUFHWVFxSkxpeUhlb1VWU1lPbHp3bkpzblc='},
                            follow_redirects = False),
                self._on_proxy)
        except tornado.httpclient.HTTPError as httperror:
            if hasattr(httperror, "response") and httperror.response:
                self._on_proxy(httperror.response)
            else:
                print("Tornado signalled HTTPError %s", httperror)


if __name__ == '__main__':
    print('begin')
    proxy = Proxy()
    proxy.doproxy('http://127.0.0.1:18888/api/query/**')
    tornado.ioloop.IOLoop.instance().start()