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
#                       (4) List all purchased modules
#                       (5) Accessing a module
#
# last edit:        29 November 2017
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
import urlparse


BASEURL = "https://prisonerlearning.appspot.com/"
HOME_LINK = BASEURL
ALL_LINK  = BASEURL + "all"
ADD_LINK  = BASEURL + "prisoner"
LOGON = BASEURL + "logon"
ALL_MODULES = BASEURL + "purchased_modules"


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
    loggedOn = False
    nav = {}
    nav['logonlink'] = LOGON
    nav['logonlinktext'] = "Logon"
    nav['homelink'] = HOME_LINK 
    nav['homelinktext'] = "Home"
    nav['newuserlink'] = ADD_LINK 
    nav['newuserlinktext'] = "Add User"
    nav['alluserslink'] = ALL_LINK 
    nav['alluserslinktext'] = "All Users"

    username = self.request.cookies.get("username")
    if username is not None:
        loggedOn = True
        nav['moduleslink'] = ALL_MODULES
        nav['moduleslinktext'] = "Purchased Modules"
        nav['storelink'] = "/store"
        nav['storelinktext'] = "Module Store"

    template = JINJA_ENVIRONMENT.get_template('MainPage.html')
    self.response.write(template.render(nav=nav, loggedOn=loggedOn))


##############################################################################
# Shows all modules in the database in a table
##############################################################################
def renderPurchasedModules(self, username):
    nav = {}
    nav['homelink'] = HOME_LINK
    nav['homelinktext'] = "Home"
    nav['newuserlink'] = ADD_LINK
    nav['newuserlinktext'] = "Add User"
    nav['alluserslink'] = ALL_LINK
    nav['alluserslinktext'] = "All Users"
    
    print(username)
    
    db = connect_to_cloudsql()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM learning_module lm INNER JOIN ' + \
                   'purchased_resources pr ON pr.moduleID = lm.moduleID ' + \
                   'INNER JOIN inmate i ON i.id = pr.inmateID ' + \
                   'WHERE i.username = %s', [str(username),])
    
    modules = []
    for row in cursor:
        module = {}
        module['id'] = int(row[0])
        module['module_name'] = str(row[1])
        module['module_data'] = str(row[2])
        module['module_summary'] = str(row[3])
        module['module_link'] = ALL_MODULES + "/" + str(row[0])
        modules.append(module)
    
    template = JINJA_ENVIRONMENT.get_template('allModules.html')
    self.response.write(template.render(modules=modules, nav=nav))

##############################################################################
# Shows the module with ID = 'id' from the database
##############################################################################
def renderModule(self, id):
    nav = {}
    nav['homelink'] = HOME_LINK
    nav['homelinktext'] = "Home"
    nav['moduleslink'] = ALL_MODULES
    nav['moduleslinktext'] = "Purchased Modules"
 
    # query the database and find the questions associated with the module
    db = connect_to_cloudsql()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM question WHERE moduleID = %s', [str(id)])
    
    questions = []
    for row in cursor:
        question = {}
        question['id'] = int(row[0])
        question['moduleID'] = str(row[1])
        question['prompt'] = str(row[2])
        question['answer'] = str(row[3])
        questions.append(question)
    

    # Query the database for the remaining information on the module
    cursor.execute('SELECT * FROM learning_module WHERE moduleID = %s', [str(id)])

    module = {}
    for row in cursor:
        #module['id'] = int(row[0])
        module['title'] = str(row[1])
        module['data'] = str(row[2])
        module['summary'] = str(row[3])
        module['media'] = str(row[4])
    cursor.close()


    #insert current moduleID into cookie, display quie on another page.
    self.response.set_cookie(key="currentModule", value=id)
    template = JINJA_ENVIRONMENT.get_template('module.html')
    self.response.write(template.render(module=module, nav=nav, questions=questions))
    #self.response.write(json.dumps(module))

##############################################################################
# Shows all users in the database in a table
##############################################################################
def showAllUsers(self):
    nav = {}
    nav['homelink'] = "/adminSplash.html"
    nav['home'] = "Admin Home"
    nav['addUserLink'] = "/prisoner"
    nav['addUser'] = "Add User"


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
    nav['homelink'] = "/adminSplash.html"
    nav['homelinktext'] = "Admin Home"
    nav['alluserslink'] = "/all"
    nav['alluserslinktext'] = "View All Users"

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
    # minit can only be one char
    if len(inmateToAdd['minit']) > 1:
        inmateToAdd['minit'] = inmateToAdd['minit'][0]

    inmateToAdd['lname'] = self.request.get('lname')

    # date must be a valid datestring MM-DD-YYY
    datestr = self.request.get('dob')
    try:
        date = datetime.datetime.strftime(datestr, '%m-%d-&Y')
    except:
        datestr = "2000-01-01"
    inmateToAdd['dob'] = datestr

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
    nav['moduleslink'] = ALL_MODULES
    nav['moduleslinktext'] = "Purchased Modules"
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
    cursor.execute("DELETE FROM inmate WHERE id = %s", [str(id),])
    db.commit()
    db.close()

def renderLogon(self):
    """This end point displays the login page. It is also the redirect
    if username and password cannot be validated"""
    template = JINJA_ENVIRONMENT.get_template("start.html")
    message = {}
    self.response.write(template.render(message=message))


##############################################################################
# render shopping cart page
##############################################################################
def renderShoppingCart(self):
    # navigation links
    nav = {}
    nav['logonlink'] = LOGON
    nav['logonlinktext'] = "Logon"
    nav['homelink'] = HOME_LINK 
    nav['homelinktext'] = "Home"
    nav['newuserlink'] = ADD_LINK 
    nav['newuserlinktext'] = "Add User"
    nav['alluserslink'] = ALL_LINK 
    nav['alluserslinktext'] = "All Users"
    nav['moduleslink'] = ALL_MODULES
    nav['moduleslinktext'] = "Purchased Modules"

    nav['confirm_checkout_link'] = BASEURL + "cart/confirmCheckout"

    # the cookie is send as a '|' delimited string
    # modIDs will be a python list of the ids that were sent in the cookie
    # the empty cookie still contains an empty string so that is what the:w
    # following test is for
    cookieString = self.request.cookies.get("shoppingList")
    modIDs = cookieString.split("|")
    if "" in modIDs:
       cart_empty = {}
       cart_empty['text'] = "No Items in Cart"
       template = JINJA_ENVIRONMENT.get_template('cart.html')
       self.response.write(template.render(nav=nav, cart_empty=cart_empty))
       return


    # show modules whose id's match the ids sent in the cookie
    modules = []

    db = connect_to_cloudsql()
    cursor = db.cursor()
    
    for i in modIDs:
        cursor.execute("SELECT * FROM learning_module WHERE moduleID = %s",
                       [str(i),])
        m = cursor.fetchone()
        module = {}
        module['id'] = int(m[0])
        module['name'] = str(m[1])
        module['remove_link'] = "none"
        modules.append(module)
        

    template = JINJA_ENVIRONMENT.get_template('cart.html')
    self.response.write(template.render(nav=nav, modules=modules))


##############################################################################
# actually add the purchased modules to the user
##############################################################################
def doCheckout(self):
    # navigation links
    nav = {}
    nav['logonlink'] = LOGON
    nav['logonlinktext'] = "Logon"
    nav['homelink'] = HOME_LINK 
    nav['homelinktext'] = "Home"
    nav['newuserlink'] = ADD_LINK 
    nav['newuserlinktext'] = "Add User"
    nav['alluserslink'] = ALL_LINK 
    nav['alluserslinktext'] = "All Users"
    nav['moduleslink'] = ALL_MODULES
    nav['moduleslinktext'] = "Purchased Modules"

    template = JINJA_ENVIRONMENT.get_template('completeCheckout.html')

    cookieString = self.request.cookies.get("checkouts")
    IDs = cookieString.split("|")
    if "" in IDs:
        self.response.write(template.render(nav=nav))
        return

    db = connect_to_cloudsql()
    cursor = db.cursor()

    username = self.request.cookies.get("username")
    cursor.execute("SELECT id FROM inmate WHERE username = %s",
                   [str(username),])
    userID = cursor.fetchone()[0]

    modules = []

    for i in IDs:
        cursor.execute("INSERT INTO purchased_resources " + \
                       "(inmateID, moduleID) VALUES (%s, %s)", 
                       [int(userID), int(i),])
        db.commit()
        cursor.execute("SELECT moduleID, module_name FROM " + \
                       "learning_module WHERE moduleID = %s",
                       [str(i),])
        m = cursor.fetchone()
        module = {}
        module['id'] = int(m[0])
        module['name'] = str(m[1])
        modules.append(module)

    self.response.write(template.render(nav=nav, modules=modules))

    

        

##############################################################################
# POST logon endpoint
#
# This end point handles logging on. Username and password are queried. If found, redirects to
# a splash page showing the user's username and creates a cookie with their username for session
# purposes
##############################################################################
def logonPost(self):
    # connect to database
    db = connect_to_cloudsql()

    # get user data
    logonData = {}
    logonData['username'] = self.request.get('username')
    logonData['password'] = self.request.get('password')

    # find matching query
    cursor = db.cursor()
    cursor.execute("SELECT username FROM inmate WHERE username = %s and password = %s;",
                   (logonData['username'], logonData['password']))
    row = cursor.fetchone()
    cursor.close()

    # test that values are not null -- occurs only if no matching user and password
    if row is not None:
        # if not null render user splash page -- this page also will have session data, specifically the username
        template_values = {'username': row[0]}
        template = JINJA_ENVIRONMENT.get_template('splash.html')
        #username is added to cookie. Can only be transferred over https.
        self.response.set_cookie(key="username", value=row[0], secure=True)
        self.response.write(template.render(template_values))

    # if null redirect back to login page
    else:
        message = {'error': 'username and/or password do not match'}
        template = JINJA_ENVIRONMENT.get_template('start.html')
        self.response.write(template.render(message=message))


##############################################################################
# GET logon endpoint
##############################################################################
def logonGet(self):
    """This end point displays the login page. It is also the redirect
    if username and password cannot be validated"""
    template = JINJA_ENVIRONMENT.get_template("start.html")
    message = {}
    self.response.write(template.render(message=message))


##############################################################################
# render store page
##############################################################################
def renderStorePage(self):
    """"Used to process handle requests relating to the store"""
    
    nav = {}
    nav['homelink'] = HOME_LINK
    nav['homelinktext'] = "Home"
    nav['newuserlink'] = ADD_LINK
    nav['newuserlinktext'] = "Add User"
    nav['alluserslink'] = ALL_LINK
    nav['alluserslinktext'] = "All Users"
    nav['moduleslink'] = ALL_MODULES
    nav['moduleslinktext'] = "Purchased Modules"
    nav['checkout_link'] = BASEURL + "cart"
    mess = {}


    """used to display the store"""
    #connect to database
    db = connect_to_cloudsql()

    username = self.request.cookies.get("username")
    #make query
    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT lm.moduleID, lm.module_name, lm.module_summary FROM learning_module " +\
                   "lm WHERE lm.moduleID NOT IN (SELECT lm.moduleID FROM learning_module lm " +\
                    "INNER JOIN purchased_resources pr ON lm.moduleID = pr.moduleID " +\
                   "INNER JOIN inmate i ON pr.inmateID = i.id WHERE i.username = %s)", [username])
    modules = []
    template = JINJA_ENVIRONMENT.get_template("store.html")
    test = cursor

    if test.fetchone() is None:
        self.response.write(template.render(availablemodules=False, modules=modules, nav=nav))
        return

    # parse query results into dict
    else:
        cursor.execute("SELECT DISTINCT lm.moduleID, lm.module_name, lm.module_summary FROM learning_module " +\
                   "lm WHERE lm.moduleID NOT IN (SELECT lm.moduleID FROM learning_module lm " +\
                    "INNER JOIN purchased_resources pr ON lm.moduleID = pr.moduleID " +\
                   "INNER JOIN inmate i ON pr.inmateID = i.id WHERE i.username = %s)", [username])
        for row in cursor:
            module = {}
            module['moduleID']  = row[0]
            module['module_name'] = row[1]
            module['module_summary'] = row[2]
            modules.append(module)
        self.response.write(template.render(availablemodules=True, modules=modules, nav=nav))


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


class purchasedModules(webapp2.RequestHandler):
    def get(self):
        username = self.request.cookies.get("username")
        if not username:
            renderLogon(self)
        else:
            renderPurchasedModules(self, username)


class ShowModule(webapp2.RequestHandler):
    def get(self, id=None):
        if not id:
            return
        renderModule(self, id)


class Logon(webapp2.RedirectHandler):
    def post(self):
        logonPost(self)

    def get(self):
        logonGet(self)


class Store(webapp2.RequestHandler):

    def get(self):
        renderStorePage(self)


class ShoppingCart(webapp2.RequestHandler):
    def get(self):
        renderShoppingCart(self)


class performCheckout(webapp2.RequestHandler):
    def get(self):
        doCheckout(self)

class Quizzler(webapp2.RequestHandler):
    def get(self):
        """displays the quiz for the user"""
        #get the moduleID from the cookie
        moduleID = self.request.cookies.get("currentModule")
        #make query for the questions using the moduleID
        db = connect_to_cloudsql()
        cursor = db.cursor()
        cursor.execute('SELECT questionID, question FROM question WHERE moduleID = %s ORDER BY questionID', [str(moduleID)])

        questions = []
        for row in cursor:
            question = {}
            question['id'] = int(row[0])
            question['prompt'] = str(row[1])
            questions.append(question)
        cursor.close()

        #render stuff
        template = JINJA_ENVIRONMENT.get_template('quiz.html')
        self.response.write(template.render(questions=questions))

    def post(self):
        """displays the results for the user"""
        #get the moduleID from the cookie
        moduleID =self.request.cookies.get("currentModule")
        #get all the questions for that questions for that module, including questions ids
        db = connect_to_cloudsql()
        cursor = db.cursor()
        cursor.execute('SELECT questionID, answer FROM question WHERE moduleID = %s ORDER BY questionID', [str(moduleID)])
        questions = []
        for row in cursor:
            question = {}
            question['id'] = int(row[0])
            question['answer'] = str(row[1])
            questions.append(question)

        #parse the request
        answered = urlparse.parse_qs(self.request.body)

        # url parse converts the url into a json string, we need a json array
        keys = answered.keys()
        fixed = []
        for key in keys:
            fix = {}
            fix[key] = answered[key]
            fixed.append(fix)

        results = 0
        for i in range(len(questions)):
            if fixed[i][str(questions[i]['id'])][0] == questions[i]['answer']:
                results += 1

        score = float(results) / len(questions)
        stringScore = "{0:.2f}".format(score * 100) + "%"
        #get the module name
        cursor.execute('SELECT module_name FROM learning_module where moduleID=%s', [str(moduleID)])
        row = cursor.fetchone()
        moduleName = row[0]

        #choose a response on if they got more than .8 correct
        message = {}
        message['moduleName'] = moduleName
        message['score'] = stringScore
        if score >= .8:
            message['passed'] = True
        else:
            message['passed'] = False

        template = JINJA_ENVIRONMENT.get_template('quizResults.html')
        self.response.write(template.render(message = message))

class AdminLogon(webapp2.RequestHandler):
    def post(self):
        db = connect_to_cloudsql()

        #get admin creds
        logonData = {}
        logonData['username'] = self.request.get('username')
        logonData['password'] = self.request.get('password')

        cursor = db.cursor()
        cursor.execute("SELECT username FROM admin WHERE username = %s AND password = %s;",
                       (logonData['username'], logonData['password']))
        row = cursor.fetchone()
        cursor.close()

        if row is not None:
            #render admin hompage
            nav = {}
            nav['allUsersLink'] = "/all"
            nav['allUsers'] = 'View All Users'
            nav['addUserLink'] = '/prisoner'
            nav['addUser'] = "Add User"

            username = row[0]
            template = JINJA_ENVIRONMENT.get_template('adminsplash.html')
            self.response.set_cookie(key="username", value=username, secure=True)
            self.response.write(template.render(nav=nav, username=username))

        else:
            message = {'error': 'username and/or password do not macth'}
            template = JINJA_ENVIRONMENT.get_template("adminlogon.html")
            self.response.write(template.render(message=message))


    def get(self):
        """if admin cannot be validated"""
        template = JINJA_ENVIRONMENT.get_template("adminlogon.html")
        message = {}
        self.response.write(template.render(message=message))


class AdminSplash(webapp2.RequestHandler):
    def get(self):
        nav = {}
        nav['allUsersLink'] = "/all"
        nav['allUsers'] = 'View All Users'
        nav['addUserLink'] = '/prisoner'
        nav['addUser'] = "Add User"

        username = self.request.cookies.get("username")

        template = JINJA_ENVIRONMENT.get_template("adminsplash.html")
        self.response.write(template.render(nav=nav, username=username))





# [END RequestHandlers]

# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/prisoner', Add),
    ('/store', Store),
    ('/prisoner/([\w-]+)', Remove),
    ('/start.html', Logon),
    ('/logon', Logon),
    ('/all', ShowAll),
    ('/quiz', Quizzler),
    ('/purchased_modules', purchasedModules),
    ('/purchased_modules/([\w-]+)', ShowModule),
    ('/cart', ShoppingCart),
    ('/cart/confirmCheckout', performCheckout),
    ('/adminlogon', AdminLogon),
    ('/adminSplash.html', AdminSplash),
], debug=True)
# [END app]
