#!/usr/bin/env python
# -*- coding:utf-8 -*-

from models import User, Blog, Comment
from transwarp import db

db.create_engine(user='www-data', password='www-data', database='awesome')

u = User(name='test', email='test@example.com', password='1234567890', image='about:blank')

u.insert()

print 'New user id :', u.id

u1 = User.find_first('where email = ?', 'test@example.com')
print 'Find user\' name:', u1.name

u1.delete()

u2 = User.find_first('where email = ?', 'test@example.com')
print 'Find user:', u2