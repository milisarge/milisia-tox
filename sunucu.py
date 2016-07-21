#!/usr/bin/python3
# Copyright (c) 2016 mahmutov.
# License: GPL v2.

import asyncio
import logging
import os
import sys
import sys
import time
from callbacks import *
from bootstrap import node_generator
from settings import *

from aiohttp import web

global tox
tox = tox_factory(ProfileHelper.open_profile("profil.tox"))
sonek=str(tox.self_get_address())[0:2]


@asyncio.coroutine
def root(request):
    text = "milis-tox network"
    text+="\n"+str(tox.self_get_address())
    
    return web.Response(body=text.encode('utf-8'))

@asyncio.coroutine
def sendMessage(request):
	global tox
	result=""
	fno = request.match_info.get('arkadasno')
	text = "Mesaj gönderildi--> {}".format(fno)
	arkadasno="2"
	no=int(fno)
	if tox.friend_get_connection_status(no):
		result=tox.friend_send_message(no,0,"selam ben milis p2p servisiyim.")
	text+="-"+str(result)
	return web.Response(body=text.encode('utf-8'))


@asyncio.coroutine
def deleteFriend(request):
	global tox
	result=""
	fno = request.match_info.get('arkadasno')
	text = "Dugum silindi--> {}".format(fno)
	no=int(fno)
	result=tox.friend_delete(no)
	data = tox.get_savedata()
	ProfileHelper.save_profile(data)
	text+="-"+str(result)
	return web.Response(body=text.encode('utf-8'))

@asyncio.coroutine
def flist(request):
	global tox
	text=""
	for num in tox.self_get_friend_list():
		text+=str(num)+"-"+tox.friend_get_name(tox.self_get_friend_list()[num])+"\n"
	return web.Response(body=text.encode('utf-8'))
 
@asyncio.coroutine
def toxloop():
	global tox
	global loop
	while 1==1:
		tox.iterate()
		time.sleep(tox.iteration_interval() / 1000.0)
		#print (tox.self_get_connection_status())
		yield from asyncio.sleep(0.05)
@asyncio.coroutine
def init(loop):
	app = web.Application(loop=loop)
	app.router.add_route('GET', '/', root)
	app.router.add_route('GET', '/sm/{arkadasno}', sendMessage)
	app.router.add_route('GET', '/df/{arkadasno}', deleteFriend)
	app.router.add_route('GET', '/flist', flist)
	srv = yield from loop.create_server(app.make_handler(),'127.0.0.1', 7001)
	print("Web sunucusu http://127.0.0.1:7001 başlatıldı.")
	init_callbacks(tox)
	# bootstrap
	print ("bootstrap dugumlerine baglanıyor...")
	for data in node_generator():
		tox.bootstrap(*data)
	settings = Settings()
	#profile = Bot(tox)
	tox.self_set_name("Toxfs_Agent-0.1"+sonek)
	tox.self_set_status_message("Tox File Sharing Agent")
	#asyncio.async(toxloop(), loop=loop)
	asyncio.Task(toxloop())
	#asyncio.async(toxloop(), loop=loop)
	return srv
    
loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()


