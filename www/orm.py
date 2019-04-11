#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio, logging

import aiomysql


# 日志
def log(sql, args=()):
    logging.info('SQL:%s' % sql)


# 创建线程池
# loop 循环对象
# kw 关键字参数 MySQL连接参数
async def create_pool(loop, **kw):
    logging.info('create database connection pool...')
    global __pool
    __pool = await aiomysql.create_pool(
        host=kw.get('host', 'localhost'),
        port=kw.get('port', 3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['db'],
        charset=kw.get('charset', 'utf8'),
        autocommit=kw.get('autocommit', True),
        maxsize=kw.get('maxsize', 10),
        minsize=kw.get('minsize', 1),
        loop=loop
    )


# 选择查询
async def select(sql, args, size=None):
    log(sql, args)
    global __pool
    async with __pool.acquire() as conn:
        # 作为一个字典类型结果返回游标
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(sql.replace('?', '%s'), args or ())
            if size:
                # 如果有获取数据库数据行数的参数 按照规定获取行数数量
                rs = await cur.fetchmany(size)
            else:
                # 没有规定获取的数量 就全部获取出来
                rs = await cur.fetchall()
        logging.info('rows returned:%s' % len(rs))
        return rs


# sql 执行方法
async def execute(sql, args, autocommit=True):
    log(sql)
    async with __pool.acquire() as conn:
        if not autocommit:
        # 如果autocommit 为False 不自动提交开启协程
        await conn.begin()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(sql.replace('?', '%s'), args)
            affected = cur.rowcount
        if not autocommit:
            await conn.commit()
    except BaseException as e:
        if not autocommit:
            await conn.rollback()
        raise
    return affected

def create_args_string(num):
    l = []
    for n in range(num):
        l.append('?')
    return ','.join(l)

class Field (object):
    def __init__(self,name,column_type,primary_key,default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)

# 映射varchar StringField
class StringField(Field):

    def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(100)'):
        super().__init__(name, ddl, primary_key, default)

# Metaclass 元类
class ModelMetaclass(type):
    def __new__ (cls,name,base,attrs):

        # 排除Model 类本身
        if name =='Model' :
            return type.__new__(cls,name,base,attrs)

        # 获取table名称
        tableName = attrs.get('__table__',None) or name 
        logging.info('found model: %s (table:%s)' % (name,tableName))
        mappings = dict()
        fields = []
        primaryKey = None
        for k,v in attrs.items():
            #判断 值是不是Field 类
            if isinstance(v,Field):
                logging.info('found mapping : %s ==> %s' % k)
                
        