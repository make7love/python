#!/usr/bin/env python
#-*- coding:UTF-8 -*-

from multiprocessing import Process , Pool , Lock
import os
import time
import subprocess
import sys

sp_hostid_dict = {
	'gx' 		: 	200, 		#深圳广信
	'hn' 		: 	202,  		#河南联通
	'hb' 		: 	203,  		#湖北电信
#	'hnyx'		:	204,		#海南有线
	'yndx'		:	205,		#云南电信
	'fj' 		:	206,		#福建电信
	'sx' 		:	207,		#陕西电信 
#	'gdyx'		:	209,		#广东有线
#	'xs' 		:	210			#山西联通
#	'atlantis'	: 	2163		#亚特兰蒂斯单体酒店
}

sp_hostid_list = [ hostids for hostids in sp_hostid_dict.values()]
pool_length = len(sp_hostid_list)
pull_data_dir = "/data/spdata"
pull_mysql_log = "/var/log/sunlight/pull_mysql_data.log"
pull_weedfs_log = "/var/log/sunlight/pull_weedfs_data.log"
pull_target_ip = ""
date_tgz = time.strftime("%Y%m%d" , time.localtime())

def print_error(msg):
	now_time_stamp = time.strftime("%Y-%m-%d %H:%M:%S" , time.localtime())
	print "[ ERROR ] %s - %s -" % (now_time_stamp , msg)

def get_current_time():
	now_time_stamp = time.strftime("%Y-%m-%d %H:%M:%S" , time.localtime())
	return now_time_stamp

def execute_command(cmd_string):
	print "---------begin to execute: %s" % cmd_string
	exec_handler = subprocess.Popen(cmd_string , shell=True , stdout=subprocess.PIPE , stderr=subprocess.STDOUT)
	(cmd_output , cmd_err) = exec_handler.communicate()
	if cmd_err is None:
		return cmd_output
	return cmd_err
		
	
def pull_data_init():
	#check sp-hostid info;
	if sp_hostid_dict is None:
		print_error("运营商hostid元组未定义！")
		sys.exit(2)
		
	pull_mysql_data_log_dir = os.path.dirname(pull_mysql_log)
	if not os.path.isdir(pull_mysql_data_log_dir):
		os.makedirs(pull_mysql_data_log_dir)
		
	pull_weedfs_data_log_dir = os.path.dirname(pull_weedfs_log)
	if not os.path.isdir(pull_weedfs_data_log_dir):
		os.makedirs(pull_weedfs_data_log_dir)

def pull_mysql_data(htid , mysql_lock):
	pull_mysql_data_dir = "%s/%s/%s" % (pull_data_dir , htid , "mysql")
	if not os.path.isdir(pull_mysql_data_dir):
		os.makedirs( pull_mysql_data_dir , 0755 )
	#pull_command= "touch %s/%s_%s" % (pull_mysql_data_dir , htid , "mysql")
	pull_command = "scp -P%d -i /usr/local/sunlight/sshkeys/init.pk %s:/home/mysql/%s.tar.gz  %s" % ((htid+20000) ,pull_target_ip , date_tgz , pull_mysql_data_dir)
	ret = execute_command(pull_command)
	exec_result = "%s \r\n %s - %s - %s - \r\n %s \r\n- pull_mysql_data finished. \r\n" %  \
	("---------------------------------------" , get_current_time() ,htid , "mysql" , ret)
	#print exec_result
	with mysql_lock:
		with open(pull_mysql_log , "a") as sql_log:
			sql_log.write(exec_result)
	
	
def pull_weedfs_data(htid , weedfs_lock):
	pull_weedfs_data_dir = "%s/%s/%s" % (pull_data_dir , htid , "weedfs")
	if not os.path.isdir(pull_weedfs_data_dir):
		os.makedirs( pull_weedfs_data_dir , 0755 )
	pull_command = "scp -P%d -i /usr/local/sunlight/sshkeys/init.pk %s:/home/weedfs/%s.tar.gz  %s" % ((htid+20000) ,pull_target_ip , date_tgz , pull_weedfs_data_dir)
	ret = execute_command(pull_command)
	exec_result = "%s \r\n %s - %s - %s - \r\n %s \r\n- pull_weedfs_data finished.\r\n" % \
	("---------------------------------------" , get_current_time() ,htid , "weedfs" , ret)
	#print exec_result
	with weedfs_lock:
		with open(pull_weedfs_log,"a") as weedfs_log:
			weedfs_log.write(exec_result)
	
	
def main():
	pull_data_init()
	mysql_lock = Lock()
	weedfs_lock = Lock()
	
	pool_mysql = Pool(pool_length)
	pool_weedfs = Pool(pool_length)
	
	for i in range(pool_length):
		pool_mysql.apply_async(pull_mysql_data(sp_hostid_list[i] , mysql_lock))
		pool_weedfs.apply_async(pull_weedfs_data(sp_hostid_list[i] , weedfs_lock ))
	
	pool_mysql.close()
	pool_weedfs.close()
	
	pool_mysql.join()
	pool_weedfs.join()
	print "command execute end..."
	
if __name__ == '__main__':
	reload(sys)
	sys.setdefaultencoding('utf-8')
	main()

