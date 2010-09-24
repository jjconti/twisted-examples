PORT = 8090

from BaseHTTPServer import BaseHTTPRequestHandler
import SocketServer
import cgi

class MyHandler(BaseHTTPRequestHandler):

	def do_GET(self):
		self.send_response(200)
		self.end_headers()
        	self.wfile.write('1.9.1')

	def do_POST(self):
		form = cgi.FieldStorage(
			fp=self.rfile,
			headers=self.headers,
			environ={'REQUEST_METHOD':'POST',
			'CONTENT_TYPE':self.headers['Content-Type'],
			})
		print form
		self.send_response(200)
		self.end_headers()
		self.wfile.write('1.9.1')

httpd = SocketServer.TCPServer(("", PORT), MyHandler)

print "serving at port", PORT
httpd.serve_forever()

