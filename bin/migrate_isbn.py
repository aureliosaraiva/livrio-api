# -*- coding: utf-8 -*-
from __future__ import absolute_import
import MySQLdb, MySQLdb.cursors
import requests
import json
DATABASE = {'host': 'localhost', 'user': 'root', 'pass': '', 'base': 'CodeWay_Livrio'}
db = MySQLdb.connect(host=DATABASE['host'],
                     user=DATABASE['user'],
                     passwd=DATABASE['pass'],
                     db=DATABASE['base'],
                     charset='utf8',
                     use_unicode=True)

conn = db.cursor()

query = """SELECT * FROM sys_isbns ORDER by id ASC LIMIT 10"""
conn.execute(query)
result = conn.fetchall()
for row in result:
    payload = {
        'isbn': row[1],
        'isbn_10': row[13],
        'title': row[2],
        'authors': row[3],
        'description': row[6],
        'cover': row[7],
        'page_count': str(row[8]),
        'publisher': row[9],
        'published_date': str(row[11]),
        'categories': [row[14]]
    }

    headers = {
        'Content-type': 'application/json'
    }
    requests.post('http://127.0.0.1:5000/v1/book', data=json.dumps(payload), headers=headers).text

    
    