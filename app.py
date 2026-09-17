import json,mimetypes,secrets,sys
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlparse
sys.path.insert(0,str(Path(__file__).parent))
from watchdog.core import parse_pdf_bytes,parse_fixture_text,audit
ROOT=Path(__file__).parent; SESSIONS={}
class H(BaseHTTPRequestHandler):
 def log_message(self,*a): pass
 def send(self,code,data,ctype='application/json'):
  b=data if isinstance(data,bytes) else (json.dumps(data).encode() if ctype=='application/json' else data.encode()); self.send_response(code); self.send_header('Content-Type',ctype); self.send_header('Content-Length',len(b)); self.end_headers(); self.wfile.write(b)
 def do_GET(self):
  p=urlparse(self.path).path
  if p=='/': return self.send(200,(ROOT/'templates/index.html').read_text(),'text/html; charset=utf-8')
  if p=='/api/demo':
   picks=[]
   for supplier in ['northstar-produce','harbor-foods']:
    for month in ['2026-07','2026-09']:
     path=next((ROOT/'data/synthetic/invoices').glob(f'{supplier}-{month}-*.pdf')); inv=parse_pdf_bytes(path.read_bytes(),path.name)
     if supplier=='harbor-foods' and month=='2026-09':
      inv['items'][3]['sku']=''; inv['items'][3]['description']='Long Grain Basmati Rice'
     picks.append(inv)
   return self.send(200,audit(picks))
  if p.startswith('/static/'):
   f=ROOT/p.lstrip('/'); return self.send(200,f.read_bytes(),mimetypes.guess_type(str(f))[0] or 'application/octet-stream')
  self.send(404,{'error':'Not found'})
 def do_POST(self):
  if self.path=='/api/audit':
   try:
    n=int(self.headers.get('Content-Length','0')); payload=json.loads(self.rfile.read(n)); inv=[]
    for f in payload.get('files',[]):
     import base64
     data=base64.b64decode(f['data']); inv.append(parse_pdf_bytes(data,f['name']))
    if len(inv)<2: raise ValueError('Upload at least two invoices from the same supplier.')
    return self.send(200,audit(inv))
   except Exception as e:return self.send(400,{'error':str(e)})
  if self.path=='/api/clear': return self.send(200,{'cleared':True})
  self.send(404,{'error':'Not found'})
if __name__=='__main__':
 print('Invoice Watchdog running at http://127.0.0.1:8000'); ThreadingHTTPServer(('127.0.0.1',8000),H).serve_forever()
