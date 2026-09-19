"""Serve the project preview with byte ranges for seekable MP4 playback."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os,re
class Handler(SimpleHTTPRequestHandler):
 def send_head(self):
  self.byte_range=None
  p=Path(self.translate_path(self.path))
  if p.suffix.lower() not in ('.mp4','.webm') or not p.is_file():return super().send_head()
  size=p.stat().st_size;start=0;end=size-1
  h=self.headers.get('Range')
  if h:
   m=re.fullmatch(r'bytes=(\d*)-(\d*)',h)
   if not m or not any(m.groups()):self.send_error(416);return None
   if m[1]:start=int(m[1]);end=min(int(m[2]),size-1) if m[2] else size-1
   else:start=max(0,size-int(m[2]))
   if start> end or start>=size:self.send_error(416);return None
  f=p.open('rb');f.seek(start);self.byte_range=(start,end)
  self.send_response(206 if h else 200);self.send_header('Content-Type',self.guess_type(str(p)));self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(end-start+1))
  if h:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
  self.end_headers();return f
 def copyfile(self,source,outputfile):
  if self.byte_range is None:return super().copyfile(source,outputfile)
  left=self.byte_range[1]-self.byte_range[0]+1
  try:
   while left:
    chunk=source.read(min(65536,left))
    if not chunk:break
    outputfile.write(chunk);left-=len(chunk)
  except (BrokenPipeError,ConnectionResetError):pass
if __name__=='__main__':
 os.chdir(Path(__file__).resolve().parent.parent)
 ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()
