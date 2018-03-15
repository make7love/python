#!/usr/bin/env python
#-*- coding:UTF-8 -*-

from fabric.api import env, run, execute, local, cd, roles
import os
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

spconf="/usr/local/sunlight/conf/spinfo.ini"


def get_time():
	return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())

def send_error(msg):
	print "[ Error ] %s - %s" % (get_time() , msg)
	
	
spdict={};
if os.path.isfile(spconf):
	with open(spconf, "r") as conf:
		for line in conf:
			if len(line.strip()) and '=' in line:
				(k , v)=line.strip().split('=')
				spdict[k]=v
else:
	send_error("%s not found..." % (spconf))
	sys.exit(1)
	
if spdict.has_key('appnodes'):
	env.hosts=spdict['appnodes'].split(",")
else:
	send_error("key : appnodes not found in spdictt")
	sys.exit(1)
	
if not env.hosts:
	send_error("env.hosts is empty!");
	sys.exit(1)


if not os.path.isfile(spdict['ssh_key']):
	send_error("ssh_key file not found.")
	sys.exit(1)
	
env.key_filename=spdict['ssh_key']

env.user=spdict['ssh_user']
env.port=spdict['ssh_port']


def epg_init():
	if not spdict['epg_test_dir']:
		send_error('epg_test_dir is empty!')
		sys.exit(1)
	
	if not os.path.isdir(spdict['epg_test_dir']):
		send_error('epg_test_dir not exist...')
		sys.exit(1)
		
	run('epg_init')
		

def epg_push():
	run('epg_push')


def epg_pull():
	run('epg_pull')
	