#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'Hello Young'

import logging
from transwarp.web import get, view
from models import User, Blog, Comment

@view('test_users.html')
@get('/')
def test_users():
	u1 = User(name='tom', email='tom@example.com', password='123456')
	u1.insert()

	users = User.find_all()
	return dict(users=users)