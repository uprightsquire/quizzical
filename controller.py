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
import hashlib

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
            cur.execute("INSERT INTO accounts(user,pword,email,type,classes) VALUES ('','','','admin','%s')" % (key))
            con.commit()
            return key
        con.close()
        return "Error"

    def validKey(self, key):
        con=mysql.connect('localhost','root','myosinmysql','quizzical')
        try:
            cur=con.cursor()
            cur.execute("SELECT classes FROM accounts")
            result=cur.fetchall()
        except:
            result=None
        con.close

    def pwhash(self, password):
        return hashlib.sha512((password).encode('utf-8')).hexdigest()
        
        

    @cherrypy.expose
    def register(self, username='', password='', password2='', email='', key='', fname='', sname='', register = False):
        tmpl = loader.load('reg.html')
        status = ''
        if cherrypy.request.method == 'POST':
            if register:
                if username == '' or password == '' or password2 == '' or email == '' or key == '' or fname == '' or sname == '':
                    status = status + 'Please complete each field\n' 
                else:
                    status=status
                if '@' not in email or '.' not in email:
                    status = status + 'Please enter a valid email\n'
                if password != password2:
                    status = status + 'Passwords do not match\n'
                
        return tmpl.generate(status=status, username=username,password=password,password2=password2,email=email,key=key,fname=fname, sname=sname).render('html', doctype='html')

    @cherrypy.expose
    def index(self, username='', password='', valid=False):
        tmpl = loader.load('index.html')
        return tmpl.generate(title='Quizzical', valid = False).render('html', doctype='html')

    @cherrypy.expose
    @require(member_of('god'))
    def globaladmin(self, tab='display', generate=False, delete=False, id=''):
        tmpl = loader.load('god.html')
        key = ''
        content = ''
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
        if tab=='display':
            try:
                con= mysql.connect('localhost','root','myosinmysql','quizzical')
                cur=con.cursor()
                cur.execute("SELECT id,user,pword,email,type,classes FROM accounts")
                content=cur.fetchall()
                con.close()
            except:
                content="Database Error"
        return tmpl.generate(title=title, tab=tab, content = content, key = key).render('html', doctype='html')

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
    
