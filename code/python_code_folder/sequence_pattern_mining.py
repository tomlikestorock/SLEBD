#!/usr/bin/python
import os
import operator
import re
import shutil
import time 
import global_APIs 
ignore_repeat_block = 1

def block_sequence_detect (folder_name):
	fl = open("sequence_tmp_report/analyze_block_node.txt", "r")
	node_line = fl.readline()
	block_line = fl.readline()	
	node_list = node_line.split()
	care_block_list = block_line.split()
	
	fl.close()
	print "block list " + str(len(care_block_list))
	"""
	care_block_list = []
	care_block_list.append("block_A")	
	care_block_list.append("block_B")	
	care_block_list.append("block_C")	
	care_block_list.append("block_D")	
	care_block_list.append("block_E")
	"""

	#prior matrix 
	#{{{
	time_1 = time.time()	
	file_list = global_APIs.get_folder_file_list (folder_name)
	total_block_report_list = []
	for block_report_file in file_list:
		print block_report_file
		fl = open(block_report_file, "r")
		node_block_lines = fl.readlines()
		node_block_report = []
		for line in node_block_lines:
			block_name = line.split()[0]
			if block_name in care_block_list:
				node_block_report.append(block_name)
		total_block_report_list.append(node_block_report)
		fl.close()
	result = multi_file_sequence_prior_matrix_gen(total_block_report_list, care_block_list)
	prior_matrix = result[0]
	prior_matrix_store (prior_matrix)
	prior_matrix = prior_matrix_read()
	print "prior_matrix done"
	time_2 = time.time()	

	#}}}
	#status_matrix
	total_status_matrix = gen_status_matrix_based_on_prior_matrix (care_block_list, prior_matrix)
	status_matrix_store(total_status_matrix)
	total_status_matrix = status_matrix_read()
	print "status_matrix done"
	time_3 = time.time()	

	#for block in status_matrix:
	#	print block
	#	print status_matrix[block]


	#critical_path
	critical_path = []
	#could be nothing, don't be surprised
	#critical_path_candidate_list = find_critical_path_candidate_list_from_status_matrix(care_block_list, total_status_matrix)
	#critical_path = find_sequential_pattern_from_candidate_list(critical_path_candidate_list, total_status_matrix)
	#print "critical_path done"
	#sub_paths
	sub_path_block_candidate_list = []
	for block in care_block_list:
		if not block in critical_path:
			sub_path_block_candidate_list.append(block)
	print "sub_path_WIL_length " + str( len(sub_path_block_candidate_list))
	#generate 2 rounds
	for i in range (0, 1):
		sorted_candidate_list = []
		jump_step = 30 
		for j in range (i*jump_step, len(sub_path_block_candidate_list)):
			sorted_candidate_list.append(sub_path_block_candidate_list[j])
		for j in range (0, i*jump_step):
			sorted_candidate_list.append(sub_path_block_candidate_list[j])
		sub_path_list = find_sub_path(sorted_candidate_list, total_status_matrix, prior_matrix)
		
		print "round " + str(i)
		print len(sub_path_list)


		sub_path_result = {}
		sub_path_result["critical_path"] = critical_path
		sub_path_num = 0
		for sub_path in sub_path_list:
			sub_path_name = "sub_path_" + str(sub_path_num)
			sub_path_result[sub_path_name] = sub_path
			sub_path_num += 1
		
		sequence_list_store(sub_path_result , i)	
	print "sub_path done"
	time_4 = time.time()	
	print "prior matrix gen time: " + str(time_2 - time_1)
	print "status matrix gen time: " + str(time_3 - time_2)
	print "sub sequence gen time: " + str(time_4 - time_3)


	return sub_path_result



#path find
#find_critical_path_candidate_list_from_status_matrix
#find_sequential_pattern_from_candidate_list
#find_sub_path
def WI_insert_into_TS (WI, TS, insert_pos, TSL_append_TS_list, PM):
	TS_WI = list(TS)
	TS_WI.insert(insert_pos, WI)
	if not TS_WI in TSL_append_TS_list:
		TSL_append_TS_list.append(TS_WI)
	return TSL_append_TS_list

def find_sub_path (WIL, SM, PM):
#{{{
	#WIL: waiting item list
	#SM: status matrix
	#PM: prior matrix
	#TSL: temporary sequence list
	#WITIL: Waiting item tangle item list
	TSL = []
	done_block_list = []
	WI = WIL[0]
	TSL.append([WI])
	WITIL = SM[WI]["tangle"]
	for WITI in WITIL:
		TSL.append([WITI])



	for WIL_index in range (1, len(WIL)):
		if WIL_index % 10 == 0:
			print "analyzed block num " + str(WIL_index)
			print len(TSL)
		WI = WIL[WIL_index]
		done_block_list.append(WI)
		WITIL = SM[WI]["tangle"]
			
		TSL_delete_index_list = []
		TSL_append_TS_list = []
		for TSL_index in range(0, len(TSL)):
			TS = TSL[TSL_index]
			if WI in TS:
				continue
			insert_pos = search_sub_block_insert_into_growing_pattern_position (TS, WI, SM)

			if not insert_pos == -1:
				TSL_delete_index_list.append(TSL_index)
				TSL_append_TS_list = WI_insert_into_TS (WI, TS, insert_pos, TSL_append_TS_list, PM)
					
				for WITI in WITIL:
					#branch
					if WITI in done_block_list:
						continue
					if not WITI in WIL:
						continue
					insert_pos = search_sub_block_insert_into_growing_pattern_position (TS, WITI, SM)
					if not insert_pos == -1:
						TSL_append_TS_list = WI_insert_into_TS (WITI, TS, insert_pos, TSL_append_TS_list, PM)


		#delete
		new_TSL = []
		for TSL_index in range (0, len(TSL)):
			if TSL_index not in TSL_delete_index_list:
				new_TSL.append(TSL[TSL_index])
		for TS in TSL_append_TS_list:
			if not TS in new_TSL:
				new_TSL.append(TS)
		TSL = list(new_TSL)
		#print "round " + str(WIL_index) +  " WI " + WI
		#print TSL
	
	return TSL 
#}}}


def find_sub_path_1 (sorted_left_list, status_matrix, prior_matrix):
#{{{
	growing_list = []
	done_block_list = []
	for main_list_index in range (0, len(sorted_left_list)):
		if main_list_index % 10 == 0:
			print "analyzed block num " + str(main_list_index)
		main_block = sorted_left_list[main_list_index]
		done_block_list.append(main_block)
		#print "detecting ============================================"
		#print main_block
		#print main_list_index
		main_block_tangle_list = status_matrix[main_block]["tangle"]
		if main_list_index == 0:
			tmp = []
			tmp.append(main_block)
			growing_list.append(tmp)
			for tangle_block in main_block_tangle_list:
				if not tangle_block in sorted_left_list:
					continue
				tmp = []
				tmp.append(tangle_block)
				growing_list.append(tmp)
		else:
			inserted = 0
			delete_list = []
			for growing_list_index in range(0, len(growing_list)):
				growing_pattern = growing_list[growing_list_index]
				if main_block in growing_pattern:
					inserted = 1
					continue
				insert_pos = search_sub_block_insert_into_growing_pattern_position (growing_pattern, main_block, status_matrix)
				if not insert_pos == -1:
					inserted = 1
					delete_list.append(growing_list_index)
					new_list = list(growing_pattern)
					new_list.insert(insert_pos, main_block)
					if not new_list in growing_list:
						growing_list.append(new_list)
					for tangle_block in main_block_tangle_list:
						#branch
						if tangle_block in done_block_list:
							continue
						if not tangle_block in sorted_left_list:
							continue
						insert_pos = search_sub_block_insert_into_growing_pattern_position (growing_pattern, tangle_block, status_matrix)
						if not insert_pos == -1:
							new_list = list(growing_pattern)
							new_list.insert(insert_pos, tangle_block)
							if not new_list in growing_list:
								growing_list.append(new_list)
			if inserted == 0:
				tmp = []
				tmp.append(main_block)
				growing_list.append(tmp)
			#delete
			new_growing_list = []
			for growing_pattern_index in range (0, len(growing_list)):
				if growing_pattern_index not in delete_list:
					new_growing_list.append(growing_list[growing_pattern_index])

			growing_list = list(new_growing_list)	
		#print growing_list
	return growing_list
#}}}

def find_critical_path_candidate_list_from_status_matrix (candidate_analyze_list, status_matrix):
#{{{
	critical_path_candidate_block_list = []
	for main_block in status_matrix:
		if len(status_matrix[main_block]["tangle"]) == 0:
			#only no tangle can be added into critical path
			critical_path_candidate_block_list.append(main_block)
	return critical_path_candidate_block_list
#}}}

def find_sequential_pattern_from_candidate_list (candidate_list, status_matrix):
#{{{
	growing_pattern = []
	for main_block in candidate_list:
		if growing_pattern == []:
			growing_pattern.append(main_block)
		else:
			insert_position = search_sub_block_insert_into_growing_pattern_position(growing_pattern, main_block, status_matrix)
			if not insert_position == -1:
				growing_pattern.insert(insert_position, main_block)
	return growing_pattern	

def search_sub_block_insert_into_growing_pattern_position_1 (growing_pattern, insert_block, status_matrix):
#{{{
	insert_position = -1 
	possible_position = 0
	forward_switch = 0
	for i in range (0, len(growing_pattern)):
		list_block = growing_pattern[i]
		if insert_block in status_matrix[list_block]["tangle"] or list_block in status_matrix[insert_block]["tangle"]:
			return -1
		if forward_switch == 0:	
			if insert_block in status_matrix[list_block]["prior"]:
				insert_position = i + 1
				#insert_block is after list_block, do nothing and push position forward
				
			elif insert_block in status_matrix[list_block]["after"]:
				insert_position = i
				forward_switch = 1
				
			elif insert_block in status_matrix[list_block]["wrap_out"]: 
				#insert_block is wrapped by list_block
				#wrap_out is same as prior
				insert_position = i + 1
			
			elif insert_block in status_matrix[list_block]["wrap_in"]:
				#list_block is wrapped by insert_block	
				#wrap_in is same as after
				insert_position = i
				forward_switch = 1

		if forward_switch == 1:
			if list_block in status_matrix[insert_block]["after"]:
				if insert_position == -1:
					insert_position = i
			elif list_block in status_matrix[insert_block]["wrap_out"]: 
				#insert_block is wrapped by list_block
				if insert_position == -1:
					insert_position = i
			
			elif list_block in status_matrix[insert_block]["wrap_in"]:
				#list_block is wrapped by insert_block	
				if insert_position == -1:
					insert_position = i + 1
	
	return insert_position
#}}}

def search_sub_block_insert_into_growing_pattern_position (growing_pattern, insert_block, status_matrix):
#{{{
	for i in range (0, len(growing_pattern)):
		list_block = growing_pattern[i]
		if insert_block in status_matrix[list_block]["tangle"] or list_block in status_matrix[insert_block]["tangle"]:
			return -1
	
	insert_position = -1 
	forward_switch = 0
	for i in range (0, len(growing_pattern)):
		list_block = growing_pattern[i]
		if forward_switch == 0:	
			if insert_block in status_matrix[list_block]["prior"] or insert_block in status_matrix[list_block]["wrap_out"]:
				insert_position = i + 1
				#insert_block is after list_block, do nothing and push position forward
				
			elif insert_block in status_matrix[list_block]["after"] or insert_block in status_matrix[list_block]["wrap_in"]:
				insert_position = i
				break
	
	return insert_position
#}}}
#}}}

#matrix operations
#multi_file_sequence_prior_matrix_gen
#gen_prior_matrix_from_candidate_list
#gen_status_matrix_based_on_prior_matrix
#search_prior_matrix_for_conflict
#{{{
def multi_file_sequence_prior_matrix_gen (block_report_list, care_block_list):
#{{{
	#we don't have a candidate_analyze_list any more. if in the future any block happen time is less than threshold, we need to erase it from the matrix
	#can add block name threshold filter here
	
	#initialize
	prior_matrix = {}	
	for main_block in care_block_list:
		main_block_sub_list = {}
		for sub_block in care_block_list:
			sub_block_record = {}
			sub_block_record["open"] = "no"
			sub_block_record["count"] = 0 
			sub_block_record["HC"] = 0 
			main_block_sub_list[sub_block] = sub_block_record
		main_block_sub_list["happen_count"] = 0
		prior_matrix[main_block] = main_block_sub_list
	for node_block_report in block_report_list:
		result = gen_prior_matrix_from_one_sequence(prior_matrix, care_block_list, node_block_report)
		prior_matrix = result[0]
	

	
	tmp = []
	tmp.append(prior_matrix)
	return tmp
#}}}

def gen_prior_matrix_from_one_sequence (prior_matrix, care_block_list, node_block_report):
#already done, including happen_count and last block index
#very useful!
#{{{
	#every block record should close all its sub block
	#if see this main_block again, reopen all its sub blocks

	previous_block = ""
	this_report_happened_block_list = []
	this_report_care_block_happen_time_list = {}
	for report_list_block in node_block_report:
		if not report_list_block in care_block_list:
			continue
		if len(report_list_block) == 1:
			report_list_block = report_list_block[0]
		if not 	report_list_block in this_report_happened_block_list:
			this_report_happened_block_list.append(report_list_block)
		
		if ignore_repeat_block == 0 or not report_list_block == previous_block:
			if not 	report_list_block in this_report_care_block_happen_time_list:
				this_report_care_block_happen_time_list[report_list_block] = 1 
			else:
				this_report_care_block_happen_time_list[report_list_block] += 1

		main_block_sub_list = prior_matrix[report_list_block]
		for sub_block in main_block_sub_list:
			if sub_block == "happen_count" or sub_block == "last_block":
				#special index
				continue
			main_block_sub_list[sub_block]["open"] = "yes"

		for main_block in prior_matrix:
			if prior_matrix[main_block][report_list_block]["open"] == "yes":
				prior_matrix[main_block][report_list_block]["count"] += 1
				prior_matrix[main_block][report_list_block]["open"] = "no"
		previous_block = report_list_block

	for report_list_block in this_report_happened_block_list:
		prior_matrix[report_list_block]["happen_count"]	+= this_report_care_block_happen_time_list[report_list_block]
		for other_block in this_report_happened_block_list:
			if other_block == report_list_block:
				continue
			prior_matrix[report_list_block][other_block]["HC"] += this_report_care_block_happen_time_list[report_list_block]


	#now, previous_block is the last block, we can record it
	if previous_block in prior_matrix:	
		last_block_sub_list = prior_matrix[previous_block]
		last_block_sub_list["last_block"] = "yes"
		prior_matrix[previous_block] = last_block_sub_list
	
	for main_block in prior_matrix:
		for sub_block in care_block_list:
			prior_matrix[main_block][sub_block]["open"] = "no" 
		
	
	tmp = []
	tmp.append(prior_matrix)
	return tmp
#}}}

def gen_status_matrix_based_on_prior_matrix (candidate_analyze_list, prior_matrix):
#{{{
	#one block can only have 4 status with others:
	#1) prior: B_1, B_2
	#2) after: B_2, B_1
	#3) equal: B_2, B_1, B_2 (B_2 -> B_1 = 1, B_1 -> B_2 = 1)
	#4) tangle: B_2, B_1, B_1, B_2
	total_status_matrix = {}
	for main_block in candidate_analyze_list:
		status_list = {}
		prior_list = []
		after_list = []
		wrap_out_list = []
		wrap_in_list = []
		tangle_list = []
		for sub_block in candidate_analyze_list:
			if main_block == sub_block:
				continue
			forward_conflict = search_prior_matrix_for_conflict(main_block, sub_block, prior_matrix)
			backward_conflict = search_prior_matrix_for_conflict(sub_block, main_block, prior_matrix)

			if forward_conflict == 0 and backward_conflict == 1:
				#prior
				prior_list.append(sub_block)
			elif forward_conflict == 1 and backward_conflict == 0:
				#after
				after_list.append(sub_block)
			elif forward_conflict == 0 and backward_conflict == 0:
				#equal
				if prior_matrix[main_block]["happen_count"] >= prior_matrix[sub_block]["happen_count"]:
					#main_block is wrapping sub_block
					wrap_out_list.append(sub_block)		
				else:
					#main_block been wrapped by sub_block
					wrap_in_list.append(sub_block)		
			elif forward_conflict == 1 and backward_conflict == 1:
				#tangle, or should we say it's real conflict
				tangle_list.append(sub_block)
		status_list["prior"] = prior_list	
		status_list["after"] = after_list	
		status_list["wrap_out"] = wrap_out_list	
		status_list["wrap_in"] = wrap_in_list	
		status_list["tangle"] = tangle_list
		total_status_matrix[main_block] = status_list	


	return total_status_matrix	
#}}}


def search_prior_matrix_for_conflict(main_block, candidate_block, prior_matrix):
#{{{
	threshold_tolerance = 1.0
	#threshold is here
	#we can use this threshold to tolerate slight fault in training set

	#only a patch, but it can still self control. this is the last defence line
	if not main_block in prior_matrix or not candidate_block in prior_matrix:
		return 1


	main_block_sub_list = prior_matrix[main_block]
	candidate_block_sub_list = prior_matrix[candidate_block]
	candidate_block_happen_time = candidate_block_sub_list[main_block]["HC"]
	main_block_happen_time = main_block_sub_list[candidate_block]["HC"]
	if candidate_block in main_block_sub_list:
		main_block_prior_candidate_block_count = main_block_sub_list[candidate_block]["count"]
	else: 
		return 1
	if main_block in candidate_block_sub_list:
		candidate_block_prior_main_block_count = candidate_block_sub_list[main_block]["count"]
	else: 
		return 1
	
	if main_block_happen_time <= candidate_block_happen_time:
		valid_happen_time = main_block_happen_time
	else:
		valid_happen_time = candidate_block_happen_time




	if valid_happen_time == 1:
		valid_happen_time = main_block_happen_time
 
	if main_block_prior_candidate_block_count >= valid_happen_time * threshold_tolerance:
		#main and candidate is following a sequence
		#we don't need to care about candidate 
		return 0

	#candidate_block_prior_main_block_count >= (valid_happen_time - 1) * threshold_tolerance:
	return 1
#}}}


#}}}

#test
#sub_path_support_time_list_gen
#sequence_file_test
def sub_path_support_time_list_gen(sub_path_list):
#{{{
	prior_matrix = prior_matrix_read()
	sub_path_support_time_list = {}
	for sub_path_name in sub_path_list:
		sub_path = sub_path_list[sub_path_name]
		support_report = get_sub_path_support_report (sub_path, prior_matrix)
		support_time = support_report[0]
		sub_path_support_time_list[sub_path_name] = support_time
	return sub_path_support_time_list
#}}}

def get_sub_path_support_report(sub_path, prior_matrix):
	support_time = 0
	support_block = ""
	for block in sub_path:
		block_happen_time = prior_matrix[block]["happen_count"]
		if support_time == 0:
			support_time = block_happen_time
			support_block = block
		if block_happen_time < support_time:
			support_time = block_happen_time
			support_block = block
	tmp = []
	tmp.append(support_time)
	tmp.append(support_block)
	return tmp

def sequence_file_test (folder_name):
#{{{
	sub_path_list = sequence_list_read(0)
	sub_path_support_time_list = sub_path_support_time_list_gen(sub_path_list)

	file_list = global_APIs.get_folder_file_list (folder_name)
	total_block_report_list = {}
	report_fl = open("sequence_tmp_report/file_test_report.txt", "w")

	fl = open("sequence_tmp_report/analyze_block_node.txt", "r")
	node_line = fl.readline()
	block_line = fl.readline()	
	node_list = node_line.split()
	care_block_list = block_line.split()
	fl.close()


	
	for sub_path_name in sub_path_list:
		total_block_report_list[sub_path_name] = 0


	for block_report_file in file_list:
		report_fl.write("testing: " + block_report_file + "\n")
		report_fl.write("==================================================\n")
		print block_report_file
		block_file_list = []
		fl = open(block_report_file, "r")
		node_block_lines = fl.readlines()
		for line in node_block_lines:
			block_name = line.split()[0]
			if block_name in care_block_list:
				block_file_list.append(block_name)
		fl.close()
		
		for sub_path_name in sub_path_list:
			#if not sub_path_name == "sub_path_1":
			#	continue
			sub_path = sub_path_list[sub_path_name]
			if sub_path == []:
				continue

			total_matched_sub_path = match_one_sub_path_with_one_sequence(sub_path ,block_file_list)
#{{{
			"""
			sub_path_start_block = sub_path[0]
			sub_path_finish_block = sub_path[len(sub_path) - 1]
			sub_path_index = 0
			sub_path_forward_range = 4 
			matched_sub_path = []
			total_matched_sub_path = []
			for block_list_num in range(0, len(block_file_list)):
				block = block_file_list[block_list_num]
				if not sub_path_index == 0 and block == sub_path_start_block:
					total_matched_sub_path.append(matched_sub_path)
					matched_sub_path = [sub_path_start_block]
					continue

				for i in range (0, sub_path_forward_range):
					if sub_path_index + i >= len(sub_path):
						break
					if block == sub_path[sub_path_index + i]:
						#match
						matched_sub_path.append(block)
						sub_path_index += i + 1
						if block == sub_path_finish_block:
							total_matched_sub_path.append(matched_sub_path)
							sub_path_index = 0
							matched_sub_path = []
						break
			"""
#}}}

			error_count, not_fully_match_count, success_count = matched_sub_path_summary(sub_path, total_matched_sub_path)
			#{{{
			"""
			error_count = 0
			not_fully_match_count = 0
			success_count = 0 
			for matched_sub_path in total_matched_sub_path:
				if not len(matched_sub_path) == len(sub_path):
					cover_ratio = float(len(matched_sub_path)) / float(len(sub_path))
					if cover_ratio > 0.95:
						not_fully_match_count += 1
						#total_block_report_list[sub_path_name] += 1
					else:
						error_count += 1
				else:
					success_count += 1
			"""
			#}}}
			
			total_block_report_list[sub_path_name] += success_count 
			if error_count > 0:
				report_fl.write("	error: " + sub_path_name + " error count: " + str(error_count) + "\n")
			if not_fully_match_count > 0:
				report_fl.write("	warning: " + sub_path_name + " not fully match count: " + str(not_fully_match_count) + "\n")

	report_fl.write("====================================\n")
	for sub_path_name in total_block_report_list:
		real_happened_time = total_block_report_list[sub_path_name]
		support_time = sub_path_support_time_list[sub_path_name]
		if not real_happened_time >= support_time:
			#print "warning! " + sub_path_name + " " +  str(real_happened_time) + " " + str(support_time)
			report_fl.write("warning! " + sub_path_name + " " +  str(real_happened_time) + " " + str(support_time) + "\n")
			
	report_fl.close()	
#}}}

def matched_sub_path_summary(sub_path, total_matched_sub_path):
	error_count = 0
	not_fully_match_count = 0
	success_count = 0 
	for matched_sub_path in total_matched_sub_path:
		if not len(matched_sub_path) == len(sub_path):
			cover_ratio = float(len(matched_sub_path)) / float(len(sub_path))
			if cover_ratio > 0.95:
				not_fully_match_count += 1
				#total_block_report_list[sub_path_name] += 1
			else:
				error_count += 1
		else:
			success_count += 1
	return error_count, not_fully_match_count, success_count	


def match_one_sub_path_with_one_sequence(sub_path ,block_file_list):
#{{{
	sub_path_start_block = sub_path[0]
	sub_path_finish_block = sub_path[len(sub_path) - 1]
	sub_path_index = 0
	sub_path_forward_range = 4 
	matched_sub_path = []
	total_matched_sub_path = []
	for block_list_num in range(0, len(block_file_list)):
		block = block_file_list[block_list_num]
		if not sub_path_index == 0 and block == sub_path_start_block:
			total_matched_sub_path.append(matched_sub_path)
			matched_sub_path = [sub_path_start_block]
			continue

		for i in range (0, sub_path_forward_range):
			if sub_path_index + i >= len(sub_path):
				break
			if block == sub_path[sub_path_index + i]:
				#match
				matched_sub_path.append(block)
				sub_path_index += i + 1
				if block == sub_path_finish_block:
					total_matched_sub_path.append(matched_sub_path)
					sub_path_index = 0
					matched_sub_path = []
				break
	return total_matched_sub_path
#}}}

def error_sequence_test(folder_name, sequence_name):
	prior_matrix = prior_matrix_read()
	sub_path_list = sequence_list_read(0)
	sub_path = sub_path_list[sequence_name]
	support_report = get_sub_path_support_report (sub_path, prior_matrix)
	support_num = support_report[0]
	support_block = support_report[1]
	file_list = global_APIs.get_folder_file_list (folder_name)
	
	for block_report_file in file_list:
		block_file_list = []
		fl = open(block_report_file, "r")
		node_block_lines = fl.readlines()
		for line in node_block_lines:
			block_name = line.split()[0]
			block_file_list.append(block_name)
		fl.close()

		support_block_happen_this_round = 0

		sub_path_index = 0
		succeed = 0
		match_list = []
		for i in range(0, len(block_file_list)):
			block = block_file_list[i]
			if block == support_block:
				support_block_happen_this_round += 1
			path_block = sub_path[sub_path_index]
			if block == path_block:
				tmp = [block, i]
				match_list.append(tmp)
				sub_path_index += 1
			if sub_path_index == len(sub_path):
				sub_path_index = 0
				#succeed
				succeed += 1
		if not 	support_block_happen_this_round == succeed:
			print block_report_file
			print "support_block " + support_block + " " + str(support_block_happen_this_round)
			print "succeed " + str(succeed)
			for tmp in match_list:
				print tmp


def all_sequence_lists_compare(test_rounds):
#{{{
	for i in range (0, test_rounds - 1):
		print "round " + str(i)
		sequence_list_1 = sequence_list_read(i)
		sequence_list_2 = sequence_list_read(i+1)
		print "length sequence 1: " + str(len(sequence_list_1))
		print "length sequence 2: " + str(len(sequence_list_2))
		correspond_list = {}
		for list_1_path_name in sequence_list_1:
			correspond_tmp_list = []
			list_1_path = sequence_list_1[list_1_path_name]
			for list_2_path_name in sequence_list_2:
				list_2_path = sequence_list_2[list_2_path_name]
				if list_2_path == list_1_path:
					correspond_tmp_list.append(list_2_path_name)
			correspond_list[list_1_path_name] = correspond_tmp_list

		for list_1_path_name in correspond_list:
			if not len(correspond_list[list_1_path_name]) == 1:
				print "error " + list_1_path_name
				print correspond_list[list_1_path_name]
#}}}
	
def  sub_path_insert_test():
#{{{
	status_matrix = status_matrix_read()	
	sequence_list = sequence_list_read(0)
	print len(sequence_list)
	for sub_path_name in sequence_list:
		if sub_path_name == "critical_path":
			continue
		sub_path = sequence_list[sub_path_name] 
		for candidate_block in status_matrix:
			if candidate_block in sub_path:
				continue
			if candidate_block == "message_38":
				continue
			insert_pos = search_sub_block_insert_into_growing_pattern_position (sub_path, candidate_block, status_matrix)
			if not insert_pos == -1:
				print "error " + sub_path_name + " " + candidate_block
#}}}


def special_test(folder_name):
	sub_path_list = sequence_list_read(0)
	prior_matrix = prior_matrix_read()
	status_matrix = status_matrix_read()
	print status_matrix["message_366"]
	print status_matrix["message_365"]
	
	
def sub_path_self_test():
	sub_path_list = sequence_list_read(0)
	total_path_list = {}
	for sub_path_name in sub_path_list:
		sub_path = sub_path_list[sub_path_name]
		unify_name_sub_path = sub_path_name_unify(sub_path)
		exist = 0
		for unified_sub_path_name in total_path_list:
			unified_name_sub_path = total_path_list[unified_sub_path_name]
			if unified_name_sub_path == unify_name_sub_path:
				print "error " + unified_sub_path_name + " " + sub_path_name
				exist = 1
		if exist == 0:
			total_path_list[sub_path_name] = unify_name_sub_path

def sub_path_self_chaos_test():
	sub_path_list = sequence_list_read(0)
	status_matrix = status_matrix_read()
	error_list = []
	for sub_path_name in sub_path_list:
		sub_path = sub_path_list[sub_path_name]
		for i in range(0, len(sub_path) - 1):
			this_element = sub_path[i]
			for j in range(i + 1, len(sub_path)):
				follow_element = sub_path[j]
				if follow_element in status_matrix[this_element]["after"]:
					if not sub_path_name in error_list: 
						error_list.append(sub_path_name)
					break
	for sub_path_name in error_list:
		print sub_path_name

def event_happen_time_count():
	prior_matrix = prior_matrix_read()
	total_happen_time = 0
	total_event_type_count = 0
	for event_name in prior_matrix:
		total_event_type_count += 1
		event_happen_time = prior_matrix[event_name]["happen_count"]
		print event_name
		print event_happen_time
		total_happen_time += event_happen_time
	print "total report"
	print total_event_type_count
	print total_happen_time

def test_file_event_count(folder_name):
	file_list = global_APIs.get_folder_file_list (folder_name)
	total_event_count = 0
	
	for block_report_file in file_list:
		print block_report_file
		fl = open(block_report_file, "r")
		node_block_lines = fl.readlines()
		print len(node_block_lines)
		total_event_count += 	len(node_block_lines)
	print total_event_count

def sequence_length_test():
	sub_path_list = sequence_list_read(0)
	longest_length = 0
	shortest_length = 999
	for sub_path_name in sub_path_list:
		sub_path = sub_path_list[sub_path_name]
		if len(sub_path) == 0:
			continue
		if len(sub_path) < shortest_length:
			shortest_length = len(sub_path)
		if len(sub_path) > longest_length:
			longest_length = len(sub_path)
	print longest_length
	print shortest_length


def sub_path_name_unify (sub_path):
	unified_name_sub_path = []
	block_pattern = r'block_([0-9]+)$'
	tmp_1_list = []
	for block in sub_path:
		matchobj = re.match (block_pattern, block)
		if matchobj:
			block_num = matchobj.group(1)
			tmp = [block, block_num]
			tmp_1_list.append(tmp)
	sorted_tmp_1_list = sorted( tmp_1_list, key=operator.itemgetter(1), reverse=False)
	for block in sorted_tmp_1_list:
		unified_name_sub_path.append(block[0])

	message_pattern = r'message_([0-9]+)$'
	tmp_1_list = []
	for message in sub_path:
		matchobj = re.match (message_pattern, message)
		if matchobj:
			message_num = matchobj.group(1)
			tmp = [message, message_num]
			tmp_1_list.append(tmp)
	sorted_tmp_1_list = sorted( tmp_1_list, key=operator.itemgetter(1), reverse=False)
	for message in sorted_tmp_1_list:
		unified_name_sub_path.append(message[0])
	return unified_name_sub_path

#database opt
#common_event_list_store
#common_event_list_read
#sequence_list_store
#sequence_list_read
#prior_matrix_store
#prior_matrix_read
#status_matrix_store
#status_matrix_read
#{{{
def common_event_list_store(common_event_list, file_name):
#{{{
	fl = open(file_name, "w")
	for event in common_event_list:
		fl.write(event + "\n")
	fl.close()
#}}}

def common_event_list_read(file_name):
#{{{	
	common_event_list = []
	fl = open(file_name, "r")
	for line in fl.readlines():
		line = line.replace("\n", "")
		common_event_list.append(line)
	fl.close()
	return common_event_list
#}}}

def sequence_list_store (sub_path_result, prefix = "", file_name = "sequence_tmp_report/sequence_report"):
#{{{
	if not prefix == "":
		file_name += "_" + str(prefix)
	file_name += ".txt"
	sequence_report_fl = open(file_name, "w")
	critical_path = sub_path_result["critical_path"]
	tmp = ""
	for block in critical_path:
		tmp += block + " "
	sequence_report_fl.write("critical_path" + "\n")
	sequence_report_fl.write(tmp + "\n")
	

	for i in range (0, len(sub_path_result) - 1):
		sub_path_name = "sub_path_" + str(i)
		sub_path = sub_path_result[sub_path_name]
		tmp = ""
		for block in sub_path:
			tmp += block + " "
		
		sequence_report_fl.write(sub_path_name + "\n")
		sequence_report_fl.write(tmp + "\n")
	sequence_report_fl.close()
#}}}
def sequence_list_read (prefix = "", file_name = "sequence_tmp_report/sequence_report"):
#{{{
	sub_path_list = {}	
	if not prefix == "":
		file_name += "_" + str(prefix)
	file_name += ".txt"
	sequence_report_fl = open(file_name, "r")
	sub_path_lines = sequence_report_fl.readlines()
	i = 0
	while i < len(sub_path_lines):
		sub_path_name = sub_path_lines[i].split()[0]
		
		sub_path_line = sub_path_lines[i+1]
		
		if sub_path_line == "":
			sub_path_list[sub_path_name] = []
			continue
		sub_path = sub_path_line.split()	
		sub_path_list[sub_path_name] = sub_path
		i += 2
	sequence_report_fl.close()
	return sub_path_list
#}}}
def prior_matrix_store (prior_matrix, file_name = "sequence_tmp_report/prior_matrix_"):
#{{{
	count = 0
	file_name += str(count)
	count += 1	
	file_name += ".txt"
	fl = open (file_name, "w")	
	for block in prior_matrix:
		fl.write("main_block " + block + " ")
		fl.write("\n")
		happen_time = prior_matrix[block]["happen_count"]
		tmp = "happen_count " + str(happen_time) + "\n"
		fl.write(tmp)
		tmp = ""
		for sub_block in prior_matrix[block]:
			if sub_block == "happen_count" or sub_block == "last_block":
				continue
			tmp += sub_block + " " + str(prior_matrix[block][sub_block]["count"]) + " " + str(prior_matrix[block][sub_block]["HC"]) + " "
		fl.write (tmp)
		fl.write("\n")
	fl.close()
#}}}
def prior_matrix_read (file_name = "sequence_tmp_report/prior_matrix_"):
#{{{
	count = 0
	file_name += str(count)
	count += 1	
	file_name += ".txt"
	fl = open (file_name, "r")
	lines = fl.readlines()
	prior_matrix = {}
	i = 0
	while i < len(lines):
		block_name_line = lines[i]
		happen_count_line = lines[i+1]
		sub_block_line = lines[i+2]

		block_name = block_name_line.split()[1]
		happen_count = int(happen_count_line.split()[1])
		block_sub_list = {}
		block_sub_list["happen_count"] = happen_count
		sub_block_list = sub_block_line.split()
		j = 0
		while j < len(sub_block_list):
			sub_block_name = sub_block_list[j]
			sub_block_count = int (sub_block_list[j+1])
			sub_block_happen_together_count = int (sub_block_list[j+2])

			sub_block_count_list = {}
			sub_block_count_list["count"] = sub_block_count
			sub_block_count_list["HC"] = sub_block_happen_together_count
			#this is not really necessary, just for using the same format with original prior matrix
			#because status matrix need to read the original format prior matrix
			block_sub_list[sub_block_name] = sub_block_count_list
			j += 3
		prior_matrix[block_name] = block_sub_list		
		i += 3 
	
	fl.close()
	return prior_matrix
#}}}
def status_matrix_store (total_status_matrix, file_name = "sequence_tmp_report/status_matrix.txt"):
#{{{ 
	fl = open (file_name, "w")	
	for block in total_status_matrix:
		fl.write("main_block " + block + " ")
		fl.write("\n")
		tmp = "prior "
		for sub_block in total_status_matrix[block]["prior"]:
			tmp += sub_block + " "
		fl.write (tmp + "\n")
		tmp = "after "
		for sub_block in total_status_matrix[block]["after"]:
			tmp += sub_block + " "
		fl.write (tmp + "\n")
		tmp = "wrap_out "
		for sub_block in total_status_matrix[block]["wrap_out"]:
			tmp += sub_block + " "
		fl.write (tmp + "\n")
		tmp = "wrap_in "
		for sub_block in total_status_matrix[block]["wrap_in"]:
			tmp += sub_block + " "
		fl.write (tmp + "\n")
		tmp = "tangle "
		for sub_block in total_status_matrix[block]["tangle"]:
			tmp += sub_block + " "
		fl.write (tmp + "\n")

	fl.close()
#}}}
def status_matrix_read (file_name = "sequence_tmp_report/status_matrix.txt"):
#{{{ 
	fl = open (file_name, "r")
	status_matrix = {}
	lines = fl.readlines()
	i = 0
	while i < len(lines):
		block_status_tmp_list = {}
		block_name_line = lines[i]
		prior_line = lines[i+1]	
		after_line = lines[i+2]	
		wrap_out_line = lines[i+3]	
		wrap_in_line = lines[i+4]	
		tangle_line = lines[i+5]	
		
		block_name = block_name_line.split()[1]
		
		prior_list = []
		j = 0
		for j in range (1, len(prior_line.split())):
			prior_list.append(prior_line.split()[j])
		block_status_tmp_list["prior"] = prior_list
		
		after_list = []
		j = 0
		for j in range (1, len(after_line.split())):
			after_list.append(after_line.split()[j])
		block_status_tmp_list["after"] = after_list
		
		wrap_out_list = []
		j = 0
		for j in range (1, len(wrap_out_line.split())):
			wrap_out_list.append(wrap_out_line.split()[j])
		block_status_tmp_list["wrap_out"] = wrap_out_list
		
		wrap_in_list = []
		j = 0
		for j in range (1, len(wrap_in_line.split())):
			wrap_in_list.append(wrap_in_line.split()[j])
		block_status_tmp_list["wrap_in"] = wrap_in_list
		
		tangle_list = []
		j = 0
		for j in range (1, len(tangle_line.split())):
			tangle_list.append(tangle_line.split()[j])
		block_status_tmp_list["tangle"] = tangle_list
		
		i += 6
		status_matrix[block_name] = block_status_tmp_list
	fl.close()
	return status_matrix 
#}}}
#}}}

#LSTM use
#sequence_list_common_block_summary
#	read_sequence_list_from_one_file
#	event_block_message_name_unconvert
#	TSM_on_sequence_list
#	all_sub_path_test_on_sequences(sequence_list, work_path_name)
#{{{
def sequence_list_common_block_summary (sequence_file_name):
#{{{
	#this is for LSTM sequence learning file detect TSM squence pattern
	sequence_list = read_sequence_list_from_one_file(sequence_file_name)

	event_summary_list = {}

	sequence_count = 0
	for sequence in sequence_list:
		for event in sequence:
			if event in event_summary_list:
				event_sequence_count_list = event_summary_list[event]
			else:
				event_sequence_count_list = []
			if not sequence_count in event_sequence_count_list:
				event_sequence_count_list.append(sequence_count)
			event_summary_list[event] = event_sequence_count_list

		sequence_count += 1

	common_event_list = []
	total_sequence_length = len(sequence_list)
	tolerate_ratio = 0.98
	support_length_num = int(total_sequence_length * tolerate_ratio)
	for event in event_summary_list:
		if len(event_summary_list[event]) >= support_length_num:
			common_event_list.append(event)
	return common_event_list
#}}}

def read_sequence_list_from_one_file (sequence_file_name):
#{{{
	sequence_list = []
	fl = open(sequence_file_name, "r")
	for line in fl.readlines():
		line = line.split()
		new_line = []
		for event in line:
			event_name = event_block_message_name_unconvert(event)
			new_line.append(event_name)
		sequence_list.append(new_line)
	fl.close()
	return sequence_list	
#}}}

def event_block_message_name_unconvert(event_num):
#{{{
	if int (event_num) < 3000:
		return "message_" + str(event_num)
	else:
		return "block_" + str(int(event_num) - 3000)
#}}}

def TSM_on_sequence_list(sequence_list, work_path_name):
#{{{
	care_event_list = common_event_list_read(work_path_name + "/common_event_list.txt")	

	result = multi_file_sequence_prior_matrix_gen(sequence_list, care_event_list)
	prior_matrix = result[0]
	prior_matrix_file_name = work_path_name + "/prior_matrix_"
	#file name will be changed to prior_matrix_0.txt in function
	prior_matrix_store(prior_matrix, prior_matrix_file_name)

	total_status_matrix = gen_status_matrix_based_on_prior_matrix (care_event_list, prior_matrix)
	status_matrix_file_name = work_path_name + "/status_matrix.txt"
	status_matrix_store(total_status_matrix, status_matrix_file_name)
	
	sub_path_list = find_sub_path(care_event_list, total_status_matrix, prior_matrix)
	sub_path_result = {}
	sub_path_result["critical_path"] = "" 
	sub_path_num = 0
	for sub_path in sub_path_list:
		sub_path_name = "sub_path_" + str(sub_path_num)
		sub_path_result[sub_path_name] = sub_path
		sub_path_num += 1
	
	sequence_pattern_file_name = work_path_name + "/sequence_report"
	sequence_list_store(sub_path_result , "", sequence_pattern_file_name)		
#}}}

def all_sub_path_test_on_sequences(sequence_list, work_path_name):
#{{{
	sequence_pattern_file_name = work_path_name + "/sequence_report"
	sub_path_list = sequence_list_read("", sequence_pattern_file_name)		
	total_block_report_list = {}
	for sub_path_name in sub_path_list:
		total_block_report_list[sub_path_name] = 0
	sequence_count = 0
	for sequence in sequence_list:
		if sequence_count %50 == 0:
			print "test sequence " + str(sequence_count)
		for sub_path_name in sub_path_list:
			sub_path = sub_path_list[sub_path_name]
			if sub_path == []:
				continue

			total_matched_sub_path = match_one_sub_path_with_one_sequence(sub_path ,sequence)
			error_count, not_fully_match_count, success_count = matched_sub_path_summary(sub_path, total_matched_sub_path)
			total_block_report_list[sub_path_name] += success_count +  not_fully_match_count
		sequence_count += 1

	for sub_path_name in 	total_block_report_list:
		print sub_path_name + " " + str(total_block_report_list[sub_path_name])


#}}}




def node_common_block_summary (folder_name):
#{{{
	file_list = global_APIs.get_folder_file_list (folder_name)
	file_list_length = len(file_list)
	block_happen_node_list = {}
	node_count = 0
	for block_report_file in file_list:
		fl = open(block_report_file, "r")
		node_block_lines = fl.readlines()
		for line in node_block_lines:
			block_name = line.split()[0]
			if not block_name in block_happen_node_list:
				block_node_list = []
				block_node_list.append(node_count)
				block_happen_node_list[block_name] = block_node_list
			else:
				block_node_list = block_happen_node_list[block_name]
				if not node_count in block_node_list:
					block_node_list.append(node_count)
					block_happen_node_list[block_name] = block_node_list
		node_count += 1
		fl.close()
	common_list = []
	for node_name in block_happen_node_list:
		if len(block_happen_node_list[node_name]) == file_list_length:
			common_list.append(node_name)
	print len(common_list)
	fl = open("sequence_tmp_report/analyze_block_node.txt", "w")
	fl.write("\n")
	tmp = ""
	for block_name in common_list:
		tmp += block_name
		tmp += " "
	fl.write(tmp)
	fl.write("\n")
	fl.close()
#}}}

def block_report_file_merge (folder_name = "block_report"):
#{{{
	fl = open("analyze_block_node.txt", "r")
	node_line = fl.readline()
	node_list = node_line.split()
	fl.close()
	if not os.path.isdir("merged_files"):
		os.mkdir("merged_files")	
	
	analyze_lower_band = 0
	analyze_upper_band = 3 
	sub_folder_list = global_APIs.get_folder_file_list (folder_name)
	folder_num = -1
	for sub_folder in sub_folder_list:
		sub_folder_file_list = global_APIs.get_folder_file_list (sub_folder)
		print sub_folder
		folder_num += 1
		if folder_num < analyze_lower_band:
			continue
		if folder_num >= analyze_upper_band:
			break
		sub_folder_file_list = global_APIs.get_folder_file_list (sub_folder)
		node_file_list = one_sub_daily_folder_report_node_block_summary (sub_folder)
		for node_name in node_file_list:
			if not node_name in node_list:
				continue
			file_out = folder_name + "/" + str(folder_num) + "/" + str(folder_num) + "_" + node_name + ".txt_block_report.txt"
			#block_report/0/0_c0-0c0s8n3.txt_block_report.txt
			file_in = "merged_files" + "/" + node_name + "_" + str(analyze_lower_band) + "_" + str(analyze_upper_band) + "_block_report.txt"
			#merged_files/0_c0-0c0s8n3_0_5_block_report.txt
			print file_out
			print file_in
			out_fl = open(file_out, "r")
			in_fl = open(file_in, "a")
			for line in out_fl.readlines():
				in_fl.write(line)
			out_fl.close()
			in_fl.close()
#}}}

def block_happen_node_summary (folder_name = "block_report"):
#{{{
	analyze_lower_band = 0
	analyze_upper_band = 1
	sub_folder_list = global_APIs.get_folder_file_list (folder_name)
	total_node_block_list = {}
	total_block_node_list = {}	
	folder_num = -1
	for sub_folder in sub_folder_list:
		folder_num += 1
		if folder_num < analyze_lower_band:
			continue
		if folder_num >= analyze_upper_band:
			break

		if sub_folder == "block_report/node_stack.txt":
			continue
		sub_folder_file_list = global_APIs.get_folder_file_list (sub_folder)
		node_file_list = one_sub_daily_folder_report_node_block_summary (sub_folder)
		for node_name in node_file_list:
			if not node_name in total_node_block_list:
				total_node_block_list[node_name] = []
			block_report_file = node_file_list[node_name]["block"]
			fl = open(block_report_file, "r")
			for line in fl.readlines():
				line = line.split()
				block_name = line[0]
				if not block_name in total_block_node_list:
					total_block_node_list[block_name] = []
				if not block_name in total_node_block_list[node_name]:
					total_node_block_list[node_name].append(block_name)
				if not node_name in total_block_node_list[block_name]:
					total_block_node_list[block_name].append(node_name)
		break
	block_cover_node_num_list = {}	
	for block_name in total_block_node_list:
		#print block_name
		#print len(total_block_node_list[block_name])
		block_cover_node_num_list[block_name] = len(total_block_node_list[block_name])
	care_threshold = 18
	care_block_list = []
	care_node_list = []
	for block_name in total_block_node_list:
		if len(total_block_node_list[block_name]) == 18 :
			for node in total_block_node_list[block_name]:
				if not node in care_node_list:
					care_node_list.append(node)
		if len(total_block_node_list[block_name]) >= care_threshold:
			if not block_name in care_block_list:
				care_block_list.append(block_name)
	fl = open("sequence_tmp_report/analyze_block_node.txt", "w")
	tmp = ""
	for node_name in care_node_list:
		tmp += node_name
		tmp += " "
	fl.write(tmp)
	fl.write("\n")
	tmp = ""
	for block_name in care_block_list:
		add = 0 
		for node_name in total_block_node_list[block_name]:
			if node_name in care_node_list:
				add = 1
				break
		if add == 1:
			tmp += block_name
			tmp += " "
	fl.write(tmp)
	fl.write("\n")
	tmp = ""
	for block_name in care_block_list:
		tmp += block_name
		tmp += " "
	fl.write(tmp)
	fl.close()
	fl = open("sequence_tmp_report/block_belong_node.txt", "w")
	for block in total_block_node_list:
		fl.write("main_block " + block + "\n")
		tmp = ""
		for node in total_block_node_list[block]:
			tmp += node + " "
		fl.write(tmp + "\n")
	fl.close()
#}}}

def one_sub_daily_folder_report_node_block_summary (sub_folder):
#{{{
	node_file_list = {}
	sub_folder_file_list = global_APIs.get_folder_file_list (sub_folder)
	for sub_folder_file in sub_folder_file_list:
		sub_folder_file_real_name = global_APIs.get_real_file_name(sub_folder_file)
		single_line_file_name_pattern = r'([0-9]+)\_(.*)\.txt\_single\_line\_report\.txt$'
		block_file_name_pattern = r'([0-9]+)\_(.*)\.txt\_block\_report\.txt$'
		#block_report/0/0_c0-0c0s9n1.txt_single_line_report.txt
		#block_report/0/0_c0-0c0s9n1.txt_block_report.txt
		matchobj = re.match (single_line_file_name_pattern, sub_folder_file_real_name)
		if matchobj:
			node_name = matchobj.group(2)
			if node_name in node_file_list:
				tmp = node_file_list[node_name]
			else:
				tmp = {}
			tmp["single"] = sub_folder_file
			node_file_list[node_name] = tmp
		matchobj = re.match (block_file_name_pattern, sub_folder_file_real_name)
		if matchobj:
			node_name = matchobj.group(2)
			if node_name in node_file_list:
				tmp = node_file_list[node_name]
			else:
				tmp = {}
			tmp["block"] = sub_folder_file
			node_file_list[node_name] = tmp
	return node_file_list
#}}}

