import os
import urllib

from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class TestPage(webapp2.RequestHandler):
    def get(self):
        template_values = {
            'greeting' : "Hello, World!"
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


# [START app]
app = webapp2.WSGIApplication([
    ('/', TestPage),
], debug=True)
# [END app]
