"""Production WSGI entry point.

waitress-serve --listen=0.0.0.0:5000 astranotes.wsgi:app
"""

from astranotes.web.app import create_app

app = create_app()
