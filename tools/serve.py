#!/usr/bin/env python3
"""Preview the built site (_site/) locally:  python3 tools/serve.py  ->  http://localhost:8000

Run tools/build.py first (and again after each change).

Like `python3 -m http.server`, but with byte-range support (needed for videos
to play in Chrome) and caching turned off (so a normal refresh shows changes).
"""
import os
import re
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_site")
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("Accept-Ranges", "bytes")
        super().end_headers()

    def send_head(self):
        match = re.fullmatch(r"bytes=(\d*)-(\d*)", self.headers.get("Range", ""))
        path = self.translate_path(self.path)
        if not match or not os.path.isfile(path):
            return super().send_head()
        size = os.path.getsize(path)
        start_s, end_s = match.groups()
        if start_s:
            start, end = int(start_s), int(end_s) if end_s else size - 1
        else:  # suffix range: last N bytes
            start, end = max(0, size - int(end_s or 0)), size - 1
        end = min(end, size - 1)
        if start > end:
            self.send_error(416, "Requested Range Not Satisfiable")
            return None
        f = open(path, "rb")
        f.seek(start)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        self._remaining = end - start + 1
        return f

    def copyfile(self, source, outputfile):
        remaining = getattr(self, "_remaining", None)
        if remaining is None:
            return super().copyfile(source, outputfile)
        while remaining > 0:
            chunk = source.read(min(64 * 1024, remaining))
            if not chunk:
                break
            outputfile.write(chunk)
            remaining -= len(chunk)
        self._remaining = None


if __name__ == "__main__":
    if not os.path.isdir(ROOT):
        sys.exit("No _site/ folder yet: run the build first (see README).")
    server = ThreadingHTTPServer(("127.0.0.1", PORT), partial(Handler, directory=ROOT))
    print(f"Serving the site at http://localhost:{PORT}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
