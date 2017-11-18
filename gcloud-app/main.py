import os
import urllib
import MySQLdb

import jinja2
import webapp2
import datetime

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# from Google App Engine Sample Code
CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')
CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD')

def connect_to_cloudsql():
    # When deployed to App Engine, the `SERVER_SOFTWARE` environment variable
    # will be set to 'Google App Engine/version'.
    if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
        # Connect using the unix socket located at
        # /cloudsql/cloudsql-connection-name.
        cloudsql_unix_socket = os.path.join(
            '/cloudsql', CLOUDSQL_CONNECTION_NAME)

        db = MySQLdb.connect(
            unix_socket=cloudsql_unix_socket,
            user=CLOUDSQL_USER,
            db="prisonDatabase",
            passwd=CLOUDSQL_PASSWORD)

    # If the unix socket is unavailable, then try to connect using TCP. This
    # will work if you're running a local MySQL server or using the Cloud SQL
    # proxy, for example:
    #
    #   $ cloud_sql_proxy -instances=your-connection-name=tcp:3306
    #
    else:
        db = MySQLdb.connect(
            host='130.211.172.86', user=CLOUDSQL_USER, passwd=CLOUDSQL_PASSWORD)

    return db

class TestPage(webapp2.RequestHandler):
    def get(self):
        db = connect_to_cloudsql()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM inmate')

        users = []
        for row in cursor:
            i = int(row[0])
            f = str(row[1])
            m = str(row[2])
            l = str(row[3])
            d = str(row[4])
            w = int(row[5])
            u = str(row[6])
            p = str(row[7])
            user = {}
            user['id'] = i
            user['fname'] = f
            user['minit'] = m
            user['lname'] = l
            user['dob'] = d
            user['wallet'] = w
            user['username'] = u
            user['password'] = p
            users.append(user)
       
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(users=users))

class LocalTest(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        users = []
        for i in range(2):
            user = {}
            user['id'] = 'i'
            user['fname'] = 'f'
            user['minit'] = 'm'
            user['lname'] = 'l'
            user['dob'] = 'd'
            user['wallet'] = 'w'
            user['username'] = 'u'
            user['password'] = 'p'
            users.append(user)
        self.response.write(template.render(users=users))

# [START app]
app = webapp2.WSGIApplication([
    ('/users', TestPage),
    ('/local', LocalTest),
], debug=True)
# [END app]
