#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio,logging

import aiomysql

# 日志
def log(sql,args=()):
	logging.info('SQL:%s' % sql)

# 创建线程池
# loop 循环对象
# kw 关键字参数 MySQL连接参数
async def create_pool(loop,**kw):
	logging.info('create database connection pool...')
	global __pool
	__pool = await aiomysql.create_pool(
		host = kw.get('host','localhost'),
		port = kw.get('port',3306),
		user = kw['user'],
		password = kw['password'],
		db =kw['db'],
		charset = kw.get('charset','utf8'),
		autocommit = kw.get('autocommit',True),
		maxsize = kw.get('maxsize',10),
		minsize = kw.get('minsize',1),
		loop = loop
	)

#选择查询
async def select(sql,args,size=None):
	log(sql,args)
	global __pool
	async with __pool.acquire() as conn :
		# 作为一个字典类型结果返回游标
		async with conn.cursor(aiomysql.DictCursor) as cur :
			await cur.execute(sql.replace('?','%s'),args or ()) 
			if size :
				# 如果有获取数据库数据行数的参数 按照规定获取行数数量
				rs = await cur.fetchmany(size)
			else :
				# 没有规定获取的数量 就全部获取出来
				rs = await cur.fetchall()
		logging.info('rows returned:%s' % len(rs))
		return rs;
