#!/usr/bin/python
#coding:utf-8
import os
import sys
import re 
import shutil
import global_APIs
import block_learning
import database_opt
import time
import anomaly_detection
folder_control_lower_band = 0 
folder_control_upper_band = 150 

#folder file preprocessor:
	#whole_dataset_folder_gen_daily_node_log_file
	#whole_dataset_folder_gen_single_node_log_file
	#sub_path_list_detector
	#find_sub_path_console_log

def whole_dataset_folder_gen_daily_node_log_file(folder_name):
#{{{
	sub_path_list = sub_path_list_detector(folder_name)
	total_wanted_file_num = 600 
	file_step = 5
	folder_count = 0
	path = "console_log_single_node_file"
	if os.path.isdir(path):
		shutil.rmtree (path)
	os.mkdir(path)	
	while folder_count < total_wanted_file_num/file_step :
		ignore_file_num = file_step * folder_count
		wanted_file_num = file_step * (folder_count + 1) 
		log_list = find_sub_path_console_log (sub_path_list, wanted_file_num, ignore_file_num)
		if log_list == []:
			break
		tmp_path = path
		tmp_path += "/"
		tmp_path += str(folder_count)
		if os.path.isdir(tmp_path):
			shutil.rmtree (tmp_path)
		os.mkdir(tmp_path)	
		whole_dataset_folder_gen_single_node_log_file(folder_name, wanted_file_num, ignore_file_num, tmp_path, str(folder_count))
		folder_count += 1
#}}}

def whole_dataset_folder_gen_single_node_log_file(folder_name, wanted_file_num = 600, ignore_file_num = 0, path = "console_log_single_node_file", file_prefix = ""):
#{{{
	sub_path_list = sub_path_list_detector(folder_name)
	log_list = find_sub_path_console_log (sub_path_list, wanted_file_num, ignore_file_num)

	if os.path.isdir(path):
		shutil.rmtree (path)
	os.mkdir(path)	
	
	node_list = {} 

	for file_name in log_list:
		fl = open (file_name, "r")
		while True:
			line = fl.readline()
			if not line:	
				break
			node_id = global_APIs.get_line_id (line)
			node_output_name = path 
			node_output_name += "/"
			if not file_prefix == "":
				node_output_name += file_prefix
				node_output_name += "_"
			
			node_output_name += node_id
			node_output_name += ".txt" 
			if not node_id in node_list:
				node_fl = open(node_output_name, "w")
				node_list[node_id] = node_fl	
			node_fl = node_list[node_id]
			node_fl.write(line)
		fl.close
	
	for node_id in node_list:
		node_fl = node_list[node_id]
		node_fl.close()
#}}}

def sub_path_list_detector (folder_name):
#{{{
	folder_list = [] 
	folder_list_1 = [] 
	
	pattern = r'p0-([0-9]+)t([0-9]+)$'		
	for filename in os.listdir (folder_name):
		#p0-20150218t105253

		matchobj = re.match (pattern, filename)
		if matchobj:
			folder_list.append (filename)		
	
	while not len (folder_list) == 0: 
		min_pos = 0
		min_date = 20209999
		min_time = 999999
		min_folder_name = ""
		for i in range (0, len(folder_list)):
			sub_folder_name = folder_list[i]
			matchobj = re.match (pattern, sub_folder_name)
			date = matchobj.group(1)
			time = matchobj.group(2)
			if int(date) < min_date:
				min_pos = i
				min_date = int(date)
				min_time = int(time)
				min_folder_name = sub_folder_name
			if int(date) == min_date and int(time) < min_time :
				min_pos = i
				min_time = int(time)
				min_folder_name = sub_folder_name
		tmp = folder_name
		tmp += "/"
		tmp += min_folder_name
		folder_list_1.append (tmp)
		del(folder_list[min_pos])	

	return folder_list_1
#}}}

def find_sub_path_console_log (sub_folder_list, max_file_count = 10, ignore_file_count = 0):
#{{{
	pattern = r'console-([0-9]+).cleansed$'
	file_count = 0
	total_needed_file_list = []	
	for sub_folder_name in sub_folder_list:
		#console-20150211.cleansed
		console_file_list = []	
		for filename in os.listdir (sub_folder_name):
			matchobj = re.match (pattern, filename)
			if matchobj:
				console_file_list.append (filename)
		while not len (console_file_list) == 0: 
			min_pos = 0
			min_date = 99999999
			min_console_name = ""
			for i in range (0, len(console_file_list)):
				console_file_name = console_file_list[i]
				matchobj = re.match (pattern, console_file_name)
				date = matchobj.group(1)
				if int(date) < min_date:
					min_pos = i
					min_date = int(date)
					min_console_name = console_file_name
			tmp = sub_folder_name
			tmp += "/"
			tmp += min_console_name
			if file_count >= ignore_file_count:
				total_needed_file_list.append (tmp)
			del(console_file_list[min_pos])
			file_count += 1 
			if file_count >= max_file_count:
				break	
				
		if file_count >= max_file_count:
			break	
	return total_needed_file_list
#}}}


#folder file block learning
def folder_happen_matrix_analyze (folder_name, happen_matrix, single_line_pattern_db, need_update_single_line_pattern_list, single_line_pattern_range_line_pattern_list, node_id_last_list , ignore_previous_file):
	file_list = global_APIs.get_folder_file_list (folder_name)
	file_count = 0
	for input_file in file_list:
		fl = open (input_file, "r")
		first_message = fl.readline()
		fl.close()	
		node_id = global_APIs.get_line_id(first_message)
		if node_id == "":
			#this is a empty file, do nothing
			continue

		file_count += 1
		if file_count % 20 == 0:
			print "generate matrix " + str(file_count)
		result = block_learning.generate_happen_matrix_from_message_list (input_file, happen_matrix, single_line_pattern_db, need_update_single_line_pattern_list, single_line_pattern_range_line_pattern_list, node_id_last_list, ignore_previous_file)
		happen_matrix = result[0]
		single_line_pattern_db = result[1]
		need_update_single_line_pattern_list = result[2]
		single_line_pattern_range_line_pattern_list = result[3]
		node_id_last_list = result[4]
	result = []
	result.append(happen_matrix)	
	result.append(single_line_pattern_db)	
	result.append(need_update_single_line_pattern_list)	
	result.append(single_line_pattern_range_line_pattern_list)
	result.append(node_id_last_list)
	return 	result	

def folder_block_learning (folder_name, happen_matrix, single_line_pattern_db, need_update_single_line_pattern_list, single_line_pattern_range_line_pattern_list, block_pattern_list, message_closest_message_list):
	need_merge_one_more_round = 1
	total_affected_message_list = []
	first_round_analyze = 1
	round_control_range = 2 
	round_num = 1
 
	not_in_need_update_list_left_message_list = []
	while need_merge_one_more_round == 1:
		print "ARES merge round " + str(round_num)
		need_merge_one_more_round = 0 

		result = block_learning.update_message_closest_list_for_update_message_list(
			need_update_single_line_pattern_list,
			single_line_pattern_range_line_pattern_list, 
			happen_matrix, 
			message_closest_message_list, 
			round_num, 
			not_in_need_update_list_left_message_list)
		affected_message_list = result[0]
		message_closest_message_list = result[1]
		single_line_pattern_range_line_pattern_list = result[2]
		for affected_message in affected_message_list:
			if not affected_message in total_affected_message_list:
				total_affected_message_list.append(affected_message)

		result = block_learning.block_merge_from_message_closest_message_list(block_pattern_list, affected_message_list, message_closest_message_list, single_line_pattern_db)
		block_pattern_list = result[0]
		single_line_pattern_db = result[1]
		left_message_list = result[2]


		if not left_message_list == []:
			print "left_message_list" + str(left_message_list)
			not_in_need_update_list_left_message_list = []
			for left_message in left_message_list:
				if not left_message in need_update_single_line_pattern_list:
					not_in_need_update_list_left_message_list.append(left_message)
			need_update_single_line_pattern_list = []
			need_update_single_line_pattern_list = left_message_list
			need_merge_one_more_round = 1

 
		round_num += 1
		if round_num >= round_control_range:
			tmp = "analyzed " + str(round_num) +" rounds, reach control num. stop!"
			break
	tmp = []
	tmp.append(happen_matrix)
	tmp.append(single_line_pattern_range_line_pattern_list)
	tmp.append(message_closest_message_list)
	tmp.append(block_pattern_list)
	tmp.append(single_line_pattern_db)
	tmp.append(total_affected_message_list)
	return tmp

def whole_daily_folder_block_learning (folder_name):
	sub_folder_list = global_APIs.get_folder_file_list (folder_name)
	done_sub_folder_list = []
	folder_num = -1 
	report_fl = open("total_progress.txt", "w")
	last_prefix = -1
	#this last prefix is the last successed folder number
	for sub_folder in sub_folder_list:
		report_tmp = ""
		report_tmp += "block learning " + sub_folder + "\n"
		print "block learning " + sub_folder + "\n"
		folder_num += 1
		file_mode = global_APIs.get_file_mode(sub_folder)
		if file_mode == "":
			print "Can't detect file mode from folder " + sub_folder
			continue
		if folder_num < folder_control_lower_band:
			last_prefix = folder_num
			continue
		if folder_num >= folder_control_upper_band:
			break
		#done_sub_folder		
		done_sub_folder_list = database_opt.read_done_sub_folder_list(sub_folder)
		
		if sub_folder in done_sub_folder_list:
			last_prefix = folder_num
			continue
		prefix_path = str(folder_num)
		global_APIs.sql_prefix_folder_initializer(sub_folder, prefix_path)
		#previous result read from database
		#{{{
		previous_happen_matrix = database_opt.read_happen_matrix(sub_folder, last_prefix, "total")
		new_found_single_line_pattern = []
		single_line_pattern_db = database_opt.read_single_line_pattern_db(sub_folder, last_prefix)
		single_line_pattern_range_line_pattern_list = database_opt.read_single_line_pattern_range_list(sub_folder, last_prefix) 
		message_closest_message_list = database_opt.read_message_closest_message_list(sub_folder, last_prefix) 
		block_pattern_list =  database_opt.read_block_pattern_list(sub_folder, last_prefix)
		previous_node_id_last_list = database_opt.read_node_id_last_list_file(sub_folder, last_prefix)
		#}}}

		#generate this matrix
		#{{{
		ignore_previous_file = 0
		this_happen_matrix = {}
		result = folder_happen_matrix_analyze (
			sub_folder, 
			this_happen_matrix, 
			single_line_pattern_db, 
			new_found_single_line_pattern, 
			single_line_pattern_range_line_pattern_list, 
			previous_node_id_last_list, 
			ignore_previous_file)
		this_happen_matrix = result[0]
		single_line_pattern_db = result[1]
		new_found_single_line_pattern = result[2]
		single_line_pattern_range_line_pattern_list = result[3]
		node_id_last_list = result[4]
		previous_node_id_last_list = database_opt.read_node_id_last_list_file(sub_folder, last_prefix)
		
		total_happen_matrix = happen_matrix_merge(this_happen_matrix, previous_happen_matrix, previous_node_id_last_list, sub_folder)
	
		if global_APIs.invalid_message == 'invalid_message':	
			global_APIs.single_line_db_invalid_message_assign(single_line_pattern_db)
		global_APIs.generate_single_pattern_dynamic_similarity_threshold(total_happen_matrix)

		#store recent record	
		database_opt.output_happen_matrix(total_happen_matrix, sub_folder, folder_num, "total")
		database_opt.output_happen_matrix(this_happen_matrix, sub_folder, folder_num, "this")
		database_opt.output_single_line_pattern_range_list (single_line_pattern_range_line_pattern_list, sub_folder, folder_num)
		database_opt.output_node_id_last_list_file(node_id_last_list, sub_folder,folder_num )
		#}}}

		#new_found_single_line_pattern
		#{{{
		report_tmp += "	new found single line " + str (len(new_found_single_line_pattern)) + "\n"
		print "	new found single line " + str (len(new_found_single_line_pattern))
		orig_new_found_single_line_pattern_list = []
		for message in new_found_single_line_pattern:
			orig_new_found_single_line_pattern_list.append(message)
		previous_happen_matrix = database_opt.read_happen_matrix(sub_folder, last_prefix, "total")
		need_update_single_line_pattern_list = anomaly_detection.this_happen_matrix_anomaly_detection(
			previous_happen_matrix, 
			total_happen_matrix, 
			new_found_single_line_pattern, 
			single_line_pattern_db, 
			message_closest_message_list)	

		new_found_single_line_num = 0
		left_new_found_single_line_pattern_list = []
		for message in 	orig_new_found_single_line_pattern_list:
			if message in need_update_single_line_pattern_list:
				new_found_single_line_num += 1
			else:
				left_new_found_single_line_pattern_list.append(message)
		update_length = len(need_update_single_line_pattern_list)

		report_tmp += "	new_found_single_line " + str(new_found_single_line_num) + "\n"
		print "	new_found_single_line " + str(new_found_single_line_num)
		report_tmp += "	need update previous single line " + str(update_length - new_found_single_line_num) + "\n"
		print "	need update previous single line " + str(update_length - new_found_single_line_num)
		#}}}

		if len(need_update_single_line_pattern_list) > 0:
			result = folder_block_learning (
					sub_folder, 
					total_happen_matrix, 
					single_line_pattern_db, 
					need_update_single_line_pattern_list, 
					single_line_pattern_range_line_pattern_list, 
					block_pattern_list, 
					message_closest_message_list)

			total_happen_matrix = result[0]
			single_line_pattern_range_line_pattern_list = result[1]
			message_closest_message_list = result[2]
			block_pattern_list = result[3]
			single_line_pattern_db = result[4]
			affected_message_list = result[5]
			
			report_tmp += "	affected_message_list_length: " + str(len(affected_message_list)) + "\n"
			print "	affected_message_list_length: " + str(len(affected_message_list))
			if len(affected_message_list) == str(new_found_single_line_num):
				report_tmp += "	previous block list have no change" + "\n"

		database_opt.output_message_closest_message_list(message_closest_message_list, sub_folder, folder_num)
		database_opt.output_block_pattern_list(block_pattern_list, sub_folder, folder_num)
		database_opt.output_single_line_pattern_db(single_line_pattern_db, sub_folder, folder_num)
		
		done_sub_folder_list.append(sub_folder)
		#ARES
		#database_opt.output_done_sub_folder_list(done_sub_folder_list, sub_folder )

		database_opt.output_this_round_affect_message_list(
			sub_folder,
			orig_new_found_single_line_pattern_list,
			need_update_single_line_pattern_list,
			left_new_found_single_line_pattern_list,
			affected_message_list,
			folder_num)

		last_prefix = folder_num
		
		block_merge_error_list = database_opt.block_pattern_list_summary(sub_folder)
		if not len(block_merge_error_list) == 0:
			report_tmp += 	str(block_merge_error_list)

		#print report_tmp
		report_fl.write(report_tmp)

	report_fl.close()
	return folder_num

def happen_matrix_merge(this_happen_matrix, previous_happen_matrix, previous_node_id_last_list, sub_folder):
	merged_matrix =  previous_happen_matrix
	
	file_list = global_APIs.get_folder_file_list (sub_folder)
	for input_file in file_list:
		fl = open (input_file, "r")
		first_message = fl.readline()
		fl.close()	
		node_id = global_APIs.get_line_id(first_message)
		if node_id == "" or not node_id in previous_node_id_last_list:
		#this is same as generate happen matrix
		#if can't detect node id, it will not generate matrix
		#if this node not generated matrix, its last line info will not update
			continue
		message_name = previous_node_id_last_list[node_id]
		merged_matrix[message_name]["last"] -= 1
		merged_matrix[message_name]["happen_time"] -= 1

		#should explain
		#last node's last line happen time and its next message info have been counted in this matrix
		#however last matrix still have its one time of happen time and the info that next line is last
		#we need to erase its one time of happen time and one time of last 


	for message in 	this_happen_matrix:
		this_list = this_happen_matrix[message]
		merged_list = {}
		if message in merged_matrix:
			merged_list = merged_matrix[message]
		for this_message in this_list:
			if this_message in merged_list:
				merged_list[this_message] += this_list[this_message]
			else:
				merged_list[this_message] = this_list[this_message]
		
		merged_matrix[message] = merged_list

	return  merged_matrix

def whole_daily_folder_block_extract (folder_name):
	total_error_report = "extract_error_report.txt"
	error_report_fl = open(total_error_report, "w")	
	sub_folder_list = global_APIs.get_folder_file_list (folder_name)
	done_example_list = []
	done_example_report_fl = open("example_report.txt", "w")
	folder_num = -1 
	for sub_folder in sub_folder_list:
		folder_num += 1
		if folder_num < folder_control_lower_band:
			continue
		if folder_num >= folder_control_upper_band:
			break
		print "block extract " + sub_folder
		file_mode = global_APIs.get_file_mode(sub_folder)
		if file_mode == "":
			print "can't detect mode " + sub_folder
			continue
		folder_block_extract(sub_folder, error_report_fl, done_example_list, done_example_report_fl)
	error_report_fl.close()
	done_example_report_fl.close()

def folder_block_extract (folder_name, error_report_fl, done_example_list, done_example_report_fl):
	last_sub_folder = global_APIs.get_latest_sql_db_path(folder_name)
	file_list = global_APIs.get_folder_file_list (folder_name)
	block_pattern_list = database_opt.read_block_pattern_list(folder_name, last_sub_folder)
	single_line_pattern_db = database_opt.read_single_line_pattern_db(folder_name, last_sub_folder)
	#we don't need to load closest message list
	file_list_error = {}
	file_count = 0
	for input_file in file_list:
		file_count += 1
		#if file_count % 5 == 0:
		#	print "file extract " + str(file_count)

		result = input_file_block_report_extraction(input_file, block_pattern_list, single_line_pattern_db)
		if result == []:
			continue
		block_list = result[0]
		file_single_line_report = result[1]
		summary = result[2]
		file_failed_list = result[3]
	
		database_opt.output_file_block_report_list(block_list, input_file)
		database_opt.output_file_single_line_list(file_single_line_report, input_file)

		if not file_failed_list == []:
			file_list_error[input_file] = file_failed_list
			error_report_fl.write(input_file)
			error_report_fl.write("\n")
			
			for file_record in file_failed_list:
				error_report_fl.write(str(file_record))
				error_report_fl.write("\n")
		#dump exmaple
		for block in block_list:
			block_name = block[0]
			if not block_name in block_pattern_list:
				continue
				#this is not a block
			if block_name in done_example_list:
				continue
			done_example_list.append(block_name)
			done_example_report_fl.write(block_name)
			done_example_report_fl.write("\n")

			block_start_line = block[1]
			block_finish_line = block[2]
			fl = open(input_file, "r")
			fl_line = fl.readlines()
			for i in range (block_start_line, block_finish_line + 1):
				done_example_report_fl.write(fl_line[i-1])
			done_example_report_fl.write("\n")
				
	
	database_opt.output_extract_error_list(file_list_error, input_file)

def single_line_report_succeed_block_list_analyze(input_file, file_single_line_report, block_pattern_list, single_line_pattern_db, care_last_node_file = 1):
#{{{
	match_last_node_block_list_start = []
	succeed_block_list = []
	stack = []

	if care_last_node_file == 1:	
		node_id = global_APIs.get_file_node_name(input_file)
		node_stack_last_block_list = database_opt.read_node_stack_last_block_list(input_file)
		if node_id in node_stack_last_block_list:
			last_same_node_last_stack = node_stack_last_block_list[node_id]["stack"]
		else:
			last_same_node_last_stack = []
		
		for last_stack_block in last_same_node_last_stack:
			tmp = []
			last_stack_block_name = last_stack_block[0]
			tmp.append(last_stack_block_name + "_lower_half")
			tmp.append(last_stack_block[1])
			stack.append(tmp)


	single_line_list_num = 0
	last_block_name = ""
	while single_line_list_num < len(file_single_line_report):
#{{{
		this_message = file_single_line_report[single_line_list_num]
		this_message_pattern_name = this_message[0]
		message_belong_block_name = single_line_pattern_db[this_message_pattern_name]["belong_block"]
		#judge if this message belong to a block is top priority. this will save resource
		if message_belong_block_name == "":
			single_line_list_num += 1
			continue
		
		next_message_pattern_name = ""
		if not single_line_list_num == len(file_single_line_report) - 1:
			#eliminate repeating messages
			next_message = file_single_line_report[single_line_list_num + 1]
			next_message_pattern_name = next_message[0]

		message_line_num = int(this_message[1])
		if is_block_start_line (this_message_pattern_name ,message_belong_block_name, block_pattern_list):
			#this is one block's start line
			#if this message is a start line, but we already have this message in stack, we should ignore it.
			#I have reason to ignore this start line if this block already in stack.
			#one block can not nest in a same block
			#only when finish line and start line can match, then generate a block record
			exist = 0
			for block_record in stack:
				if block_record[0] == message_belong_block_name:
					single_line_list_num += 1
					exist = 1
					break
			if exist == 1:
				continue
			tmp = []
			tmp.append(message_belong_block_name)
			tmp.append(message_line_num)
			stack.append(tmp)
		elif is_block_finish_line (this_message_pattern_name ,message_belong_block_name, block_pattern_list):
			#this is one block's finish line
			#if this message is a finish line, and its next message is same as it, we should ignore this message.
			if next_message_pattern_name == this_message_pattern_name:
				single_line_list_num += 1
				continue
			if not stack == []:	
				block_stack_tmp = stack.pop()
				stack_block_name = block_stack_tmp[0]
				block_start_line_num = block_stack_tmp[1]
			else:
				block_stack_tmp = []
				stack_block_name = ""

			if message_belong_block_name == stack_block_name:
				#match
				tmp = []
				tmp.append(message_belong_block_name)
				tmp.append(block_start_line_num)
				tmp.append(message_line_num)
				succeed_block_list.append(tmp)
				last_block_name = message_belong_block_name
			elif message_belong_block_name + "_lower_half" == stack_block_name:
				#match
				tmp = []
				tmp.append(message_belong_block_name + "_lower_half")
				tmp.append(1)
				tmp.append(message_line_num)
				succeed_block_list.append(tmp)
				last_block_name = message_belong_block_name + "_lower_half"
				block_stack_tmp[0] = block_stack_tmp[0].replace("_lower_half", "")
				match_last_node_block_list_start = block_stack_tmp
			else:
				#mismatch
				#should judge if this line is last block's last line.
				#could have this situation:
				#M_1, M_2, M_3, M_4, M_3
				#M_1 and M_3 are block's start and finish
				#however last block record will not include the second M_3
				if message_belong_block_name == last_block_name:
					#this is last block's finish line.
					#extend the last block
					#do not need to reassign last block name
					succeed_block_list[len(succeed_block_list) - 1][2] = message_line_num
					#push stack record back to avoid nesting block
					if not block_stack_tmp == []:
						stack.append(block_stack_tmp)


		single_line_list_num += 1

	succeed_block_list = block_nest_eliminate(succeed_block_list)
#}}}
	if care_last_node_file == 1 and not match_last_node_block_list_start == []:
		#this means have last node last half block, don't need to judge if there is this noid in the last stack
		last_node_file = node_stack_last_block_list[node_id]["last_file_path"]
		print "ARES update last node" + str(match_last_node_block_list_start)
		database_opt.update_last_node_file_block_list(last_node_file, match_last_node_block_list_start)

	
	if care_last_node_file == 1:
		remain_stack_list = []
		i = 0
		while i < len(stack):
			block_record = stack[i]
			block_name = block_record[0]
			if not re.match(r'block\_([0-9]+)\_lower\_half$', block_name):
				remain_stack_list.append(block_record)
			i += 1
		if node_id in node_stack_last_block_list:
			node_stack_last_block_list[node_id]["stack"] = remain_stack_list
			node_stack_last_block_list[node_id]["last_file_path"] = input_file
		else:
			node_stack_last_block_list[node_id] = {}
			node_stack_last_block_list[node_id]["stack"] = remain_stack_list
			node_stack_last_block_list[node_id]["last_file_path"] = input_file
		database_opt.output_node_stack_last_block_list(input_file, node_stack_last_block_list)


	return succeed_block_list
#}}}

def single_line_report_convert_into_block_list (succeed_block_list, file_single_line_report, block_pattern_list, single_line_pattern_db):
#{{{
	block_list = []
	extraction_summary = {}
	file_failed_list = []
	succeed_block_list_num = 0
	succeed_block_list_length = len(succeed_block_list)
	single_line_list_num = 0
	inside_block_switch = 0
	repeat_single_line_info = []
	while single_line_list_num < len(file_single_line_report):
		if succeed_block_list_length == 0:
			current_block = [] 
			current_block_name = ""
			current_block_start_line = -1
			current_block_finish_line = -1
		
		else:
			current_block = succeed_block_list[succeed_block_list_num]
			current_block_name = current_block[0]
			current_block_start_line = current_block[1]
			current_block_finish_line = current_block[2]

		single_line_message = file_single_line_report[single_line_list_num]
		message_pattern_name = single_line_message[0]
		message_belong_block_name = single_line_pattern_db[message_pattern_name]["belong_block"]
		message_line_num = int(single_line_message[1])
		if single_line_list_num < len(file_single_line_report) - 1:
			next_single_line_message = file_single_line_report[single_line_list_num + 1]
		else:
			next_single_line_message = single_line_message
		next_message_pattern_name = next_single_line_message[0]
		next_message_line_num = int(next_single_line_message[1])

		if repeat_single_line_info == []:
			repeat_single_line_info.append(message_pattern_name)
			repeat_single_line_info.append(message_line_num)
			repeat_single_line_info.append(message_line_num)


		#in fact, message_line_num is single_line_list_num + 1
		
		if message_line_num == current_block_start_line:
			block_list.append(current_block)
			single_line_list_num = current_block_finish_line 
			#this is very important!
			#current_block_finish_line is real line number in file, but single_line_list_num is a list sub-index in list
			#however single_line_list_num is current_block_finish_line, means the next line of the current block
			current_block_name = current_block_name.replace ("_lower_half", "")
			if current_block_name in extraction_summary:
				tmp = extraction_summary[current_block_name]
				tmp ["correct"] += 1
			else:
				tmp = {}
				tmp ["correct"] = 1
				tmp ["incorrect"] = 0 
			extraction_summary[current_block_name] = tmp
			if succeed_block_list_num < succeed_block_list_length - 1:
				succeed_block_list_num += 1
			repeat_single_line_info = []
		else:
			if not message_pattern_name == next_message_pattern_name:
				block_list.append(repeat_single_line_info)
				repeat_single_line_info = []
			else:
				repeat_single_line_info[2] =  next_message_line_num
			single_line_list_num += 1
			if not message_belong_block_name == "":
				#acturally it belongs to a block
				if message_belong_block_name in extraction_summary:
					tmp = extraction_summary[message_belong_block_name]
					tmp ["incorrect"] += 1
				else:
					tmp = {}
					tmp ["correct"] = 0
					tmp ["incorrect"] = 1
				extraction_summary[message_belong_block_name] = tmp
				tmp = []
				tmp.append(message_line_num)
				tmp.append(message_belong_block_name)
				file_failed_list.append(tmp)
	
	tmp = []
	tmp.append(block_list)
	tmp.append(extraction_summary)
	tmp.append(file_failed_list)
	return tmp

def input_file_block_report_extraction(input_file, block_pattern_list, single_line_pattern_db):
#{{{
	#step 1: single_line_report
	node_id = global_APIs.get_file_node_name(input_file)
	if node_id == "":
		#this file have no node name
		return []
	file_single_line_report = database_opt.read_file_single_line_list(input_file)
	if file_single_line_report == []:
		#this can save a large time
		file_single_line_report = block_learning.input_file_single_line_report_extraction(input_file, single_line_pattern_db)

	#step 2: find succeed block list
	care_last_node_file = 0 
	succeed_block_list = single_line_report_succeed_block_list_analyze(input_file, file_single_line_report, block_pattern_list, single_line_pattern_db, care_last_node_file)
		
	#step 3: convert single line report into block list
	result = single_line_report_convert_into_block_list (succeed_block_list, file_single_line_report, block_pattern_list, single_line_pattern_db)
	block_list = result[0]
	extraction_summary = result[1]
	file_failed_list = result[2]
	
	result = []
	result.append(block_list)
	result.append(file_single_line_report)
	result.append(extraction_summary)
	result.append(file_failed_list)
	return result
#}}}

def is_block_start_line (this_message_pattern_name ,message_belong_block_name, block_pattern_list):
#{{{
	correspond_block_pattern = block_pattern_list[message_belong_block_name]["pattern"]
	pattern_length = len(correspond_block_pattern)
	if correspond_block_pattern[0] == this_message_pattern_name:
		return 1
	else:
		return 0
#}}}


def is_block_finish_line (this_message_pattern_name ,message_belong_block_name, block_pattern_list):
#{{{
	correspond_block_pattern = block_pattern_list[message_belong_block_name]["pattern"]
	pattern_length = len(correspond_block_pattern)
	if correspond_block_pattern[pattern_length - 1] == this_message_pattern_name:
		return 1
	else:
		return 0
#}}}

def block_nest_eliminate (block_list):
#{{{
#32 370 371
#22 369 372
#block_104 16 16
#block_102 15 19
	merge = 1
	while merge == 1:
		merge = 0
		i = 0
		while i < len(block_list) - 1:
			block = block_list[i]
			next_block = block_list[i+1]
			start_line = int(block[1])
			finish_line = int(block[2])
			next_start_line = int(next_block[1])
			next_finish_line = int(next_block[2])

			if start_line >= next_start_line and finish_line < next_finish_line:
				#ARES
				merge = 1 
				del (block_list[i])
			else:
				i = i + 1

	return block_list
#}}}

