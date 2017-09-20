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
import sequence_pattern_mining

def main (cmd_1):
	sub_path_list = sequence_pattern_mining.block_sequence_detect(cmd_1)
	
	#test 1
		#Test if all sequences can map mining object files.
	#sequence_pattern_mining.sequence_file_test (cmd_1)
	#test 2 
		#Test if any item can be insert into any sequence
	#sequence_pattern_mining.sub_path_insert_test()
	#test 3 
		#Test if any sequence have item conflict.
	#sequence_pattern_mining.sub_path_self_chaos_test()
	


cmd_1 = sys.argv[1]
if not os.path.isfile(cmd_1):
	print "no file"
main(cmd_1)
