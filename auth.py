# -*- encoding: UTF-8 -*-
#
# Form based authentication for CherryPy. Requires the
# Session tool to be loaded.
#

import cherrypy
import os
import urllib
from genshi.template import TemplateLoader
import MySQLdb as mysql


db_server = "localhost"
db_account = "root"
db_pass = "myosinsmysql"
db_name = "quizzical"

SESSION_KEY = '_cp_username'

loader = TemplateLoader(
    os.path.join(os.path.dirname(__file__), 'templates'),
    auto_reload = True)


def account_type(user):
    """
    Returns the type of account for a given user
    """
    try:
        con = mysql.connect(db_server,db_account,db_pass,db_name)
        cur = con.cursor()
        cur.execute("SELECT type FROM accounts WHERE user = '%s'" % (user))
        result = cur.fetchone()
        con.close()
    except:
        return 'x'
    return result[0]

def check_credentials(username, password):
    """Verifies credentials for username and password.
    Returns None on success or a string describing the error on failure"""
    if username in ('zwatts', 'steve') and password == 'x':
        return None
    else:
        return u"Incorrect username or password."

def check_auth(*args, **kwargs):
    """A tool that looks in config for 'auth.require'. If found and it
    is not None, a login is required and the entry is evaluated as a list of
    conditions that the user must fulfill"""
    conditions = cherrypy.request.config.get('auth.require', None)
    get_params = urllib.quote(cherrypy.request.request_line.split()[1])
    if conditions is not None:
        username = cherrypy.session.get(SESSION_KEY)
        if username:
            cherrypy.request.login = username
            for condition in conditions:
                # A condition is just a callable that returns true or false
                if not condition():
                    raise cherrypy.HTTPRedirect("/auth/login?from_page=%s" %get_params)
        else:
            raise cherrypy.HTTPRedirect("/auth/login?from_page=%s" %get_params)
    
cherrypy.tools.auth = cherrypy.Tool('before_handler', check_auth)

def require(*conditions):
    """A decorator that appends conditions to the auth.require config
    variable."""
    def decorate(f):
        if not hasattr(f, '_cp_config'):
            f._cp_config = dict()
        if 'auth.require' not in f._cp_config:
            f._cp_config['auth.require'] = []
        f._cp_config['auth.require'].extend(conditions)
        return f
    return decorate


def member_of(groupname):
    """
    Returns wheather user is belongs to account type
    """
    return lambda: groupname == account_type(cherrypy.request.login)

def name_is(reqd_username):
    return lambda: reqd_username == cherrypy.request.login


# Controller to provide login and logout actions

class AuthController(object):
    
    def on_login(self, username):
        """Called on successful login"""
    
    def on_logout(self, username):
        """Called on logout"""
    
    def get_loginform(self, username, msg="Enter login information", from_page="/"):
        tmpl = loader.load('login.html')
        return tmpl.generate(msg = msg, from_page=from_page).render('html', doctype='html')

    @cherrypy.expose
    def login(self, username=None, password=None, from_page="/"):
        if username is None or password is None:
            return self.get_loginform("", from_page=from_page)
        
        error_msg = check_credentials(username, password)
        if error_msg:
            return self.get_loginform(username, error_msg, from_page)
        else:
            cherrypy.session[SESSION_KEY] = cherrypy.request.login = username
            cherrypy.login=username
            if account_type(username) == "god":
              raise cherrypy.HTTPRedirect("/globaladmin")
            else:
              raise cherrypy.HTTPRedirect("www.%s.com" %account_type(username))
              
    @cherrypy.expose
    def logout(self, from_page="/"):
        sess = cherrypy.session
        username = sess.get(SESSION_KEY, None)
        sess[SESSION_KEY] = None
        if username:
            cherrypy.request.login = None
            self.on_logout(username)
        raise cherrypy.HTTPRedirect(from_page or "/")
