import webapp2

import Restify

application = webapp2.WSGIApplication(
    [
        ('/api/.*', Restify.ReST),
        ],
    debug=True)