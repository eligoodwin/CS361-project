##############################################################################
# filename:         main.py
#
# author:           CS 496 Fall 2017 - Group 1:
#                                       Eli Goodwin
#                                       Andrew Lodge
#                                       Robert Scanlon
#                                       Kevin Lewis
#
# description:      Implements a basic admin app for the prison
#                   E-learning system. Features include:
#                       (1) Adding new users
#                       (2) Deleting existing users
#                       (3) Listing all users
#
# last edit:        18 November 2017
##############################################################################

import os
import urllib
import MySQLdb
import jinja2
import webapp2
import datetime
import json
import random
import string

BASEURL   = "https://cs361project.appspot.com/"
HOME_LINK = BASEURL
ALL_LINK  = BASEURL + "all"
ADD_LINK  = BASEURL + "prisoner"

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# from Google App Engine Sample Code
CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')
CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD')


##############################################################################
# returns MySQLdb obj connected to the g cloud database
# code taken from Google App Engine Python Documentation
##############################################################################
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


##############################################################################
# Renders the application home page with links to
# (1) add user
# (2) show all users
##############################################################################
def renderHomePage(self):
    nav = {}
    nav['homelink'] = HOME_LINK 
    nav['homelinktext'] = "Home"
    nav['newuserlink'] = ADD_LINK 
    nav['newuserlinktext'] = "Add User"
    nav['alluserslink'] = ALL_LINK 
    nav['alluserslinktext'] = "All Users"
    template = JINJA_ENVIRONMENT.get_template('MainPage.html')
    self.response.write(template.render(nav=nav))


##############################################################################
# Shows all users in the database in a table
##############################################################################
def showAllUsers(self):
    nav = {}
    nav['homelink'] = HOME_LINK 
    nav['homelinktext'] = "Home"
    nav['newuserlink'] = ADD_LINK 
    nav['newuserlinktext'] = "Add User"
    nav['alluserslink'] = ALL_LINK 
    nav['alluserslinktext'] = "All Users"

    db = connect_to_cloudsql()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM inmate')

    users = []
    for row in cursor:
        user = {}
        user['id'] = int(row[0])
        user['fname'] = str(row[1])
        user['minit'] = str(row[2])
        user['lname'] = str(row[3])
        user['dob'] = str(row[4])
        user['wallet'] = int(row[5])
        user['username'] = str(row[6])
        user['password'] = str(row[7])
        user['remove_link'] = BASEURL + "prisoner/" + str(row[0])
        users.append(user)
   
    template = JINJA_ENVIRONMENT.get_template('allusers.html')
    self.response.write(template.render(users=users, nav=nav))


##############################################################################
# Renders the page where a user can be added
# the fields id, username, and password are auto generated
##############################################################################
def renderAddUser(self):
   nav = {}
   nav['homelink'] = HOME_LINK 
   nav['homelinktext'] = "Home"
   nav['alluserslink'] = ALL_LINK 
   nav['alluserslinktext'] = "All Users"
   template = JINJA_ENVIRONMENT.get_template('adduser.html')
   self.response.write(template.render(nav=nav))


##############################################################################
# adds a new user to the database
# the new user information is passed in the request body
##############################################################################
def addNewUser(self):
    db = connect_to_cloudsql()

    inmateToAdd = {}
    inmateToAdd['fname'] = self.request.get('fname')
    inmateToAdd['minit'] = self.request.get('minit')
    inmateToAdd['lname'] = self.request.get('lname')
    inmateToAdd['dob'] = self.request.get('dob')

    inmateToAdd['username'] = str(inmateToAdd['fname']) + \
                              str(inmateToAdd['minit'])+ \
                              str(inmateToAdd['lname'])
    inmateToAdd['password'] = ''.join(random.choice(string.ascii_uppercase + \
                                                    string.digits) \
                                                    for _ in range(12))
    inmateToAdd['wallet'] = int(self.request.get('wallet'))

    cursor = db.cursor()
    cursor.execute("INSERT INTO inmate (fname, minit, lname, dob, " + \
                   "username, password, wallet) VALUES " + \
                   "(%s, %s, %s, %s, %s, %s, %s);",
                   (inmateToAdd['fname'], inmateToAdd['minit'],
                    inmateToAdd['lname'], inmateToAdd['dob'],
                    inmateToAdd['username'], inmateToAdd['password'],
                    inmateToAdd['wallet']))

    db.commit()
    db.close()

    nav = {}
    nav['homelink'] = HOME_LINK 
    nav['homelinktext'] = "Home"
    nav['newuserlink'] = ADD_LINK 
    nav['newuserlinktext'] = "Add User"
    nav['alluserslink'] = ALL_LINK 
    nav['alluserslinktext'] = "All Users"

    mess = {}
    mess['success'] = "User Added to Database"

    template = JINJA_ENVIRONMENT.get_template('addsuccess.html')
    self.response.write(template.render(nav=nav, mess=mess))


##############################################################################
# renders the page which asks the user to confirm they wish to
# delete the user with ID = 'id'
##############################################################################
def renderConfirmDelete(self, id):
    nav = {}
    nav['homelink'] = HOME_LINK 
    nav['homelinktext'] = "Home"
    nav['newuserlink'] = ADD_LINK 
    nav['newuserlinktext'] = "Add User"
    nav['alluserslink'] = ALL_LINK 
    nav['alluserslinktext'] = "All Users"
    mess = {}
    mess['warning'] = "Are you sure you want to delete the " + \
            "user with ID: " + str(id) + "?"
    mess['buttonText'] = "Yes"
    link = {}
    link['deleteLink'] = BASEURL + "prisoner/" + str(id) 
    template = JINJA_ENVIRONMENT.get_template('confirmDelete.html')
    self.response.write(template.render(mess=mess, link=link, nav=nav))


##############################################################################
# removes the user with ID = 'id' from the database then
# renders the page confirming the delete took place
##############################################################################
def deleteUser(self, id):
    db = connect_to_cloudsql()
    cursor = db.cursor()
    cursor.execute("DELETE FROM inmate WHERE id = %s", str(id))
    db.commit()
    db.close()

    mess = {}
    mess['header'] = "User Removed from Database"

    nav = {}
    nav['homelink'] = HOME_LINK 
    nav['homelinktext'] = "Home"
    nav['newuserlink'] = ADD_LINK 
    nav['newuserlinktext'] = "Add User"
    nav['alluserslink'] = ALL_LINK 
    nav['alluserslinktext'] = "All Users"

    template = JINJA_ENVIRONMENT.get_template('deleteSuccess.html')
    self.response.write(template.render(nav=nav, mess=mess))


# [START RequestHandlers]
class MainPage(webapp2.RequestHandler):
    def get(self):
        renderHomePage(self)

class ShowAll(webapp2.RequestHandler):
    def get(self):
        showAllUsers(self)


class Add(webapp2.RequestHandler):
    def get(self):
        renderAddUser(self)

    def post(self):
        addNewUser(self)


class Remove(webapp2.RequestHandler):
    def get(self, id=None):
        if not id:
            return
        renderConfirmDelete(self, id)


    def post(self, id=None):
        if not id:
            return
        deleteUser(self, id)
# [END RequestHandlers]

# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/prisoner', Add),
    ('/prisoner/([\w-]+)', Remove),
    ('/all', ShowAll),
], debug=True)
# [END app]
