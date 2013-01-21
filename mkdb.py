#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import sys

con = mdb.connect('localhost','root','myosinmysql','quizzical');

with con:
	cur = con.cursor()
	cur.execute("CREATE TABLE IF NOT EXISTS accounts(Id INT PRIMARY KEY AUTO_INCREMENT, user VARCHAR(16), pword VARCHAR(16), email VARCHAR(50), type VARCHAR(5), classes TEXT)")
	cur.execute("INSERT INTO accounts(user,pword,email,type) VALUES('zwatts','x','zwatts@gmail.com','god')")


