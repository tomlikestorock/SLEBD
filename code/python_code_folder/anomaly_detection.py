#!/usr/bin/python
#coding:utf-8
import os
import sys
import re 
import shutil
import global_APIs
import block_learning
import database_opt
import multi_file_folder
import time
consider_merge_threshold = 2
use_dynamic_threshold = 1

def this_happen_matrix_anomaly_detection (previous_happen_matrix, this_happen_matrix, need_update_single_line_pattern_list, single_line_pattern_db, message_closest_message_list):
#{{{
	previous_result = block_learning.gen_forward_backward_pos_matrix_on_happen_matrix (previous_happen_matrix)
	previous_matrix_forward_matrix = previous_result[0]
	previous_matrix_backward_matrix = previous_result[1]
	this_result = block_learning.gen_forward_backward_pos_matrix_on_happen_matrix (this_happen_matrix)
	this_matrix_forward_matrix = this_result[0]
	this_matrix_backward_matrix = this_result[1]

	invalid_message = ""
	for message in this_happen_matrix:
		if single_line_pattern_db[message]["pattern"] == [['0', 'invalid_line']]:
			invalid_message = message
		if not message in previous_happen_matrix:
			continue
		if previous_happen_matrix[message]["happen_time"] < consider_merge_threshold and this_happen_matrix[message]["happen_time"] >= consider_merge_threshold:
			need_update_single_line_pattern_list.append(message)

	for message in this_matrix_forward_matrix:
		#forward test
		#{{{
		if this_happen_matrix[message]["happen_time"] <= 1:
			continue
		if message == invalid_message:
			continue
		if message in need_update_single_line_pattern_list:
			continue
		this_message_list = this_matrix_forward_matrix[message]
		previous_message_list = []
		if message in previous_matrix_forward_matrix:
			previous_message_list = previous_matrix_forward_matrix[message]
		else:
			#this is a new message, previous matrix don't have this message
			if not message in need_update_single_line_pattern_list:
				need_update_single_line_pattern_list.append(message)
			continue

		if use_dynamic_threshold == 1:
			start_message_dynamic_threshold_info = global_APIs.dynamic_threshold_list[message]
			similar_threshold = start_message_dynamic_threshold_info[0]
			start_message_confidence_interval = start_message_dynamic_threshold_info[1]
		else:
			similar_threshold = block_learning.global_similar_threshold
		tolerate_ratio_range = 1 - similar_threshold

		should_add_update_list = 0 
		#compare this message list and previous message list
		for this_sub_message in this_message_list:
			if this_sub_message == invalid_message:
				continue
			this_sub_message_ratio = this_message_list[this_sub_message]
			if this_sub_message in previous_message_list:
				previous_sub_message_ratio = previous_message_list[this_sub_message]
			else:
				previous_sub_message_ratio = 0

			if previous_sub_message_ratio >= similar_threshold and this_sub_message_ratio < similar_threshold:
				should_add_update_list = 1
				break
			elif previous_sub_message_ratio < similar_threshold and this_sub_message_ratio >= similar_threshold:
				should_add_update_list = 1
				break

			tolerate_upper_range = previous_sub_message_ratio * (1.0 + tolerate_ratio_range)
			tolerate_lower_range = previous_sub_message_ratio * (1.0 - tolerate_ratio_range)
			#ARES
			if this_sub_message_ratio > tolerate_upper_range or this_sub_message_ratio < tolerate_lower_range:
				#exceed tolerate range
				should_add_update_list = 1
				break

		if should_add_update_list == 1:
			need_update_single_line_pattern_list.append(message)
		#}}}
	for message in this_matrix_backward_matrix:
		#backward test
		#{{{
		if message == invalid_message:
			continue
		this_message_list = this_matrix_backward_matrix[message]
		previous_message_list = []
		if message in previous_matrix_backward_matrix:
			previous_message_list = previous_matrix_backward_matrix[message]

		should_add_update_list = 0 
		#compare this message list and previous message list
		for this_sub_message in this_message_list:
			if this_happen_matrix[this_sub_message]["happen_time"] <= 1:
				continue
			if this_sub_message == invalid_message:
				continue
			if this_sub_message in need_update_single_line_pattern_list:
				continue

			if use_dynamic_threshold == 1:
				start_message_dynamic_threshold_info = global_APIs.dynamic_threshold_list[this_sub_message]
				similar_threshold = start_message_dynamic_threshold_info[0]
				start_message_confidence_interval = start_message_dynamic_threshold_info[1]
			else:
				similar_threshold = block_learning.global_similar_threshold
			tolerate_ratio_range = 1 - similar_threshold

			this_sub_message_ratio = this_message_list[this_sub_message]
			if this_sub_message in previous_message_list:
				previous_sub_message_ratio = previous_message_list[this_sub_message]
			else:
				previous_sub_message_ratio = 0
				#this is a new found message, or never happened to this message
				#ratio = 0, upper_range = 0 too
				#this ratio should higher than upper_range
					
			if previous_sub_message_ratio >= similar_threshold and this_sub_message_ratio < similar_threshold:
				should_add_update_list = 1
			elif previous_sub_message_ratio < similar_threshold and this_sub_message_ratio >= similar_threshold:
				should_add_update_list = 1
			tolerate_upper_range = previous_sub_message_ratio * (1.0 + tolerate_ratio_range)
			tolerate_lower_range = previous_sub_message_ratio * (1.0 - tolerate_ratio_range)
			if this_sub_message_ratio > tolerate_upper_range or this_sub_message_ratio < tolerate_lower_range:
				#exceed tolerate range
				should_add_update_list = 1
		
			if should_add_update_list == 1:
				need_update_single_line_pattern_list.append(this_sub_message)
		#}}}
	for message in message_closest_message_list:
		if this_happen_matrix[message]["happen_time"] <= 1:
			continue
		if message == invalid_message:
			continue
		if message in need_update_single_line_pattern_list:
			continue
		start_message_happen_time = this_happen_matrix[message]["happen_time"]
		if use_dynamic_threshold == 1:
			start_message_dynamic_threshold_info = global_APIs.dynamic_threshold_list[message]
			similar_threshold = start_message_dynamic_threshold_info[0]
			start_message_confidence_interval = start_message_dynamic_threshold_info[1]
			follow_message_happen_time_upper_range = start_message_happen_time + start_message_confidence_interval
			follow_message_happen_time_lower_range = start_message_happen_time - start_message_confidence_interval
		else:
			similar_threshold = block_learning.global_similar_threshold
			follow_message_happen_time_upper_range = int(start_message_happen_time * (2.0 - similar_threshold))
			follow_message_happen_time_lower_range = int(start_message_happen_time * similar_threshold)
		need_add_update_list = 0
		prior_list = message_closest_message_list[message]["prior"]
		for prior_message in prior_list:
			prior_message_happen_time = this_happen_matrix[prior_message]["happen_time"]
			if prior_message_happen_time > follow_message_happen_time_upper_range or prior_message_happen_time < follow_message_happen_time_lower_range:
				need_add_update_list = 1 
				break
		if need_add_update_list == 1:
			need_update_single_line_pattern_list.append(message)
			continue
		
		follow_list = message_closest_message_list[message]["follow"]
		for follow_message in follow_list:
			follow_message_happen_time = this_happen_matrix[follow_message]["happen_time"]
			if follow_message_happen_time > follow_message_happen_time_upper_range or follow_message_happen_time < follow_message_happen_time_lower_range:
				need_add_update_list = 1
				break
		if need_add_update_list == 1:
			need_update_single_line_pattern_list.append(message)
			continue


	
	new_need_update_single_line_pattern_list = []
	for message in need_update_single_line_pattern_list:
		if this_happen_matrix[message]["happen_time"] >= consider_merge_threshold:
			new_need_update_single_line_pattern_list.append(message)

	return new_need_update_single_line_pattern_list
#}}}	

def affected_message_pattern_history_analyze(folder_name):
	#this is testing cutoff
	sub_folder_list = global_APIs.get_folder_file_list (folder_name)
	folder_num = -1 
	prefix = -1
	last_prefix = -1
	each_message_record_dict = {}
	cutoff_message_list = []
	each_interval_record = {}
	cut_off_happen_time_threshold = 100
	cut_off_folder_num_threshold = 10

	daily_num = 2
	interval_num = 0
	interval_control_num = 10 
	total_day_num = 0
	
	this_interval_need_update_list = []
	this_interval_affected_list = []
	this_interval_new_found_num = 0
	this_interval_new_found_update_num = 0

	for sub_folder in sub_folder_list:
		folder_num += 1
		prefix = folder_num
		file_mode = global_APIs.get_file_mode(sub_folder)
		if file_mode == "":
			continue
		if folder_num < multi_file_folder.folder_control_lower_band:
			last_prefix = folder_num
			continue
		if folder_num >= multi_file_folder.folder_control_upper_band:
			break
		
		affect_record = database_opt.read_this_round_affect_message_list(sub_folder, prefix)
		new_found_single_line_pattern = affect_record[0]
		need_update_single_line_pattern_list = affect_record[1]
		left_new_found_single_line_pattern_list = affect_record[2]
		affected_message_list = affect_record[3]

		for need_update_pattern in need_update_single_line_pattern_list:
			if not need_update_pattern in this_interval_need_update_list:
				this_interval_need_update_list.append(need_update_pattern)
		for affected_message in affected_message_list:
			if not affected_message in this_interval_affected_list:
				this_interval_affected_list.append(affected_message)
		this_interval_new_found_num += len(new_found_single_line_pattern)
		this_interval_new_found_update_num += len(new_found_single_line_pattern) - len(left_new_found_single_line_pattern_list)

	
		total_day_num = (folder_num + 1)* daily_num
		if total_day_num % interval_control_num == 0:
			tmp = []
			tmp.append(this_interval_new_found_num)	
			tmp.append(this_interval_new_found_update_num)	
			tmp.append(len(this_interval_need_update_list))	
			tmp.append(len(this_interval_affected_list))
			print total_day_num 
			print tmp
			each_interval_record[interval_num] = tmp
			this_interval_need_update_list = []
			this_interval_affected_list = []
			this_interval_new_found_num = 0
			this_interval_new_found_update_num = 0
			interval_num += 1
		continue
	



		for message in new_found_single_line_pattern:
			tmp = {}
			tmp["first_seen"] = folder_num
			tmp["last_need_update"] = -1
			tmp["last_change"] = -1 
			each_message_record_dict[message] = tmp
		for message in need_update_single_line_pattern_list:
			each_message_record_dict[message]["last_need_update"] = folder_num
		for message in affected_message_list:
			previous_block_pattern_list =  database_opt.read_block_pattern_list(sub_folder, last_prefix)
			previous_single_line_pattern_db = database_opt.read_single_line_pattern_db(sub_folder, last_prefix)
			this_block_pattern_list =  database_opt.read_block_pattern_list(sub_folder, prefix)
			this_single_line_pattern_db = database_opt.read_single_line_pattern_db(sub_folder, prefix)
			if not message in previous_single_line_pattern_db or previous_single_line_pattern_db[message]["belong_block"] == "":
				each_message_record_dict[message]["last_change"] = folder_num
				continue
			previous_belong_block = previous_single_line_pattern_db[message]["belong_block"]
			previous_belong_block_pattern = previous_block_pattern_list[previous_belong_block]
			this_belong_block = this_single_line_pattern_db[message]["belong_block"]
			if this_belong_block == "":
				#previous belong to a block, now disconnected
				if message in cutoff_message_list:
					print "cutoff message update " + message + " " + str(each_message_record_dict[message]["last_change"]) + " " + str(folder_num)

				each_message_record_dict[message]["last_change"] = folder_num
				continue
			this_belong_block_pattern = this_block_pattern_list[this_belong_block]
			#now this message have a belong block
			same_result = judge_two_block_pattern_list_same(previous_belong_block_pattern, this_belong_block_pattern)	
			if same_result == 0:
				if message in cutoff_message_list:
					print "cutoff message update " + message + " " + str(each_message_record_dict[message]["last_change"]) + " " + str(folder_num)
				each_message_record_dict[message]["last_change"] = folder_num
				continue
				
				 



		#here make cut off decision
		this_happen_matrix = database_opt.read_happen_matrix(sub_folder, prefix, "total")
			#happen_matrix is for count each message's happen time
		for message in each_message_record_dict:
			if message in cutoff_message_list:
				continue
			message_happen_time = this_happen_matrix[message]["happen_time"]
			if message_happen_time < cut_off_happen_time_threshold:
				continue	
			last_change_folder_num = each_message_record_dict[message]["last_change"]
			if last_change_folder_num == -1:
				#continue
				#this means this message never merged or dismerged with any other messages
				first_seen_folder_num = each_message_record_dict[message]["first_seen"]
				if folder_num - first_seen_folder_num > cut_off_folder_num_threshold:
					cutoff_message_list.append(message)
			else:
				interval_to_last_change = folder_num - last_change_folder_num
				if interval_to_last_change >= cut_off_folder_num_threshold:	
					cutoff_message_list.append(message)
		#final test
		#for message in cutoff_message_list:
		#	last_change_folder_num = each_message_record_dict[message]["last_change"]
		#	interval_to_last_change = folder_num - last_change_folder_num
		#	if interval_to_last_change < cut_off_folder_num_threshold:	
		#		print "error "	+ message + " " + str(folder_num)

		last_prefix = folder_num

	#print "cutoff list"
	#print 	len(cutoff_message_list)

def judge_two_block_pattern_list_same (previous_belong_block_pattern, this_belong_block_pattern):
	if not len(this_belong_block_pattern) == len(previous_belong_block_pattern):
		#length is not same
		return 0
	for this_belong_block_message in this_belong_block_pattern:
		if not this_belong_block_message in previous_belong_block_pattern:
			return 0	

	return 1

def happen_time_analyze ():
	sub_folder = "../log_file/2_days/0"
	happen_matrix = database_opt.read_happen_matrix(sub_folder, 149, "total")
	single_line_pattern_db = database_opt.read_single_line_pattern_db(sub_folder, 149)
	one_time_message_count = 0 
	one_time_message_block_count = 0 
	
	for message in happen_matrix :
		happen_time = happen_matrix[message]["happen_time"]
		if happen_time <= 1:
			one_time_message_count += 1
			if not single_line_pattern_db[message]["belong_block"] == "":
				one_time_message_block_count += 1
	print one_time_message_count
	print one_time_message_block_count
