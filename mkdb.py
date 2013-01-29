#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script to create database

import MySQLdb as mdb
import sys
import hashlib

con = mdb.connect('localhost','root','myosinmysql','quizzical');

passhash = hashlib.sha512(("pass").encode('utf-8')).hexdigest()

print len(passhash)

with con:
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS accounts(Id INT PRIMARY KEY AUTO_INCREMENT,user VARCHAR(16),pword VARCHAR(128),email VARCHAR(50),fname VARCHAR(50),sname VARCHAR(50),type VARCHAR(5),classkey VARCHAR(128), classes TEXT)")
    cur.execute("INSERT INTO accounts(user,pword,email,type) VALUES('admin','%s','zwatts@gmail.com','god')" % (passhash))
