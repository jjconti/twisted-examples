PORT = 8090

from BaseHTTPServer import BaseHTTPRequestHandler
import SocketServer
import urlparse
from twitterupdates import api as twitter

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urlparse.parse_qs(self.path[2:])
        for key,val in parsed.items():
            v,t = val[0].split('@')
            y = t[:4]
            m = t[4:6]
            d = t[6:8]
            h = t[8:10]
            mm = t[10:12]
            s = t[12:14]
            twitter.update_status("%s: %s - %s/%s/%s %s:%s:%s" % (key, v, d, m, y, h, mm, s))
        self.send_response(200)


httpd = SocketServer.TCPServer(("", PORT), MyHandler)

print "serving at port", PORT
httpd.serve_forever()

