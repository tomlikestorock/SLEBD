#!/usr/bin/python
#coding:utf-8
import os
import sys
import re 
import shutil
import operator 
import global_APIs
import database_opt 

global_search_deep_level = 4 
global_message_range_forward_step_num = 6
global_similar_threshold = 0.98
global_most_possible_message_threshold = 0.51
analyze_range_message_count_threshold = 20
use_dynamic_threshold = 1 

def generate_happen_matrix_from_message_list (input_file, happen_matrix = {}, single_line_pattern_db = {}, new_add_single_line_pattern_list = [], single_line_pattern_range_line_pattern_list = {},  node_id_last_list = {}, ignore_previous_file = 1):
#{{{
	fl = open (input_file, "r")
	first_message = fl.readline()
	fl.close()	
	node_id = global_APIs.get_line_id(first_message)

	previous_file_last_line_name = ""
	if ignore_previous_file == 0 and node_id in node_id_last_list:
		previous_file_last_line_name = node_id_last_list[node_id]

	#this previous_pattern is for last node_id file 

	
	file_single_line_report = database_opt.read_file_single_line_list(input_file)
	if file_single_line_report == []:
		result = input_file_single_line_pattern_grow(input_file, single_line_pattern_db)
		file_single_line_report = result[0]
		database_opt.output_file_single_line_list(file_single_line_report, input_file)
		single_line_pattern_db = result[1]
		new_add_single_line_pattern_tmp_list = result[2]
	else:
		result = input_file_exist_single_line_report_file_compare_single_line_db(input_file, file_single_line_report, single_line_pattern_db)
		single_line_pattern_db = result[0]
		new_add_single_line_pattern_tmp_list = result[1]

	for pattern in new_add_single_line_pattern_tmp_list:
		new_add_single_line_pattern_list.append(pattern)

	
	if not previous_file_last_line_name == "":
		#treat last node file last line as the first line
		tmp = []
		tmp.append(previous_file_last_line_name)
		tmp.append(0)
		file_single_line_report = [tmp] + file_single_line_report
	

	length = len(file_single_line_report)
	last_line = []
	if not length == 0:
		last_line = file_single_line_report[0]

	if length == 1:
		last_line_name = last_line[0]
		if last_line_name in happen_matrix:
			tmp = happen_matrix[last_line_name]
			tmp["happen_time"] += 1
		else:
			tmp = {}
			tmp["happen_time"] = 1
		happen_matrix[last_line_name] = tmp

	range_fifo = []

	for i in range (1, length):
		this_line = file_single_line_report[i]
		
		last_line_name = last_line[0]	
		this_line_name = this_line[0]	

		if this_line_name == last_line_name:
			#ignore repeating lines and do not add matrix
			continue

		#now can update happen_matrix
		happen_matrix = update_happen_matrix (happen_matrix, last_line_name, this_line_name)

		#single_line_pattern_range_line_pattern_list
		#{{{
		result = range_fifo_update_to_gen_range_pattern_list(last_line_name, range_fifo, single_line_pattern_range_line_pattern_list)
		range_fifo = result[0]
		single_line_pattern_range_line_pattern_list = result[1]
		last_line = this_line
		#}}}


###########################################
	#last_line
	#{{{
	if not last_line == []:
		last_line_name = last_line[0]
		update_happen_matrix (happen_matrix, last_line_name, "last")
		node_id_last_list[node_id] = last_line_name
	#}}}
	
	tmp = []
	tmp.append(happen_matrix)
	tmp.append(single_line_pattern_db)
	tmp.append(new_add_single_line_pattern_list)
	tmp.append(single_line_pattern_range_line_pattern_list)
	tmp.append(node_id_last_list)
	return tmp 
#}}}

def range_fifo_update_to_gen_range_pattern_list(this_line_correspond_pattern_name ,range_fifo, single_line_pattern_range_line_pattern_list):
#{{{
	length = len(range_fifo)
	i = 0
	while i < length:
		previous_line_name = range_fifo[i]
		if previous_line_name == this_line_correspond_pattern_name:
			#do not add this_name to this previous_name's previous_list because same pattern can't have pair
			#re-add this_name to the rear of fifo, at the end 
			del(range_fifo[i])
			length = len(range_fifo)
			continue

		if previous_line_name in single_line_pattern_range_line_pattern_list:
			previous_line_range_list = single_line_pattern_range_line_pattern_list[previous_line_name]
		else:
			previous_line_range_list = {}

		#ARES
		if this_line_correspond_pattern_name in previous_line_range_list:
			previous_line_range_list[this_line_correspond_pattern_name] += 1
		else:
			previous_line_range_list[this_line_correspond_pattern_name] = 1
		#ARES end

		single_line_pattern_range_line_pattern_list[previous_line_name] = previous_line_range_list
		i += 1

	if len(range_fifo) < global_message_range_forward_step_num:
		range_fifo.append(this_line_correspond_pattern_name)
	else:
		del(range_fifo[0])
		range_fifo.append(this_line_correspond_pattern_name)
	tmp = []
	tmp.append(range_fifo)
	tmp.append(single_line_pattern_range_line_pattern_list)
	return tmp
#}}}

def update_happen_matrix (happen_matrix, this_line_correspond_pattern_name, next_line_correspond_pattern_name):
#{{{
	#last file's last line is already recorded
	if this_line_correspond_pattern_name in happen_matrix:
		this_list = happen_matrix[this_line_correspond_pattern_name]
		this_list["happen_time"] += 1
	else:
		this_list = {}
		this_list["happen_time"] = 1
	
	if next_line_correspond_pattern_name in this_list: 
		this_list[next_line_correspond_pattern_name] += 1
	else:
		this_list[next_line_correspond_pattern_name] = 1
	happen_matrix[this_line_correspond_pattern_name] = this_list
	return happen_matrix
#}}}

def search_pattern_db_for_correspond_or_add_in_pattern_db(this_line, single_line_pattern_db, new_add_single_line_pattern_list):
#{{{
	if not global_APIs.is_baler_mutrino_format(this_line):
		line_message = global_APIs.get_line_message(this_line)
		this_line_pattern = global_APIs.gen_line_pattern(line_message)
	else:
		line_message = global_APIs.get_line_message(this_line)
		this_line_pattern = global_APIs.gen_line_pattern(line_message)
		#this_line_pattern = global_APIs.gen_baler_line_pattern (this_line)
	
	if this_line_pattern == []:
		tmp = ["0", "invalid_line"]
		this_line_pattern.append(tmp) 
	
	correspond_pattern_name_list = global_APIs.search_correspond_pattern_from_single_line_pattern_db (this_line_pattern, single_line_pattern_db)
	this_line_correspond_pattern_name = ""
	if len(correspond_pattern_name_list) == 0:
		new_add_pattern_number = get_lowest_single_line_pattern_list_num(single_line_pattern_db)
		this_line_correspond_pattern_name = "message_" + str(new_add_pattern_number)
		new_add_single_line_pattern_list.append(this_line_correspond_pattern_name)
		tmp = {}
		tmp["pattern"] = this_line_pattern
		tmp["belong_block"] = ""
		single_line_pattern_db[this_line_correspond_pattern_name] = tmp
	else:
		this_line_correspond_pattern_name = correspond_pattern_name_list[0]

	tmp = []
	tmp.append(this_line_correspond_pattern_name)
	tmp.append(single_line_pattern_db)	
	tmp.append(new_add_single_line_pattern_list)	
	return tmp	
#}}}

def gen_forward_backward_pos_matrix_on_happen_matrix (happen_matrix):
#{{{
	forward_matrix = {}	
	backward_matrix = {}	
	for this_pattern in happen_matrix:
		this_list = happen_matrix[this_pattern]
		for next_pattern in this_list:
			if next_pattern == "happen_time":
				continue
	 		forward_pos = float(this_list[next_pattern])/float(this_list["happen_time"])
			if this_pattern in forward_matrix:
				this_forward_pos_list = forward_matrix[this_pattern]
			else:
				this_forward_pos_list = {}
			this_forward_pos_list[next_pattern] = forward_pos
			forward_matrix[this_pattern] = this_forward_pos_list
			
			if next_pattern == "last":
				#don't move this line! last only calculate forward pos but ignore backward!
				continue
			backward_pos = float(this_list[next_pattern])/float(happen_matrix[next_pattern]["happen_time"])

			if next_pattern in backward_matrix:
				next_backward_pos_list = backward_matrix[next_pattern]
			else:
				next_backward_pos_list = {}
			next_backward_pos_list[this_pattern] = backward_pos
			backward_matrix[next_pattern] = next_backward_pos_list

	tmp = []
	tmp.append(forward_matrix)
	tmp.append(backward_matrix)
	return tmp
#}}}

#other API:
#get_lowest_single_line_pattern_list_num
#{{{
def get_lowest_single_line_pattern_list_num (single_line_pattern_db):
	count = 0
	tmp = "message_"
	tmp += str(count)
	while tmp in single_line_pattern_db:
		count = count + 1
		tmp = "message_"
		tmp += str(count)
	return count 	

def get_lowest_block_name_list_num (block_list):
	count = 0
	tmp = "block_"
	tmp += str(count)
	while tmp in block_list:
		count = count + 1
		tmp = "block_"
		tmp += str(count)
	return count 	

#}}}

def find_closest_message_pair_mode_1 (need_update_single_line_pattern_list, happen_matrix, single_line_pattern_range_line_pattern_list):
	total_closest_message_pair_dict = {} 
	
	result = gen_forward_backward_pos_matrix_on_happen_matrix (happen_matrix)
	forward_matrix = result[0]
	backward_matrix = result[1]
	#find closest follow pair dict
	#{{{
	count = 0
	for start_message in need_update_single_line_pattern_list:
		closest_follow_message_list = []
		total_closest_message_pair_dict[start_message] = closest_follow_message_list
		count += 1
		if count % 40 == 0:
			print "merge " + str(count)
		if not start_message in single_line_pattern_range_line_pattern_list or  start_message == global_APIs.invalid_message:
			continue
			#right now, the last message in one file and only happen one time will only have one range pattern: "last"
			#it will not add into range line pattern list
		#ARES
		start_message_follow_message_list = forward_matrix[start_message]
		most_possible_follow_rate = 0.0
		most_possible_follow_message = ""
		for follow_message in start_message_follow_message_list:
			if follow_message == "last" or follow_message == global_APIs.invalid_message:
				continue
			if start_message_follow_message_list[follow_message] > most_possible_follow_rate:
				most_possible_follow_rate = start_message_follow_message_list[follow_message]
				most_possible_follow_message = follow_message
		if most_possible_follow_rate < global_similar_threshold:
			continue

		follow_message_prior_message_list = backward_matrix[most_possible_follow_message]
		most_possible_prior_rate = 0.0
		most_possible_prior_message = ""
		for prior_message in follow_message_prior_message_list:
			if follow_message_prior_message_list[prior_message] > most_possible_prior_rate:
				most_possible_prior_rate = follow_message_prior_message_list[prior_message]
				most_possible_prior_message = prior_message
		if most_possible_prior_rate < global_similar_threshold or not most_possible_prior_message == start_message:
			continue

		closest_follow_message_list.append(most_possible_follow_message)
		total_closest_message_pair_dict[start_message] = closest_follow_message_list
	#}}}
	return total_closest_message_pair_dict

def find_closest_message_pair_mode_2 (need_update_single_line_pattern_list, happen_matrix, single_line_pattern_range_line_pattern_list, merge_round_num):
	total_closest_message_pair_dict = {} 
	
	result = gen_forward_backward_pos_matrix_on_happen_matrix (happen_matrix)
	forward_matrix = result[0]
	backward_matrix = result[1]
	#find closest follow pair dict
	#{{{
	count = 0

	for start_message in need_update_single_line_pattern_list:
		count += 1
		if count % 40 == 0:
			print "merge " + str(count)
		if not start_message in single_line_pattern_range_line_pattern_list or  start_message == global_APIs.invalid_message:
			continue
			#right now, the last message in one file and only happen one time will only have one range pattern: "last"
			#it will not add into range line pattern list
		start_message_range_message_list = single_line_pattern_range_line_pattern_list[start_message]

		range_message_priority_list = []
		sorted_start_message_range_message_list = {}
		sorted_start_message_range_message_list = sorted(start_message_range_message_list.items(), key = operator.itemgetter(1), reverse = True)
		for finish_message in sorted_start_message_range_message_list:
			range_message_priority_list.append(finish_message[0])
		
		
		analyzed_range_count = 0
		if merge_round_num == 1:
			closest_follow_message_list = []
		else:
			if start_message in not_in_need_update_list_left_message_list:
				closest_follow_message_list = []
				analyzed_range_count = 0 
			else:	
				closest_follow_message_list = message_closest_message_list[start_message]["follow"]
				analyzed_range_count =  (merge_round_num - 1) * analyze_range_message_count_threshold

		#this start message's closest follow message list
		analyze_range_upper_limit = merge_round_num * analyze_range_message_count_threshold
		for finish_message in range_message_priority_list:
			if finish_message == global_APIs.invalid_message:
				continue
			analyzed_range_count += 1
			if analyzed_range_count >= analyze_range_upper_limit:
				#one round only care 10 messages in range list
				break

			if finish_message in closest_follow_message_list:
				continue
			forward_pos = calculate_possibility (start_message, finish_message, forward_matrix, 0, start_message, [])
			if forward_pos < global_similar_threshold:
				#forward_pos is less than threshold, do not waste time to calculate backward_pos
				continue
			backward_pos = calculate_possibility (finish_message, start_message, backward_matrix, 0, finish_message, [])
			if backward_pos >= global_similar_threshold:
				closest_follow_message_list.append(finish_message)
		total_closest_message_pair_dict[start_message] = closest_follow_message_list
	#}}}

	return total_closest_message_pair_dict

def find_closest_message_pair_mode_3 (need_update_single_line_pattern_list, happen_matrix, single_line_pattern_range_line_pattern_list):
	total_closest_message_pair_dict = {} 
	
	result = gen_forward_backward_pos_matrix_on_happen_matrix (happen_matrix)
	forward_matrix = result[0]
	backward_matrix = result[1]
	#find closest follow pair dict
	#{{{
	count = 0
	for start_message in need_update_single_line_pattern_list:
		count += 1
		if count % 40 == 0:
			print "merge " + str(count)
		if not start_message in single_line_pattern_range_line_pattern_list or  start_message == global_APIs.invalid_message:
			continue
			#right now, the last message in one file and only happen one time will only have one range pattern: "last"
			#it will not add into range line pattern list
		start_message_range_message_list = single_line_pattern_range_line_pattern_list[start_message]

		sorted_start_message_range_message_list = {}
		sorted_start_message_range_message_list = sorted(start_message_range_message_list.items(), key = operator.itemgetter(1), reverse = True)
		#this start message's closest follow message list
		closest_follow_message_list = []
		start_message_happen_time = happen_matrix[start_message]["happen_time"]
		if use_dynamic_threshold == 1:
			start_message_dynamic_threshold_info = global_APIs.dynamic_threshold_list[start_message]
			forward_similar_threshold = start_message_dynamic_threshold_info[0]
			start_message_confidence_interval = start_message_dynamic_threshold_info[1]

			follow_message_happen_time_upper_range = start_message_happen_time + start_message_confidence_interval
			follow_message_happen_time_lower_range = start_message_happen_time - start_message_confidence_interval
			
		else:
			forward_similar_threshold = global_similar_threshold
			follow_message_happen_time_upper_range = int(start_message_happen_time * (2.0 - global_similar_threshold))
			follow_message_happen_time_lower_range = int(start_message_happen_time * global_similar_threshold)
		for follow_message in sorted_start_message_range_message_list:
			follow_message = follow_message[0]
			follow_message_happen_time = happen_matrix[follow_message]["happen_time"]
	
			if follow_message_happen_time <= 1:
				continue		
	
			if use_dynamic_threshold == 1:
				follow_message_dynamic_threshold_info = global_APIs.dynamic_threshold_list[follow_message]
				backward_similar_threshold = follow_message_dynamic_threshold_info[0]
				follow_message_confidence_interval = follow_message_dynamic_threshold_info[1]

				start_message_happen_time_upper_range = follow_message_happen_time + follow_message_confidence_interval
				start_message_happen_time_lower_range = follow_message_happen_time - follow_message_confidence_interval
			else:
				backward_similar_threshold = global_similar_threshold
				start_message_happen_time_upper_range = int(follow_message_happen_time * (2.0 - global_similar_threshold))
				start_message_happen_time_lower_range = int(follow_message_happen_time * global_similar_threshold)

			if follow_message == global_APIs.invalid_message:
				continue
			if follow_message_happen_time > follow_message_happen_time_upper_range or follow_message_happen_time < follow_message_happen_time_lower_range:
				continue
			if start_message_happen_time > start_message_happen_time_upper_range or start_message_happen_time < start_message_happen_time_lower_range:
				continue
			
			forward_pos = calculate_possibility (start_message, follow_message, forward_matrix, 0, start_message, [])

			if forward_pos < forward_similar_threshold:
				#forward_pos is less than threshold, do not waste time to calculate backward_pos
				continue

			backward_pos = calculate_possibility (follow_message, start_message, backward_matrix, 0, follow_message, [])

			if backward_pos >= backward_similar_threshold:
				closest_follow_message_list.append(follow_message)
		total_closest_message_pair_dict[start_message] = closest_follow_message_list
	#}}}

	return total_closest_message_pair_dict

def  update_message_closest_list_for_update_message_list(need_update_single_line_pattern_list, single_line_pattern_range_line_pattern_list, happen_matrix, message_closest_message_list, merge_round_num, not_in_need_update_list_left_message_list = []):
#{{{
	#total_closest_message_pair_dict = find_closest_message_pair_mode_2 (need_update_single_line_pattern_list, happen_matrix, single_line_pattern_range_line_pattern_list, merge_round_num)
	total_closest_message_pair_dict = find_closest_message_pair_mode_3 (need_update_single_line_pattern_list, happen_matrix, single_line_pattern_range_line_pattern_list)

	
	#update message_closest_message_list
	#{{{
	affected_message_list = []
	message_connect_dict = {}
	message_disconnect_dict = {}

	#one complicate situation:
	#M_1, M_2, M_1, M_2,.....(99 times)M_1, M_2
	#M_1 happened 100 times, M_2 also happened 100 times, M_1 and M_2 are in both's range
	#M_2 in M_1's closest pair list, M_1 also in M_2's closest pair list. but we can not connect M_2 to M_1 and M_1 to M_2
	#which one's happen number larger, which one in the front.
	#or which one's name smaller, which one in the front.
	#{{{
	conflict_pair_list = []
	for start_message in total_closest_message_pair_dict:
		start_message_closest_follow_message_list = total_closest_message_pair_dict[start_message]
		for follow_message in start_message_closest_follow_message_list:
			need_update = 0
			if follow_message in total_closest_message_pair_dict:
				follow_message_closest_follow_message_list = total_closest_message_pair_dict[follow_message]
			elif follow_message in message_closest_message_list:
				follow_message_closest_follow_message_list = message_closest_message_list[follow_message]["follow"]
			else:
				follow_message_closest_follow_message_list = []
 			if start_message in follow_message_closest_follow_message_list:
				need_update = 1
			else:
				continue
			
			start_message_happen_time = happen_matrix[start_message]["happen_time"]
			follow_message_happen_time = happen_matrix[follow_message]["happen_time"]
			keep_message = ""
			remove_message = ""
			if start_message_happen_time > follow_message_happen_time:
				keep_message = start_message
				remove_message = follow_message
			elif start_message_happen_time < follow_message_happen_time:
				keep_message = follow_message
				remove_message = start_message
			else:
				pattern = r'message\_([0-9]+)$'
				start_message_num = int(re.match(pattern, start_message).group(1))
				follow_message_num = int(re.match(pattern, follow_message).group(1))
				if start_message_num > follow_message_num:
					keep_message = start_message
					remove_message = follow_message
				else:	
					keep_message = follow_message
					remove_message = start_message
			tmp = []
			tmp.append(keep_message)
			tmp.append(remove_message)
			exist = 0
			for conflict_pair in conflict_pair_list:
				if conflict_pair == tmp:
					exist = 1
			if exist == 0:
				conflict_pair_list.append(tmp)


	for conflict_pair in  conflict_pair_list:
		keep_message = conflict_pair[0]
		remove_message = conflict_pair[1]
		if remove_message in total_closest_message_pair_dict:
			remove_message_closest_list = total_closest_message_pair_dict[remove_message]
		else:
			remove_message_closest_list = []
			for remove_message_follow_message in message_closest_message_list[remove_message]["follow"]:
				remove_message_closest_list.append(remove_message_follow_message)
			
		p = remove_message_closest_list.index(keep_message)
		del(remove_message_closest_list[p])
		total_closest_message_pair_dict[remove_message] = remove_message_closest_list
	#}}}
	#need update message closest message list initialize
	for message in need_update_single_line_pattern_list:
		if not message in message_closest_message_list:
			tmp = {}
			tmp["prior"] = [] 
			tmp["follow"] = []
			message_closest_message_list[message] = tmp

	
	for start_message in total_closest_message_pair_dict:
		closest_follow_message_list = total_closest_message_pair_dict[start_message]
		previous_start_message_follow_list = message_closest_message_list[start_message]["follow"]
		connect_follow_list = []
		disconnect_follow_list = []
		for previous_follow_message in previous_start_message_follow_list:
			if not previous_follow_message in closest_follow_message_list:
				#previous follow, now it's not
				disconnect_follow_list.append(previous_follow_message)
		for follow_message in closest_follow_message_list:
			if not follow_message in previous_start_message_follow_list:
				connect_follow_list.append(follow_message)
		message_connect_dict [start_message] = connect_follow_list
		message_disconnect_dict [start_message] = disconnect_follow_list

	#closest message list need to connect and disconnect twice
	#1)connect and disconnect all direct related message, 2)connect and disconnect indirect messages
	#I do this have a reason, first I need to connect or cut all direct edges. If I analyze indirect related messages before all edges are connected or disconnected, that could affect the result.  

	#connect and disconnect direct related messages
	#{{{
	for start_message in message_disconnect_dict:
		disconnect_follow_list = message_disconnect_dict[start_message]
		if disconnect_follow_list == []:
			continue
		if not start_message in affected_message_list:
			#only when need to update start's status then add start into affected message list
			affected_message_list.append(start_message)
		for disconnect_follow_message in disconnect_follow_list:
			if not disconnect_follow_message in affected_message_list:
				affected_message_list.append(disconnect_follow_message)
			message_closest_message_list = disconnect_closest_message_pair(start_message, disconnect_follow_message, message_closest_message_list, single_line_pattern_range_line_pattern_list)

	for start_message in message_connect_dict:
		connect_follow_list = message_connect_dict[start_message]
		if connect_follow_list == []:
			continue
		if not start_message in affected_message_list:
			#only when need to update start's status then add start into affected message list
			affected_message_list.append(start_message)
		for connect_follow_message in connect_follow_list:
			if not connect_follow_message in affected_message_list:
				affected_message_list.append(connect_follow_message)
			message_closest_message_list = connect_closest_message_pair(start_message, connect_follow_message, message_closest_message_list, single_line_pattern_range_line_pattern_list)
	#}}}

	#connect and disconnect indirect messages
	#{{{
	for start_message in message_disconnect_dict:
		disconnect_follow_list = message_disconnect_dict[start_message]
		for disconnect_follow_message in disconnect_follow_list:
			start_message_prior_list = message_closest_message_list[start_message]["prior"]
			disconnect_follow_message_follow_list = message_closest_message_list[disconnect_follow_message]["follow"]
			for start_message_prior_message in start_message_prior_list:
				if start_message_prior_message in message_connect_dict and disconnect_follow_message in message_connect_dict[start_message_prior_message]:
					continue
				message_closest_message_list = disconnect_closest_message_pair(start_message_prior_message, disconnect_follow_message, message_closest_message_list, single_line_pattern_range_line_pattern_list)
			for disconnect_follow_message_follow_message in disconnect_follow_message_follow_list:
				if start_message in message_connect_dict and disconnect_follow_message_follow_message in message_connect_dict[start_message]:
					continue
				message_closest_message_list = disconnect_closest_message_pair(start_message, disconnect_follow_message_follow_message, message_closest_message_list, single_line_pattern_range_line_pattern_list)
			
	for start_message in message_connect_dict:
		connect_follow_list = message_connect_dict[start_message]
		for connect_follow_message in connect_follow_list:
			start_message_prior_list = message_closest_message_list[start_message]["prior"]
			connect_follow_message_follow_list = message_closest_message_list[connect_follow_message]["follow"]
			for start_message_prior_message in start_message_prior_list:
				if start_message_prior_message in message_disconnect_dict and connect_follow_message in message_disconnect_dict[start_message_prior_message]:
					continue
				message_closest_message_list = connect_closest_message_pair(start_message_prior_message, connect_follow_message, message_closest_message_list, single_line_pattern_range_line_pattern_list)
			for connect_follow_message_follow_message in connect_follow_message_follow_list:
				if start_message in message_disconnect_dict and connect_follow_message_follow_message in message_disconnect_dict[start_message]:
					continue
				message_closest_message_list = connect_closest_message_pair(start_message, connect_follow_message_follow_message, message_closest_message_list, single_line_pattern_range_line_pattern_list)
	#}}}
	#}}}


	tmp = []
	tmp.append(affected_message_list)
	tmp.append(message_closest_message_list)
	tmp.append(single_line_pattern_range_line_pattern_list)
	return tmp
#}}}

def connect_closest_message_pair(start_message, connect_follow_message, message_closest_message_list, single_line_pattern_range_line_pattern_list):
	start_message_follow_list = message_closest_message_list[start_message]["follow"]
	connect_follow_message_prior_list = message_closest_message_list[connect_follow_message]["prior"]
	
	if connect_follow_message in single_line_pattern_range_line_pattern_list[start_message]:
		#if this connect follow message in start message's range, than connect them
		if not connect_follow_message in start_message_follow_list:
			start_message_follow_list.append(connect_follow_message)
			message_closest_message_list[start_message]["follow"] = start_message_follow_list
		if not start_message in connect_follow_message_prior_list:
			connect_follow_message_prior_list.append(start_message)
			message_closest_message_list[connect_follow_message]["prior"] = connect_follow_message_prior_list
	return message_closest_message_list

	
def disconnect_closest_message_pair(start_message, disconnect_follow_message, message_closest_message_list, single_line_pattern_range_line_pattern_list):
	start_message_follow_list = message_closest_message_list[start_message]["follow"]
	disconnect_follow_message_prior_list = message_closest_message_list[disconnect_follow_message]["prior"]

	if disconnect_follow_message in start_message_follow_list:
		p = start_message_follow_list.index(disconnect_follow_message)
		del (start_message_follow_list[p])
		message_closest_message_list[start_message]["follow"] = start_message_follow_list
		
	if start_message in disconnect_follow_message_prior_list:
		p = disconnect_follow_message_prior_list.index(start_message)
		del (disconnect_follow_message_prior_list[p])
		message_closest_message_list[disconnect_follow_message]["prior"] = disconnect_follow_message_prior_list
	return message_closest_message_list

def block_merge_from_message_closest_message_list (block_list, affected_message_list, message_closest_message_list, single_line_pattern_db):
	done_message_list = []
	start_message_list = []
	deleted_block_name_list = []
	new_affected_message_list = []
	#first, reset all affected messages' belong block
	#maybe later assign a total same belong block name, but this time reset them first
	#all messages which belong block have been removed, add them into new affected message list.
	#{{{
	for message in affected_message_list:
		new_affected_message_list.append(message)
		if "belong_block" in single_line_pattern_db[message] and not single_line_pattern_db[message]["belong_block"] == "": 
			belong_block = single_line_pattern_db[message]["belong_block"]
			single_line_pattern_db[message]["belong_block"] = ""
			if belong_block in block_list:
				del (block_list[belong_block])
			if not belong_block in deleted_block_name_list:
				deleted_block_name_list.append(belong_block)
	
	for message in single_line_pattern_db:
		if single_line_pattern_db[message]["belong_block"] in deleted_block_name_list:
			single_line_pattern_db[message]["belong_block"] = ""
			if not message in new_affected_message_list:
				new_affected_message_list.append(message)
	#}}}
	#generate start_message_list
	#{{{
	for message in new_affected_message_list:
		if message_closest_message_list[message]["follow"] == [] and message_closest_message_list[message]["prior"] == []:
			done_message_list.append (message)
			continue
		if message in message_closest_message_list and message_closest_message_list[message]["prior"] == [] and not message_closest_message_list[message]["follow"] == []:
			# this message have no prior message but have follow message, it should be a start message
			start_message_list.append(message)
	#}}}
	#block merge
	#{{{
	report_error = 0 
	for start_message in start_message_list:
		tmp_block_fifo = []
		tmp_block_list = []
		tmp_block_finish_message_list = []
		tmp_block_fifo.append(start_message)
		block_grow_error = 0
		while not tmp_block_fifo == []:
			current_message = tmp_block_fifo[0]
				
			current_message_follow_message_list = message_closest_message_list[current_message]["follow"]
			if not current_message_follow_message_list == []:
				for follow_message in current_message_follow_message_list:
					if not follow_message in tmp_block_list and not follow_message in tmp_block_fifo:
						tmp_block_fifo.append(follow_message)
			else:
				if tmp_block_finish_message_list == []:
					tmp_block_finish_message_list.append(current_message)
				elif len(tmp_block_finish_message_list) >= 1 and not current_message in tmp_block_finish_message_list:
					block_grow_error = 1
					break
			if not current_message in tmp_block_finish_message_list:
				tmp_block_list.append(current_message)
			del(tmp_block_fifo[0])
		if block_grow_error == 1:
			#report error
			#this is for preventing one message could lead to two ends.
			#right now I just report it, in the future I should add more features
			#this is caused by I just analyze one message's 10 recent seen range message. if analyze the whole range message list this will gone.
			if report_error == 1:
				print "merge error!"
				print "block start message " + start_message
				print "block tmp list " + str(tmp_block_list)
				print "block current finish message " + str(tmp_block_finish_message_list)
				print "conflict message " + current_message
			continue
		#add last message to tmp_block_list
		#error judge is done before, at this point there should have no problem


		tmp_block_list.append(tmp_block_finish_message_list[0])
		#only this block successfuly done, can insert them into done list
		for block_message in tmp_block_list:
			done_message_list.append(block_message)

	
		#this is a total new block, only initialize the block name and its pattern
		block_num = get_lowest_block_name_list_num (block_list)
		block_name = "block_" + str(block_num)
		block_list[block_name] = {}
		block_list[block_name]["pattern"] = tmp_block_list
		block_list[block_name]["happen_count"] = {}
		block_list[block_name]["happen_count"]["correct"] = 0
		block_list[block_name]["happen_count"]["incorrect"] = 0
		for message in tmp_block_list:
			single_line_pattern_db[message]["belong_block"] = block_name
	#}}}
	
	#final test
	#{{{
	left_message_list = []
	if not len(done_message_list) == len(new_affected_message_list):
		if len(done_message_list) > len(new_affected_message_list):
			if report_error == 1:	
				print "done message list bigger"
				print len(new_affected_message_list)
				print len(done_message_list)
			for i in range(0, len(done_message_list)):
				this_message = done_message_list[i]
				for j in range(i + 1, len(done_message_list)):
					next_message = done_message_list[j]
					if this_message == next_message:
						#done list have repeat message
						#meaning one message been included in multiple blocks
						if not this_message in left_message_list:
							left_message_list.append(this_message)
						continue
		else:
			if report_error == 1:	
				print "affected list have left message"
				print "affect_length " + str(len(new_affected_message_list))
				print "done list length " + str(len(done_message_list))
			for i in range(0, len(new_affected_message_list)):
				this_message = new_affected_message_list[i]
				for j in range(i + 1, len(new_affected_message_list)):
					next_message = new_affected_message_list[j]
					if this_message == next_message:
						print "new_affected_message_list have repeat message"
						print this_message

				if not this_message in done_message_list:
					left_message_list.append(this_message)
	#}}}	
	tmp = []
	tmp.append(block_list)
	tmp.append(single_line_pattern_db)
	tmp.append(left_message_list)
	
	return tmp

def calculate_possibility(start_message, finish_message, next_pos_matrix, level, root_start_message, previous_step_stock):
#{{{
	if start_message == "last" or finish_message == "last":
		return 0.0
	total_pos = 0.0
	if start_message == finish_message:
		#found the final destination message
		return 1.0
	if level == global_search_deep_level:
		return 0.0
	if start_message == root_start_message and not level == 0:
		return 0.0
	
	start_message_next_message_list = []
	for next_message in next_pos_matrix[start_message]:
		start_message_next_message_list.append(next_message)
	start_message_next_pos_list = next_pos_matrix[start_message]

	new_previous_step_stock = []
	for previous in previous_step_stock:
		new_previous_step_stock.append(previous)
	new_previous_step_stock.append(start_message)


	for next_message in start_message_next_message_list:
		if start_message in previous_step_stock:
			return 1.0
		else:	
			pos = start_message_next_pos_list[next_message]
			pos = pos*calculate_possibility (next_message, finish_message, next_pos_matrix, level + 1, root_start_message, new_previous_step_stock)
			
			total_pos += pos
	return total_pos
#}}}

def input_file_exist_single_line_report_file_compare_single_line_db(input_file, file_single_line_report, single_line_pattern_db):
	fl = open(input_file, "r")
	new_add_single_line_pattern_list = []
	line_count = 1
	single_line_report_count = 0
	for line in fl.readlines():
		report_list_line = file_single_line_report[single_line_report_count]
		report_message_name = report_list_line[0]
		if not report_message_name in single_line_pattern_db:
			if not global_APIs.is_baler_mutrino_format(line):
				line_message = global_APIs.get_line_message(line)
				this_line_pattern = global_APIs.gen_line_pattern(line_message)
			else:
				line_message = global_APIs.get_line_message(line)
				this_line_pattern = global_APIs.gen_line_pattern(line_message)
				#this_line_pattern = global_APIs.gen_baler_line_pattern (this_line)
			this_line_correspond_pattern_name = report_message_name
			new_add_single_line_pattern_list.append(this_line_correspond_pattern_name)
			tmp = {}
			tmp["pattern"] = this_line_pattern
			tmp["belong_block"] = ""
			single_line_pattern_db[this_line_correspond_pattern_name] = tmp
		line_count += 1
		single_line_report_count += 1
	tmp = []	
	tmp.append(single_line_pattern_db)
	tmp.append(new_add_single_line_pattern_list)
	return tmp 

def input_file_single_line_pattern_grow (input_file, single_line_pattern_db): 
	file_single_line_report = []	
	fl = open(input_file, "r")
	new_add_single_line_pattern_list = []
	line_count = 1
	for line in fl.readlines():
		result = search_pattern_db_for_correspond_or_add_in_pattern_db(line, single_line_pattern_db, new_add_single_line_pattern_list)
		#this time we don't need to care new add pattern, but in the future may need
		line_pattern_name = result[0]
		single_line_pattern_db = result[1]
		new_add_single_line_pattern_list = result[2]
		
		tmp = []
		tmp.append (line_pattern_name)
		tmp.append (line_count)
		file_single_line_report.append(tmp)
		line_count += 1
	fl.close()
	tmp = []
	tmp.append(file_single_line_report)
	tmp.append(single_line_pattern_db)
	tmp.append(new_add_single_line_pattern_list)
	return tmp 



def input_file_single_line_report_extraction (input_file, single_line_pattern_db):
	#this is only for report extraction, this will not affect single_line_pattern_db 
	file_single_line_report = []	
	fl = open(input_file, "r")
	new_add_single_line_pattern_list = []
	line_count = 1
	for line in fl.readlines():
		if not global_APIs.is_baler_mutrino_format(line):
			line_message = global_APIs.get_line_message(line)
			line_pattern = global_APIs.gen_line_pattern(line_message)
		else:
			line_message = global_APIs.get_line_message(line)
			line_pattern = global_APIs.gen_line_pattern(line_message)
			#this_line_pattern = global_APIs.gen_baler_line_pattern (this_line)
		if line_pattern == []:
			tmp = ["0", "invalid_line"]
			line_pattern.append(tmp) 
		
		correspond_pattern_name_list = global_APIs.search_correspond_pattern_from_single_line_pattern_db (line_pattern, single_line_pattern_db)
		line_pattern_name = ""
		if not len(correspond_pattern_name_list) == 0:
			line_pattern_name = correspond_pattern_name_list[0]
		tmp = []
		tmp.append (line_pattern_name)
		tmp.append (line_count)
		file_single_line_report.append(tmp)
		line_count += 1
	fl.close()
	return file_single_line_report

