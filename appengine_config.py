from gaesessions import SessionMiddleware

# suggestion: generate your own random key using os.urandom(64)
# WARNING: Make sure you run os.urandom(64) OFFLINE and copy/paste the output to
# this file.  If you use os.urandom() to *dynamically* generate your key at
# runtime then any existing sessions will become junk every time you start,
# deploy, or update your app!
import os
COOKIE_KEY = '\x9ex\x1d\xabg5x\xc21h\xa7*\xe4\xad\x8a\x1fs1c\x90\xf6\xddn\x8c\xc7\x1d\xb5T1<La\x07\x8c\x95#\xe0\xfdz\x91/\xd3\x0c\xdd\x1f\xc5\x9a\x0b$."vl$\x07\x12\x08\xd6\x00\'\x85\xa8\t\xe9'

def webapp_add_wsgi_middleware(app):
  from google.appengine.ext.appstats import recording
  app = SessionMiddleware(app, cookie_key=COOKIE_KEY)
  app = recording.appstats_wsgi_middleware(app)
  return app
