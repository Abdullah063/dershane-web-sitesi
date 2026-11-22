#!/usr/bin/env python3
"""Local HTTP preview with the compression configured for Apache hosting."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import gzip
import io

ROOT=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ROOT),**kwargs)
    def send_head(self):
        path=Path(self.translate_path(self.path))
        if path.is_dir():path=path/'index.html'
        mime=self.guess_type(str(path).split('?',1)[0])
        if path.is_file() and 'gzip' in self.headers.get('Accept-Encoding','') and (mime.startswith('text/') or mime in ('application/javascript','application/json','image/svg+xml')):
            data=gzip.compress(path.read_bytes(),compresslevel=6)
            self.send_response(200)
            self.send_header('Content-Type',mime)
            self.send_header('Content-Encoding','gzip')
            self.send_header('Vary','Accept-Encoding')
            self.send_header('Content-Length',str(len(data)))
            self.end_headers()
            return io.BytesIO(data)
        return super().send_head()
class Server(ThreadingHTTPServer):
    request_queue_size=128
if __name__=='__main__':
    print('Preview http://127.0.0.1:8081 (gzip enabled)',flush=True)
    Server(('127.0.0.1',8081),Handler).serve_forever()
