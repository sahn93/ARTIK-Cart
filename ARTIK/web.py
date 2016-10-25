from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess as sp


CONTENT='''
<form action="/" method="post">
  <input type="hidden" name="action" value="start">
  <input type="submit" value="Start">
</form>
<form action="/" method="post">
  <input type="hidden" name="action" value="stop">
  <input type="submit" value="Stop">
</form>
'''
MAINLOOP = None

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    def do_GET(self):
        global MAINLOOP
        if MAINLOOP is None:
            ret = 'NOT Running.'
        else:
            ret = 'Running.'
        ret += CONTENT
        self._set_headers()
        self.wfile.write(ret.encode())
    def do_HEAD(self):
        self._set_headers()
    def do_POST(self):
        global MAINLOOP
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        if post_data == b'action=start' and MAINLOOP is None:
            MAINLOOP = sp.Popen(('python3', '/jubo/main.py'), stdin=sp.PIPE)
            try:
                MAINLOOP.communicate(input=self.client_address[0].encode(),
                                     timeout=3)
            except:
                pass
        elif post_data == b'action=stop' and MAINLOOP is not None:
            MAINLOOP.terminate()
            MAINLOOP = None
        if MAINLOOP is None:
            ret = 'NOT Running.'
        else:
            ret = 'Running.'
        ret += CONTENT
        self._set_headers()
        self.wfile.write(ret.encode())

def run(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == "__main__":
    run()
