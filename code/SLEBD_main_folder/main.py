#!/usr/bin/python
#coding:utf-8
import sys
sys.path.append("../python_code_folder")
import os
import re 
import time 
import global_APIs
import multi_file_folder
import block_learning
import database_opt
import anomaly_detection
import report_APIs


def main (cmd_1):
	print "begin"

	global_APIs.global_folder_initializer(cmd_1)
	time_1 = time.time()
	#EBD learning
	#multi_file_folder.whole_daily_folder_block_learning(cmd_1)
	time_2 = time.time()
	#EB list extraction
	#multi_file_folder.whole_daily_folder_block_extract (cmd_1)
	time_3 = time.time()
	
	print "EB learning time"
	print time_2 - time_1
	print "EB list extraction time"
	print time_3 - time_2

	report_APIs.block_report_folder_total_event_analyze()

	print "finish"


cmd_1 = sys.argv[1]
if not os.path.isfile(cmd_1):
	print "no file"
main(cmd_1)
