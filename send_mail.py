#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#此脚本用于向特定用户发送邮件通知；
#by chao.dong   
#472298551@qq.com


import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import getopt
import os
import time

import logging
from email.mime.text import MIMEText
from email.utils import formataddr
import smtplib

import ConfigParser



#邮件中必有的邮件地址；
#----------------------------------------------------
chao_dong	=	'chao.dong@sunlight-tech.com'
basic = [ chao_dong ]


#TS组；
#----------------------------------------------------
li_kang		=	'kang.li@sunlight-tech.com'
you_hua		=	'frank.zhou@sunlight-tech.com'
ri_co		=	'rico.li@sunlight-tech.com'

ts	=	[ li_kang , you_hua , ri_co ]

#领导；
#----------------------------------------------------
william		=	'william.zeng@sunlight-tech.com'
gavin		=	'gavin.xie@sunlight-tech.com'

leader = [ william , gavin ] 

#开发；
#----------------------------------------------------
ye_tao		=	'yetao.zheng@sunlight-tech.com'
lin_tao		=	'tao.lin@sunlight-tech.com'
gao_ru		=	'ru.gao@sunlight-tech.com'
guang_hao	=	'guanghao.he@sunlight-tech.com'

dev	=	[ ye_tao , lin_tao , gao_ru , guang_hao ]
#运营组
#----------------------------------------------------
#河南-王刚；
wang_gang		=	'wanggang@sunlight-tech.com'
hn = [ wang_gang ] 


#陕西-王昭
wang_zhao		=	'zhao.wang@sunlight-tech.com'
sx = [ wang_zhao ]

#武汉-王锡磷
wang_xilin		=	'xilin.wang@sunlight-tech.com'
wh = [ wang_xilin ] 

#云南-徐达翔
xu_daxiang		=	'jack.xu@sunlight-tech.com'
#云南-李超杰
li_chaojie		=	'chaojie.li@sunlight-tech.com'
yn = [ xu_daxiang , li_chaojie ] 


#深圳-李大志
li_dazhi		=	'sam.li@sunlight-tech.com'
sz = [ li_dazhi ]

#海南-何元哲
he_yuanzhe		=	'yuanzhe.he@sunlight-tech.com'
#海南-陈忠超
chen_zhongchao	=	'zhongchao.chen@sunlight-tech.com'
hnan = [ he_yuanzhe , chen_zhongchao ]


#福建
#--

#广西
#--

#广东有线
#--

#t - title
#r - receivor
#f - from



config_file = '/usr/local/sunlight/conf/monitor.ini'
send_mail_log	=	"/var/log/sunlight/monitor/send_mail_history.log"
time_format_string = "%Y/%m/%d %H:%M:%S"

#smtp_default_config
send_title = '盛阳科技 - 运营商监控报警系统 - 通知消息'
send_from = ['盛阳监控管理员','SL-zabbix@sunlight-tech.com']
smtp_to  	= ["Chao",'chao.dong@sunlight-tech.com']
send_receivor = [ chao_dong ]
html_msg = ""


def send_error(msg):
	print "[ Error ] %s - %s -" % (get_timestamp() , msg)


def get_timestamp():
	return time.strftime(time_format_string , time.localtime())

def send_mail():
	log_dir = os.path.dirname(send_mail_log)
	if not os.path.isdir(log_dir):
		os.makedirs(log_dir)
	logging.basicConfig(filename=send_mail_log,level=logging.INFO)
	send_msg = MIMEText(str(html_msg),'html','utf-8')
	send_msg['From'] = formataddr(send_from)
	send_msg['To'] = formataddr(smtp_to)
	send_msg['Subject'] = send_title
	try:

		email_server = smtplib.SMTP(smtp_server,25)
		email_server.login(smtp_user,smtp_pass)
		email_server.sendmail(smtp_user,send_receivor,send_msg.as_string())
		email_server.quit()
		logging.info("[ success ] - %s - [ mail content ] - %s" %( get_timestamp() , str(html_msg)))
		
	except smtplib.SMTPException:
		logging.error("[ failed ] - %s - [ mail content ] - %s" %( get_timestamp() , str(html_msg)))


def get_config_data():
	if not os.path.isfile(config_file):
		print " [ Error ] %s The file %s not found." % (get_timestamp() , config_file )
		sys.exit(0)
	cfp	=	ConfigParser.ConfigParser()
	cfp.read(config_file)
	mail_server = cfp.get('smtp','smtp_server')	
	mail_user = cfp.get('smtp','smtp_user')	
	mail_pass = cfp.get('smtp','smtp_pass')	
	
	if mail_server is None or mail_user is None or mail_pass is None:
		send_error("SMTP configure is empty!")
		sys.exit(0)
	
	
	globals()['smtp_server'] 	= mail_server
	globals()['smtp_user'] 		= mail_user
	globals()['smtp_pass'] 		= mail_pass
	
def  parse_send_receivor(rdata):
		receivers = rdata.split('+')
		rs = [ chao_dong ]
		for r in receivers:
			if r == 'leader':
				rs.extend( leader )
			elif r == 'ts':
				rs.extend( ts )
			elif r == 'dev':
				rs.extend(dev)
			elif r == 'hn':
				rs.extend(hn)
			elif r == 'sz':
				rs.extend(sz)
			elif r == 'sx':
				rs.extend(sx)
			elif r == 'hnan':
				rs.extend(hnan)
			elif r == 'wh':
				rs.extend(wh)	
			elif r == 'yn':
				rs.extend(yn)
		globals()['send_receivor'] = rs

				
def main(all_argv):
	try :
		opts , args = getopt.getopt(all_argv , "ht:r:f:c:" , ["help" , "title=" , "receivor=" , "from=" , "content="])
	except getopt.GetoptError:
		send_error('parametors passed error.')
		sys.exit(2)
		
	for opt , arg in opts:
		if opt in ('-h' , '--help'):
			print '''
slt_send_mail.py  [options]
-t mail_title 
-r mail_receivor
-f mail_from
-c mail_content			
--title=mail_title string		
--receivor=mail_receivor  	
values like 'basic' 'leader' 'dev' 'hn' 'sx' 'wh' 'yn' 'sz' 'hnan' 'fj' 'gx' 'gdyx'
or 'basic+dev' 'baisc+hn+wh'			
--from=main_from  string
--content=mail_content  string
			'''
			sys.exit()
		elif opt in ("-t" , "--title"):
			globals()['send_title'] = arg
		elif opt in ("-r" , "--receivor"):
			parse_send_receivor(arg)
		elif opt in ("-f" , "--from"):
			globals()['send_from'] = arg
		elif opt in ("-c" , "--content"):
			globals()['html_msg'] = arg
	#parse smtp data;
	get_config_data()
	#send mail;
	send_mail()
	
if __name__ == '__main__':
	if len(sys.argv) < 2:
		send_error("parametor number error!")
		sys.exit()
	main(sys.argv[1:])