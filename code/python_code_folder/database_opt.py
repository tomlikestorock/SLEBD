#!/usr/bin/python
#coding:utf-8
import os
import sys
import re 
import shutil
import global_APIs

def read_single_line_pattern_range_list (input_file, prefix = ""):
#{{{
	single_line_pattern_range_line_pattern_list = {}
	file_mode = global_APIs.get_file_mode(input_file)
	range_pattern_list_path = "sql_database/"
	range_pattern_list_path += file_mode
	if not prefix == "":
		range_pattern_list_path += "/" + str(prefix)
	range_pattern_list_path += "/range_pattern_list"
	range_pattern_list_path += ".txt"
	if os.path.isfile(range_pattern_list_path):	
		fl = open (range_pattern_list_path, "r") 
		while True:
			line_1 = fl.readline()
			line_2 = fl.readline()
			if not line_1 or not line_2:	
				break
			pattern_name = line_1.split()[0]

			range_pattern_file_list = line_2.split()
			range_pattern_list = {}
			i = 0
			while i < len(range_pattern_file_list):
				range_pattern_list[range_pattern_file_list[i]] = int(range_pattern_file_list[i+1])
				i = i + 2	
			single_line_pattern_range_line_pattern_list[pattern_name] = range_pattern_list

		fl.close()	
		
	else:
		return {}
	return single_line_pattern_range_line_pattern_list
#}}}

def output_single_line_pattern_range_list (single_line_pattern_range_line_pattern_list, input_file, prefix = ""):
#{{{
	file_mode = global_APIs.get_file_mode(input_file)
	range_pattern_list_path = "sql_database/"
	range_pattern_list_path += file_mode
	if not prefix == "":
		range_pattern_list_path += "/" + str(prefix)
	range_pattern_list_path += "/range_pattern_list"
	range_pattern_list_path += ".txt"
	fl = open (range_pattern_list_path, "w") 
	for line_pattern_name in single_line_pattern_range_line_pattern_list:
		fl.write(line_pattern_name)
		fl.write(" \n")
		range_pattern_list = single_line_pattern_range_line_pattern_list[line_pattern_name]
		tmp = ""
		for pattern in range_pattern_list:
			tmp += pattern
			tmp += " "	
			tmp += str(range_pattern_list[pattern])
			tmp += " "	
		fl.write(tmp)
		fl.write("\n")
	fl.close()
#}}}

def read_happen_matrix (input_file, prefix = "", file_name_prefix = ""):
#{{{
	happen_matrix = {}
	file_mode = global_APIs.get_file_mode(input_file)
	happen_matrix_path = "sql_database/"
	happen_matrix_path += file_mode
	happen_matrix_path += "/" 
	
	if not prefix == "":
		happen_matrix_path += "/" + str(prefix) + "/"
	if not file_name_prefix == "":
		happen_matrix_path += file_name_prefix + "_"
		
	happen_matrix_path += "happen_matrix"
	happen_matrix_path += ".txt"
	if os.path.isfile(happen_matrix_path):	
		fl = open (happen_matrix_path, "r") 
		while True:
			line_1 = fl.readline()
			line_2 = fl.readline()
			if not line_1 or not line_2:	
				break
			pattern_name = line_1.split()[0]
			next_pattern_list = {}
			next_pattern_file_list = line_2.split()
			i = 0	
			while i < len(next_pattern_file_list) :
				next_pattern_name = next_pattern_file_list[i]
				next_pattern_happen_time = next_pattern_file_list[i+1]
				i = i + 2
				tmp = []
				next_pattern_list[next_pattern_name] = int(next_pattern_happen_time)
			happen_matrix[pattern_name] = next_pattern_list

	else:
		return {}
	return happen_matrix
#}}}

def output_happen_matrix (happen_matrix, input_file, prefix = "", file_name_prefix = ""):
#{{{
	file_mode = global_APIs.get_file_mode(input_file)
	happen_matrix_path = "sql_database/"
	happen_matrix_path += file_mode
	happen_matrix_path += "/" 
	if not prefix == "":
		happen_matrix_path += "/" + str(prefix) + "/"
	if not file_name_prefix == "":
		happen_matrix_path += file_name_prefix + "_"
		
	happen_matrix_path += "happen_matrix"
	happen_matrix_path += ".txt"
	fl = open (happen_matrix_path, "w") 
	for line_pattern_name in happen_matrix:
		fl.write(line_pattern_name)
		fl.write(" \n")
		line_pattern_happen_list = happen_matrix[line_pattern_name]
		tmp = ""
		tmp += "happen_time"
		tmp += " "
		tmp += str(line_pattern_happen_list["happen_time"])
		tmp += " "
		for next_pattern in line_pattern_happen_list:
			if next_pattern == "happen_time":
				continue
			next_pattern_happern_time = line_pattern_happen_list[next_pattern] 	
			tmp += next_pattern
			tmp += " "
			tmp += str(next_pattern_happern_time)
			tmp += " "
		fl.write(tmp)
		fl.write("\n")
	fl.close()
#}}}

def read_single_line_pattern_db(input_file, prefix = ""):
#{{{
	single_line_pattern_db = {}
	file_mode = global_APIs.get_file_mode(input_file)
	single_line_pattern_file_path = "sql_database/"
	single_line_pattern_file_path += file_mode
	if not prefix == "":
		single_line_pattern_file_path += "/" + str(prefix)
	single_line_pattern_file_path += "/single_line_pattern_db.txt"
	if os.path.isfile(single_line_pattern_file_path):	
		fl = open(single_line_pattern_file_path, "r")
		while True:
			line_1 = fl.readline()
			line_2 = fl.readline()
			line_3 = fl.readline()
			if not line_1 or not line_2 or not line_3:	
				break
			pattern_name = line_1.split()[0]
			pattern = convert_string_into_pattern(line_2)
			tmp = {}
			tmp["pattern"] = pattern
			belong_block = line_3.split()
			if len (belong_block) == 1:
				tmp["belong_block"] = ""
			else:
				tmp["belong_block"] = belong_block[1] 
			single_line_pattern_db[pattern_name] = tmp
		fl.close()	
		
	else:
		return {}
	return 	single_line_pattern_db
#}}}

def output_single_line_pattern_db(single_line_pattern_db, input_file, prefix = ""):
#{{{
	file_mode = global_APIs.get_file_mode(input_file)
	node_id_last_file_path = "sql_database/"
	node_id_last_file_path += file_mode
	if not prefix == "":
		node_id_last_file_path += "/" + str(prefix)
	node_id_last_file_path += "/single_line_pattern_db.txt"
	fl = open (node_id_last_file_path, "w") 
	for line_pattern_name in single_line_pattern_db:
		fl.write(line_pattern_name)
		fl.write(" \n")
		line_pattern = single_line_pattern_db[line_pattern_name]["pattern"]
		tmp = ""
		for i in range (0, len(line_pattern)):
			element = line_pattern[i]
			pos = element[0]
			word = element[1]
			
			tmp += str(pos)
			tmp += " "
			tmp += str(word)
			tmp += " "
		fl.write(tmp)
		fl.write("\n")
		
		tmp = ""
		tmp += "belong_block"
		tmp += " "
		tmp += single_line_pattern_db[line_pattern_name]["belong_block"]
		fl.write(tmp)
		fl.write("\n")
	fl.close()
#}}}

def convert_string_into_pattern (string):
#{{{
	pattern = []
	
	string_element_list = string.split()
	i = 0
	while i < len(string_element_list) :
		pos = 	string_element_list[i]
		word = string_element_list[i+1]
		i = i + 2
		tmp = []
		tmp.append(pos)
		tmp.append(word)
		pattern.append(tmp)
	return pattern 
#}}}

def read_node_id_last_list_file(input_file, prefix = ""):
#{{{
	node_id_last_list = {}
	file_mode = global_APIs.get_file_mode(input_file)
	node_id_last_file_path = "sql_database/"
	node_id_last_file_path += file_mode
	if not prefix == "":
		node_id_last_file_path += "/" + str(prefix)
	node_id_last_file_path += "/node_id_last_file.txt" 
	if os.path.isfile(node_id_last_file_path):	
		fl = open(node_id_last_file_path, "r")
		for line in fl.readlines():
			line = line.replace("\n", "")
			line = line.split(" ")
			node_id_last_list[line[0]] = line[1]
		fl.close()	
		
	else:
		return {}
	return 	node_id_last_list
#}}}

def output_node_id_last_list_file(node_id_last_list, input_file, prefix = ""):
#{{{
	file_mode = global_APIs.get_file_mode(input_file)
	node_id_last_file_path = "sql_database/"
	node_id_last_file_path += file_mode
	if not prefix == "":
		node_id_last_file_path += "/" + str(prefix)
	node_id_last_file_path += "/node_id_last_file.txt"
	fl = open (node_id_last_file_path, "w") 
	for node_id in 	node_id_last_list:
		tmp = node_id
		tmp += " "
		tmp += str(node_id_last_list[node_id])
		tmp += "\n"
		fl.write(tmp)
	fl.close()
#}}}

def read_message_closest_message_list (input_file, prefix = ""):
#{{{
	message_closest_message_list = {}
	file_mode = global_APIs.get_file_mode(input_file)
	message_closest_message_file_path = "sql_database/"
	message_closest_message_file_path += file_mode
	if not prefix == "":
		message_closest_message_file_path += "/" + str(prefix)
	message_closest_message_file_path += "/message_closest_message_list.txt"
	if os.path.isfile(message_closest_message_file_path):	
		fl = open (message_closest_message_file_path, "r") 
		while True:
			line_1 = fl.readline()
			line_2 = fl.readline()
			line_3 = fl.readline()
			if not line_1 or not line_2 or not line_3:	
				break
			message_pattern = line_1.split()[0]
			prior_pattern_list = line_2.split()
			follow_pattern_list = line_3.split()
			tmp = {}
			prior_list = []
			for i in range (1, len(prior_pattern_list)):
				prior_list.append(prior_pattern_list[i])
			follow_list = []
			for i in range (1, len(follow_pattern_list)):
				follow_list.append(follow_pattern_list[i])
			tmp["prior"] = prior_list	
			tmp["follow"] = follow_list	
			message_closest_message_list[message_pattern] = tmp
	return 	message_closest_message_list	
#}}}

def output_message_closest_message_list (message_closest_message_list ,input_file, prefix = ""):
#{{{
	file_mode = global_APIs.get_file_mode(input_file)
	message_closest_message_file_path = "sql_database/"
	message_closest_message_file_path += file_mode
	if not prefix == "":
		message_closest_message_file_path += "/" + str(prefix)
	message_closest_message_file_path += "/message_closest_message_list.txt"
	fl = open (message_closest_message_file_path, "w") 
	for message_pattern in message_closest_message_list:
		fl.write(message_pattern)
		fl.write(" \n")
		closest_message_list = message_closest_message_list[message_pattern]
		tmp = ""
		if "prior" in closest_message_list:
			tmp += "prior"
			tmp += " "
			for message in closest_message_list["prior"]:
				tmp += message
				tmp += " "

		fl.write(tmp)
		fl.write("\n")
		tmp = ""
		if "follow" in closest_message_list:
			tmp += "follow"
			tmp += " "
			for message in closest_message_list["follow"]:
				tmp += message
				tmp += " "
		fl.write(tmp)
		fl.write("\n")
	fl.close()
#}}}

def read_block_pattern_list (input_file, prefix = ""):
#{{{
	block_pattern_list = {}	
	
	file_mode = global_APIs.get_file_mode(input_file)
	block_pattern_list_file_path = "sql_database/"
	block_pattern_list_file_path += file_mode
	if not prefix == "":
		block_pattern_list_file_path += "/" + str(prefix)
	block_pattern_list_file_path += "/block_pattern_list.txt"
	if os.path.isfile(block_pattern_list_file_path):	
		fl = open (block_pattern_list_file_path, "r") 
		while True:
			line_1 = fl.readline()
			line_2 = fl.readline()
			line_3 = fl.readline()
			if not line_1 or not line_2 or not line_3:	
				break
			block_name = line_1.split()[0]

			block_pattern_list_tmp = {}
			pattern_list = line_2.split()
			pattern_tmp = []
			i = 0
			while i < len(pattern_list):
				pattern_tmp.append(pattern_list[i])
				i = i + 1	
			block_pattern_list_tmp["pattern"] = pattern_tmp

			happen_count_list = line_3.split()
			happen_count_tmp = {}
			i = 0
			while i < len(happen_count_list):
				happen_count_tmp[happen_count_list[i]] = happen_count_list[i + 1]
				i = i + 2
			block_pattern_list_tmp["happen_count"] = happen_count_tmp
			block_pattern_list[block_name] = block_pattern_list_tmp
	return 	block_pattern_list
#}}}

def output_block_pattern_list (block_pattern_list ,input_file, prefix = ""):
#{{{
	file_mode = global_APIs.get_file_mode(input_file)
	block_pattern_list_file_path = "sql_database/"
	block_pattern_list_file_path += file_mode
	if not prefix == "":
		block_pattern_list_file_path += "/" + str(prefix)
	block_pattern_list_file_path += "/block_pattern_list.txt"
	fl = open (block_pattern_list_file_path, "w") 
	for block in block_pattern_list:
		fl.write(block)
		fl.write(" \n")
		pattern = block_pattern_list[block]["pattern"]
		tmp = ""
		for message in pattern:
			tmp += message
			tmp += " "
		fl.write(tmp)
		fl.write("\n")
		
		happen_count = block_pattern_list[block]["happen_count"]
		tmp = ""
		tmp += "correct"
		tmp += " "
		tmp += str(happen_count["correct"])
		tmp += " "
		tmp += "incorrect"
		tmp += " "
		tmp += str(happen_count["incorrect"])
		fl.write(tmp)
		fl.write("\n")
	fl.close()
#}}}

def output_file_single_line_list(file_single_line_report, input_file):
#{{{
	real_file_name = global_APIs.get_real_file_name(input_file)
	single_line_report_path = "block_report/"
	prefix_path = global_APIs.analyze_node_block_list_prefix_path(input_file)
	if not prefix_path == "":
		single_line_report_path += str(prefix_path)
		single_line_report_path += "/"
	if not  os.path.isdir(single_line_report_path):
		os.mkdir (single_line_report_path)
	single_line_report_path += real_file_name
	single_line_report_path += "_single_line_report"
	single_line_report_path += ".txt"
	fl = open(single_line_report_path, "w")
	for single_line in file_single_line_report:
		tmp = ""
		tmp += str(single_line[0])
		tmp += " "
		tmp += str(single_line[1])
		fl.write(tmp)
		fl.write("\n")
	fl.close()
#}}}

def read_file_single_line_list(input_file):
#{{{
	file_single_line_report = []
	real_file_name = global_APIs.get_real_file_name(input_file)
	single_line_report_path = "block_report/"
	prefix_path = global_APIs.analyze_node_block_list_prefix_path(input_file)
	if not prefix_path == "":
		single_line_report_path += str(prefix_path)
		single_line_report_path += "/"
	#if not  os.path.isdir(single_line_report_path):
		#report error
	single_line_report_path += real_file_name
	single_line_report_path += "_single_line_report"
	single_line_report_path += ".txt"
	if os.path.isfile(single_line_report_path):
		fl = open(single_line_report_path, "r")
		for line in fl.readlines():
			line = line.split()
			tmp = []
			tmp.append(line[0])	
			tmp.append(line[1])
			file_single_line_report.append(tmp)
		fl.close()
	return file_single_line_report
#}}}

def output_file_block_report_list(file_block_report, input_file):
#{{{
	real_file_name = global_APIs.get_real_file_name(input_file)
	block_report_path = "block_report/"
	prefix_path = global_APIs.analyze_node_block_list_prefix_path(input_file)
	if not prefix_path == "":
		block_report_path += str(prefix_path)
		block_report_path += "/"
	if not  os.path.isdir(block_report_path):
		os.mkdir (block_report_path)
	block_report_path += real_file_name
	block_report_path += "_block_report"
	block_report_path += ".txt"
	fl = open(block_report_path, "w")
	for block in file_block_report:
		tmp = ""
		tmp += str(block[0])
		tmp += " "
		tmp += str(block[1])
		tmp += " "
		tmp += str(block[2])
		fl.write(tmp)
		fl.write("\n")
	fl.close()
#}}}

def read_file_block_report_list(input_file):
#{{{
	file_block_report = []
	real_file_name = global_APIs.get_real_file_name(input_file)
	block_report_path = "block_report/"
	prefix_path = global_APIs.analyze_node_block_list_prefix_path(input_file)
	if not prefix_path == "":
		block_report_path += str(prefix_path)
		block_report_path += "/"
	#if not  os.path.isdir(block_report_path):
		#report error
	block_report_path += real_file_name
	block_report_path += "_block_report"
	block_report_path += ".txt"
	if os.path.isfile(block_report_path):
		fl = open(block_report_path, "r")
		for line in fl.readlines():
			line = line.split()
			tmp = []
			tmp.append(line[0])	
			tmp.append(line[1])
			tmp.append(line[2])
			file_block_report.append(tmp)
	fl.close()
	return file_block_report
#}}}

def output_extract_error_list(file_list_error, input_file):
#{{{
	error_report_path = "block_report/"
	prefix_path = global_APIs.analyze_node_block_list_prefix_path(input_file)
	if not prefix_path == "":
		error_report_path += str(prefix_path)
		error_report_path += "/"
	if not  os.path.isdir(error_report_path):
		os.mkdir (error_report_path)
	error_report_path += "extract_error"
	error_report_path += ".txt"
	fl = open(error_report_path, "w")
	for file_name in file_list_error:
		fl.write(file_name)
		fl.write("\n")
		for error in file_list_error[file_name]:
			fl.write(str(error) + "\n")

	fl.close()
#}}}

def read_node_stack_last_block_list(input_file):
#{{{
	#input_file is for future file mode
	node_stack_last_block_list = {}

	node_stack_path = "block_report/node_stack.txt"
	if os.path.isfile(node_stack_path):
		fl = open(node_stack_path, "r")
		while True:
			node_tmp = {}
			line_1 = fl.readline()
			line_2 = fl.readline()
			line_3 = fl.readline()
			if not line_1 or not line_2 or not line_3:	
				break
			node_id = line_1.split()[0]
			node_tmp["last_file_path"] = line_2.split()[0]
			block_stack = []
			block_list = line_3.split()
			i = 0
			while i < len(block_list):
				block_name = block_list[i]
				block_line = block_list[i+1]
				tmp = []
				tmp.append(block_name)	
				tmp.append(block_line)	
				block_stack.append(tmp)
				i = i + 2
			node_tmp["stack"] = block_stack
			node_stack_last_block_list[node_id] = node_tmp
		fl.close()
	return node_stack_last_block_list
#}}}

def output_node_stack_last_block_list(input_file, node_stack_last_block_list):
#{{{
	#input_file is for future file mode
	node_stack_path = "block_report/node_stack.txt"
	fl = open(node_stack_path, "w")
	for node_id in node_stack_last_block_list:
		fl.write(node_id)
		fl.write(" \n")
		fl.write(node_stack_last_block_list[node_id]["last_file_path"])
		fl.write(" \n")
		block_stack = node_stack_last_block_list[node_id]["stack"]
		tmp = ""
		for block in block_stack:
			tmp += block[0]
			tmp += " "
			tmp += str(block[1])
			tmp += " "
		fl.write(tmp)
		fl.write("\n")
		
	fl.close()
#}}}

def update_last_node_file_block_list(last_node_file, match_last_node_block_list_start):
#{{{
	last_block_name = match_last_node_block_list_start[0]
	last_block_start_line = int(match_last_node_block_list_start[1])
	last_node_block_list = read_file_block_report_list(last_node_file)
	new_block_list = []
	node_last_block = last_node_block_list[len(last_node_block_list) - 1]
	node_last_line_num = node_last_block[2]
	for i in range (0, len(last_node_block_list)):
		block = last_node_block_list[i]
		if int(block[1]) < last_block_start_line :
			#block start line
			new_block_list.append(block)
		else:
			tmp = []
			last_block_name += "_upper_half"
			tmp.append(last_block_name)
			tmp.append(last_block_start_line)
			tmp.append(node_last_line_num)
			#until block start line equal to last block start line
			new_block_list.append(tmp)
			break
	output_file_block_report_list(new_block_list, last_node_file)	
#}}}

def read_done_sub_folder_list(sub_folder):
#{{{
	done_sub_folder_list = []
	file_mode = global_APIs.get_file_mode(sub_folder)
	done_sub_folder_list_file_path = "sql_database/"
	done_sub_folder_list_file_path += file_mode
	done_sub_folder_list_file_path += "/done_sub_folder_list.txt" 
	if os.path.isfile(done_sub_folder_list_file_path):	
		fl = open(done_sub_folder_list_file_path, "r")
		for line in fl.readlines():
			line = line.replace("\n", "")
			line = line.split(" ")
			done_sub_folder_list.append(line[0])
		fl.close()	
		
	else:
		return [] 
	return 	done_sub_folder_list
#}}}

def output_done_sub_folder_list(done_sub_folder_list, sub_folder):
#{{{
	file_mode = global_APIs.get_file_mode(sub_folder)
	done_sub_folder_list_file_path = "sql_database/"
	done_sub_folder_list_file_path += file_mode
	done_sub_folder_list_file_path += "/done_sub_folder_list.txt" 
	fl = open (done_sub_folder_list_file_path, "w") 
	for sub_folder in done_sub_folder_list:
		tmp = ""
		tmp += sub_folder
		tmp += " \n"
		fl.write(tmp)
	fl.close()
#}}}

def output_this_round_affect_message_list(sub_folder, new_found_single_line_pattern, need_update_single_line_pattern_list, left_new_found_single_line_pattern_list, affected_message_list, prefix):
#{{{
	file_mode = global_APIs.get_file_mode(sub_folder)
	affect_message_file_path = "sql_database/"
	affect_message_file_path += file_mode
	if not prefix == "":
		 affect_message_file_path += "/" + str(prefix)
	affect_message_file_path += "/affected_message.txt" 
	fl = open (affect_message_file_path, "w")
	fl.write("new_found_single_line_pattern\n")
	tmp = ""
	for message in new_found_single_line_pattern:
		tmp += message + " "
	tmp += "\n"
	fl.write (tmp)
	fl.write("need_update_single_line_pattern_list\n") 
	tmp = ""
	for message in need_update_single_line_pattern_list:
		tmp += message + " "
	tmp += "\n"
	fl.write (tmp)
	fl.write("left_new_found_single_line_pattern_list\n") 
	tmp = ""
	for message in left_new_found_single_line_pattern_list:
		tmp += message + " "
	tmp += "\n"
	fl.write (tmp)
	fl.write("affected_message_list\n") 
	tmp = ""
	for message in affected_message_list:
		tmp += message + " "
	tmp += "\n"
	fl.write (tmp)
	fl.close()
#}}}

def read_this_round_affect_message_list(sub_folder,  prefix):
	file_mode = global_APIs.get_file_mode(sub_folder)
	affect_message_file_path = "sql_database/"
	affect_message_file_path += file_mode
	if not prefix == "":
		 affect_message_file_path += "/" + str(prefix)
	affect_message_file_path += "/affected_message.txt"
	if os.path.isfile( affect_message_file_path):
		fl = open (affect_message_file_path, "r")
		line_list = fl.readlines()
		new_found_single_line_pattern = []	
		need_update_single_line_pattern_list = []
		left_new_found_single_line_pattern_list = []
		affected_message_list = []

		new_found_line = line_list[1]
		need_update_line = line_list[3]
		left_new_line = line_list[5]
		affected_line = line_list[7]
		for message in new_found_line.split():
			if message == "\n":
				continue
			new_found_single_line_pattern.append(message)
		for message in need_update_line.split():
			if message == "\n":
				continue
			need_update_single_line_pattern_list.append(message)
		for message in left_new_line.split():
			if message == "\n":
				continue
			left_new_found_single_line_pattern_list.append(message)
		for message in affected_line.split():
			if message == "\n":
				continue
			affected_message_list.append(message)
		tmp = []
		tmp.append(new_found_single_line_pattern)	
		tmp.append(need_update_single_line_pattern_list)	
		tmp.append(left_new_found_single_line_pattern_list)	
		tmp.append(affected_message_list)	
		return tmp
	else:
		return []


#testing
def block_pattern_list_summary (input_file, show_report = 0):
	#this input_file is just a file mode tragger
	file_mode = global_APIs.get_file_mode(input_file)
	block_pattern_list_file_path = "sql_database/"
	block_pattern_list_file_path += file_mode
	file_list = global_APIs.get_folder_file_list(block_pattern_list_file_path)
	last_sub_folder = global_APIs.get_latest_sql_db_path(input_file)

	block_pattern_list = read_block_pattern_list(input_file, last_sub_folder)
	single_line_pattern_db = read_single_line_pattern_db(input_file, last_sub_folder)

	block_covered_message_list = {} 
	block_covered_message_num = 0
	for block in 	block_pattern_list:
		block_pattern = block_pattern_list[block]["pattern"]
		block_covered_message_num += len(block_pattern)
		for message in block_pattern:
			if not message in block_covered_message_list:
				tmp = [block]
				block_covered_message_list[message] = tmp
			else:
				print message
				tmp = block_covered_message_list[message]
				tmp.append(block)
				block_covered_message_list[message] = tmp
				

	message_have_block_info_list = []
	message_have_block_info_num = 0
	for single_line_pattern in single_line_pattern_db:
		if not single_line_pattern_db[single_line_pattern]["belong_block"] == "":
			message_have_block_info_num += 1
			if not single_line_pattern in message_have_block_info_list:
				message_have_block_info_list.append(single_line_pattern)
	if show_report == 1:	
		print "==================================================="
		print "EBD summary report"
		print "	block_covered_message_num: " + str(block_covered_message_num)
		print "	message_have_block_info_num: " + str(message_have_block_info_num)
		print "	total_single_line_message: " + str(len(single_line_pattern_db))
		print "	total_block: " + str(len(block_pattern_list))
		print "==================================================="
	error_list = {}
	
	for message in block_covered_message_list:
		if len(block_covered_message_list[message]) > 1:
			error_list [message] = block_covered_message_list[message]
		
	return error_list


def read_block_belong_node_list ():
	block_belong_node_list = {}
	fl = open("sequence_tmp_report/block_belong_node.txt" , "r")
	lines = fl.readlines()
	fl.close()
	i = 0	
	while i < len(lines):
		block_name_line = lines[i]
		block_belong_node_line = lines[i+1]
		block_name = block_name_line.split()[1]
		#0 is "main_block"
		block_belong_node = block_belong_node_line.split()
		block_belong_node_list[block_name] = block_belong_node
		i += 2


	return block_belong_node_list
