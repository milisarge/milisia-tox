#!/usr/bin/python3
# Copyright (c) 2016 mahmutov.
# License: GPL v2.

import asyncio
import jinja2
import aiohttp_jinja2
import logging
import os
import sys
import sys
import time
from callbacks import *
from bootstrap import node_generator
from settings import *
import subprocess
from aiohttp import web
#from http.server import BaseHTTPRequestHandler,HTTPServer
import random

kodsayfasi="iso-8859_9"
lokalhost="http://127.0.0.1"
global tox

if os.path.isfile("profil.tox"): 
    print ("mevcut profil açılıyor.")
    tox = tox_factory(ProfileHelper.open_profile("profil.tox"))
else:
    print ("yeni profil açılıyor.")
    tox = tox_factory(None,None)
    data = tox.get_savedata()
    ProfileHelper.save_profile(data)
sonek=str(tox.self_get_address())[0:4]

global tuntox
tuntox=None
if os.path.isfile("ozel/tox_save"): 
    print ("tuntox profili açılıyor.")
    tuntox = tox_factory(ProfileHelper.open_profile("ozel/tox_save"))
else:
    print ("tuntox sunucu'da sorun var.")

@asyncio.coroutine
def paysun():
    port=33999
    komut="cd paylasim && python3 -m http.server "+str(port)+" 2>&1|tee ../paysun.log"

    durum=yield from komutar(komut)
    if durum:
       komut="./tuntox -C ozel/ 2>&1|tee tuntox.log"
       durumt=yield from komutar(komut)
    return
@asyncio.coroutine
def root(request):
    global tuntox
    context = {}
    text = "milisia-dugum adresi"
    text+="<br>"+str(tox.self_get_address())
    text+="<br>" +"milisia-tuntox adresi"
    if tuntox is None:
        tuntox = tox_factory(ProfileHelper.open_profile("ozel/tox_save"))
    text+="<br>"+str(tuntox.self_get_address())
    context = {'data': text}
    response = aiohttp_jinja2.render_template(
        "ana.html", request, context)
    response.headers['Content-Language'] = 'tr'
    return response

@asyncio.coroutine
def sendMessage(request):
	global tox
	result=""
	fno = request.match_info.get('arkadasno')
	text = "Mesaj gönderildi--> {}".format(fno)
	no=int(fno)
	if tox.friend_get_connection_status(no):
		result=tox.friend_send_message(no,0,"selam ben milis p2p servisiyim.")
	text+="-"+str(result)
	return web.Response(body=text.encode('utf-8'))


@asyncio.coroutine
def komutar(komut):
	subprocess.Popen(komut,stdout=subprocess.PIPE,shell=True)
	print (komut)
	return True

@asyncio.coroutine
def listFiles(request):
	global tox
	durum=""
	toxid = request.match_info.get('toxid')
	#port  = request.match_info.get('port')
	#lport = request.match_info.get('lport')
	port =33999 
	lport=random.randrange(38000,40000)
	komut="./tuntox -i "+str(toxid)+" -L "+str(lport)+":127.0.0.1:"+str(port)
	print ("dugumler arası tunel acılıyor.")
	#tunel id kaydetmek için-şu an iptal
	#open("yenidugum","w").write(toxid)
	durum=yield from komutar(komut)
	link=lokalhost+":"+str(lport)
	context = {'data': link}
	response = aiohttp_jinja2.render_template("pano.html", request, context)
	response.headers['Content-Language'] = 'tr'
	return response

#dosya paylasim modulu
@asyncio.coroutine
def dps(request):
	global tox
	data=""
	if request.method =="POST":
		print("---",request["kdugum"])
	
	context = {'data': data}
	response = aiohttp_jinja2.render_template("dps.html", request, context)
	response.headers['Content-Language'] = 'tr'
	return response

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
def wshandler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.tp == web.MsgType.text:
            ws.send_str("merhaba, {}".format(msg.data))
        elif msg.tp == web.MsgType.binary:
            ws.send_bytes(msg.data)
        elif msg.tp == web.MsgType.close:
            break

    return ws

@asyncio.coroutine
def guncelle(request):
	komut="git pull > guncelleme.log"
	durum=yield from komutar(komut)
	log=open("guncelleme.log","r").read()
	loghtml="<html>güncellendi:<p>"+log+"<p><a href='/'>ana sayfa</a> </html>"
	return web.Response(body=loghtml.encode(kodsayfasi))

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
	while 1==1:
		tox.iterate()
		time.sleep(tox.iteration_interval() / 1000.0)
		
		if(os.path.isfile("yenidugum")):
			tox.friend_add_norequest(open("yenidugum","r").read())
			data = tox.get_savedata()
			ProfileHelper.save_profile(data)
			os.system("rm yenidugum") 
		
		#print (tox.self_get_connection_status())
		yield from asyncio.sleep(0.05)
@asyncio.coroutine
def init(loop):
	app = web.Application(loop=loop)
	app.router.add_route('GET', '/', root)
	app.router.add_route('GET', '/sm/{arkadasno}', sendMessage)
	app.router.add_route('GET', '/df/{arkadasno}', deleteFriend)
	app.router.add_route('GET', '/lf/{toxid}', listFiles)
	app.router.add_route('GET', '/flist', flist)
	app.router.add_route('GET', '/guncelle', guncelle)
	app.router.add_route('GET', '/dps', dps)
	app.router.add_static("/static",'./static')
	aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('./templates'))
	srv = yield from loop.create_server(app.make_handler(),'127.0.0.1', 7001)
	print("Web sunucusu http://127.0.0.1:7001 başlatıldı.")
	init_callbacks(tox)
	# bootstrap
	print ("bootstrap dugumlerine baglanıyor...")
	for data in node_generator():
		tox.bootstrap(*data)
	settings = Settings()
	#profile = Bot(tox)
	tox.self_set_name("milis-toxia-"+sonek)
	tox.self_set_status_message("Milis Toxia")
	#asyncio.async(toxloop(), loop=loop)
	asyncio.Task(toxloop())
	asyncio.Task(paysun())
	#asyncio.async(toxloop(), loop=loop)
	return srv
    
loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()


