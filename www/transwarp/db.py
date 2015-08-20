#!usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'Hello Young'

'''
Database operation module
'''

import time, uuid, functools, threading, logging
#Dict object:
class Dict(dict):
	'''
	Simple dict but support as x.y style

	>>> d1 = Dict()
	>>> d1['x'] = 100
	>>> d1.x
		100
	>>> d1['y'] = 200
	>>> d1.y
	200
	>>> d2 = Dict(a=1, b=2, c='3')
	>>> d2.c
	'3'
	>>> d2['empty']
	Traceback (most recent call last):
	 	...
	KeyError: 'empty'
	>>> d2.empty
	Traceback (most recent call last):
		...
	AttributeError: 'Dict' object has no attribute 'empty'
	>>> d3 = Dict(('a', 'b', 'c'),(1, 2, 3))
	>>> d3.a
	1
	>>> d3.b
	2
	>>> d3.c
	3
	'''
	def __init__(self, names=(), values=(), **kw):
		super(Dict, self).__init__(**kw)
		for k, v in zip(names, values):
			self[k] = v

	def __getattr__(self, key):
		try:
			return self[key]
		except KeyError:
			raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

	def __setattr__(self, key , value):
		self[key] = value
		
#返回下一个id
def next_id(t = None):
	'''
	Return next id as 50 char string

	Args:
		t: unix timestamp , default to None and using time.time()

	'''
	if t is None:
		t = time.time()
	return '%015d%s000' %(int(t*1000), uuid.uuid4.hex)

#??
def _profiling(start, sql=''):
	t = time.time() - start
	if t > 0.1:
		logging.warning('[Prolfiling] [DB] %s: %s' % (t, sql))
	else:
		logging.info('[Prolfiling] [DB] %s: %s' % (t, sql))
#
class DBError(Exception):
	pass

#
class MultiColumnsError(DBError):
	pass

#数据库引擎对象
class _Engine(object):
	def __init__(self, connect):
		self._connect = connect
	def connect(self):
		return self._connect

#global engine Object
engin = None

#持有数据库链接的上下文对象
class _DbCtx(threading.local):

	'''
	Thread local object that holds connection info
	'''
	def __init__(self):
		self.connection = None
		self.transactions = 0

	def is_init(self):
		return not self.connection is None

	def init(self):
		self.connection = _LasyConnection()
		self.connection = 0

	def cleanup(self):
		self.connection.cleanup()
		self.connection = None

	def  cursor(self):
		return self.connection.cursor()

# thread-local  db context
_db_ctx = _DbCtx()

#
def create_engine(user, password, database, host='127.0.0.1', port=3306, **kw):
	import mysql.connector
	global engine
	if engine is not None:
		raise DBError('Engine is already initialized.')
	params = dict(user=user, password=password, host=host, port=port)
	defaults = dict(use_unicode=True, charset='utf-8', collation='utf8_general_ci', autocommit=False)
	for k, v in defaults.iteritems():
		params[k] = kw.pop(k, v)
	params.update(kw)
	params['buffered'] = True
	egnine = _Engine(lambda: mysql.connector.connect(**params))
	#test connection
	logging.info('Init mysql engine <%s> ok.' % hex(id(engine)))

#
class _LasyConnection(object):
	"""docstring for _LasyConnection"""
	def __init__(self):
		self.connection = None

	def cursor(self):
		if self.connection is None:
			connection = egnine.connect()
			logging.info('open connection <%s>' % hex(id(connection)))
			self.connection = connection
		return self.connection.cursor()

	def commit(self):
		self.connection.commit()

	def rollback(self):
		self.connection.rollback()

	def cleanup(self):
		if self.connection:
			connection = self.connection
			self.connection = None
			logging.info('close connection <%s>' % hex(id(connection)))
			connection.close()


#数据库链接的上下文
#定义了__enter__()和__exit__()的对象可以用于with语句，确保任何情况下__exit__()方法可以被调用。
class _ConnectionCtx(object):
	def __enter__(self):
		global _db_ctx
		self.should_cleanup = False
		if not _db_ctx.is_init():
			_db_ctx.init()
			self.should_cleanup = True
		return self

	def __exit__(self):
		global _db_ctx
		if self.should_cleanup:
			_db_ctx.cleanup

def connection():
	return _ConnectionCtx()