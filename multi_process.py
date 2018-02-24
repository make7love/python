#!/usr/bin/env python
#-*- coding:UTF-8 -*-

from multiprocessing import Process , Queue
from Queue import Empty as QueueEmpty
import subprocess
import os
import sys
import time
import re

reload(sys)
sys.setdefaultencoding('utf-8')


def sys_command(cmd):
	exec_cmd = subprocess.Popen(cmd , shell=True , stdout=subprocess.PIPE , stderr=subprocess.STDOUT)
	cmd_result , cmd_errno = exec_cmd.communicate()
	if cmd_errno is None:
		return 0, cmd_result
	else:
		return 1,cmd_errno	
	
def msg_write(q):
	produce_line = subprocess.Popen("/usr/local/dstat/dstat -tcdmnfs" , shell=True , stdout=subprocess.PIPE , stderr=subprocess.STDOUT)
	while True:
		line = produce_line.stdout.readline()
		line = re.sub(r"[\x1B]" , "" ,line)
		line = line.replace("[0;0m" , "")
		q.put(line,True,10)

			
def msg_read(q):
	while True:
		try:
			msg = q.get(True,10) #如不加任何参数，则无限期等待；
			with open("./getter_dstat_data", "a") as h:
				h.write(msg)
		except QueueEmpty:
			print "Queue is empty!"
			break
	sys.exit(1)

def main():
	test_dstat = "test -f /usr/local/dstat/dstat && echo OK"
	if len(str(sys_command(test_dstat)[1])) == 0:
		print "Error! dstat not found..."
		sys.exit(1)
	queue = Queue()
	pqueue = Queue()
	
	write_process = Process(target = msg_write , args=(queue,))
	read_process = Process(target = msg_read, args=(queue,))
	
	write_process.start()
	read_process.start()
	
	write_process.join()
	read_process.join()
	
main()