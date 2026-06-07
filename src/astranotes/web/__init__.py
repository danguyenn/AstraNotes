"""Web layer: Flask routes, templates, and static assets.

Routes are thin — they parse the request, call NoteService, and render a
template. Anything more involved than that belongs in a service, not a route.
"""
