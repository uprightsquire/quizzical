#!/usr/bin/env python3
#
#CherryPy controller

import operator, os, sys
import cherrypy
from genshi.template import TemplateLoader
from genshi.template import MarkupTemplate
import MySQLdb as mysql
from random import randrange as randrange
from auth import *


current_dir = os.path.dirname(os.path.abspath(__file__))

loader = TemplateLoader(
    os.path.join(os.path.dirname(__file__), 'templates'),
    auto_reload = True
)

class Root(object):
 
    auth = AuthController()

    def __init__(self):
        return

    def keygen(self):
        con=mysql.connect('localhost','root','myosinmysql','quizzical')
        key = str(hex(int(randrange(int(0xFFFFFF)))))[2:].upper()
        result = ()
        try:
            cur=con.cursor()
            cur.execute("SELECT classes FROM accounts WHERE classes = '%s'" % (key))
            result = cur.fetchall()
        except:
            con.rollback()
        if len(result) == 0:
            cur.execute("INSERT INTO accounts(user,pword,email,type,classkey) VALUES ('','','','teach','%s')" % (key))
            con.commit()
            return key
        con.close()
        return "Error"

    
        

    @cherrypy.expose
    def register(self, username='', password='', password2='', email='', key='', fname='', sname='', register = False):
        tmpl = loader.load('reg.html')
        status = ''
        if cherrypy.request.method == 'POST':
            if register:
                con=mysql.connect('localhost','root','myosinmysql','quizzical')
                try:
                    cur=con.cursor()
                    cur.execute("SELECT user FROM accounts WHERE classkey = '%s'" % (key))
                    result=cur.fetchone()
                    con.close()
                    if result[0] == '':
                        valid = True
                    else:
                        valid = False
                except:
                    valid = False
                try:
                    con=mysql.connect('localhost','root','myosinmysql','quizzical')
                    cur=con.cursor()
                    cur.execute("SELECT COUNT(*) FROM accounts WHERE user = '%s'" % (username))
                    result=cur.fetchone()
                    con.close()
                    if int(result[0])>0:
                        valid = False
                        status = status + "Username already in use\n"
                except:
                    valid = False
                if username == '' or password == '' or password2 == '' or email == '' or key == '' or fname == '' or sname == '':
                    status = status + 'Please complete each field\n'
                    valid = False
                if '@' not in email or '.' not in email:
                    status = status + 'Please enter a valid email\n'
                    valid = False
                if password != password2:
                    status = status + 'Passwords do not match\n'
                    valid = False
                if valid == True:
                    try:
                        con= mysql.connect('localhost','root','myosinmysql','quizzical')
                        cur=con.cursor()
                        cur.execute("UPDATE accounts SET user = '%s', pword = '%s', fname = '%s', sname = '%s', email = '%s' WHERE classkey = '%s'" % (username, pwhash(password2), fname, sname, email, key))      
                        status = "Account Created"
                        con.commit()
                        con.close()
                    except Exception as e:
                        status = "Database Error: %s" % repr(e)
                if valid == True:
                    raise cherrypy.HTTPRedirect('/auth/login')
        return tmpl.generate(status=status, username=username,password=password,password2=password2,email=email,key=key,fname=fname, sname=sname).render('html', doctype='html')

    @cherrypy.expose
    def index(self, username='', password='', valid=False):
        tmpl = loader.load('index.html')
        return tmpl.generate(title='Quizzical', valid = False).render('html', doctype='html')

    @cherrypy.expose
    @require(member_of('god'))
    def globaladmin(self, tab='display', generate=False, delete=False, account=False, id='', oldpassword = '', password1 = '', password2 = ''):
        tmpl = loader.load('god.html')
        key = ''
        content = ''
        status = ''
        title='Global Admin'
        if cherrypy.request.method == 'POST':
            if generate:
                key = "Key: "+str(self.keygen())
            if delete:
                con=mysql.connect('localhost','root','myosinmysql','quizzical')
                cur=con.cursor()
                if type(id)!=type(list()):
                    cur.execute("DELETE FROM accounts WHERE id = '%d'" % int(id))
                else:
                    for i in id:
                        cur.execute("DELETE FROM accounts WHERE id = '%d'" % int(i))
                con.commit()  
                con.close()
            if account:
                status = 'blank'
                try:
                    con = mysql.connect("localhost","root","myosinmysql","quizzical")
                    cur = con.cursor()
                    cur.execute("SELECT pword FROM accounts WHERE user = '%s'" % (cherrypy.request.login))
                    result = cur.fetchone()
                    con.close()
                    if result[0] == pwhash(oldpassword):
                        if password1 == password2:
                            try:
                                con= mysql.connect('localhost','root','myosinmysql','quizzical')
                                cur=con.cursor()
                                cur.execute("UPDATE accounts SET pword = '%s' WHERE user = '%s'" % (pwhash(password2), cherrypy.request.login))      
                                status = "Password changed"
                                con.commit()
                                con.close()        
                            except Exception as e:
                                status = "Database Error: %s" % repr(e)
                                con.rollback()
                                con.close()
                        else:
                            status = "New password not re-entered correctly"
                    else: 
                        status = "Password incorrect"
                except Exception as e:
                    status ="Database Error %s" % repr(e)
                
        if tab=='display':
            try:
                con= mysql.connect('localhost','root','myosinmysql','quizzical')
                cur=con.cursor()
                cur.execute("SELECT id,user,email,fname,sname,type,classkey FROM accounts")
                content=cur.fetchall()
                con.close()
            except:
                content="Database Error"
        return tmpl.generate(title=title, tab=tab, content = content, key = key, status=status).render('html', doctype='html')

def main():
    
    cherrypy.config.update({
    'tools.encode.on': True, 'tools.encode.encoding': 'utf-8',
    'tools.decode.on': True,
    'tools.trailing_slash.on': True,
    'tools.staticdir.root': os.path.abspath(os.path.dirname(__file__)),
    'tools.sessions.on': True,
    'tools.auth.on': True
    })

    cherrypy.quickstart(Root(), '/', {
    '/templates': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': os.path.join(current_dir, 'templates')
    }
    })

if __name__ == '__main__':
    main()
    
