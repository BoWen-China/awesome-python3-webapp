#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__autor__ = 'BoWen Chi'
# 日志
import logging; logging.basicConfig(level=logging.INFO)
# 异步 系统 JSON 时间模块
import asyncio,os,json,time

from datetime import datetime
from aiohttp import web

# index 访问返回的内容
def index(request):
	resp = web.Response(body=b'<h1>Awesome</h1>')
	# 防止默写浏览器会出现下载现象 chrome
	resp.content_type = 'text/html;charset=utf-8'
	return resp

@asyncio.coroutine
def init(loop):
	app = web.Application(loop=loop)
	# 填加路由节点 
	# 访问方式为get 路径地址为/ 用index 方法响应
	app.router.add_route('GET','/',index)
	srv = yield from loop.create_server(app.make_handler(),'127.0.0.1',9000)
	logging.info('server started at http://127.0.0.1:9000...')
	return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
