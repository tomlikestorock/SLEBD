#!/usr/bin/python
#coding:utf-8
import os
import sys
import re 
import shutil
import operator 
import global_APIs
import database_opt
import sequence_pattern_mining


def block_length_average_summary (folder_name = "block_report"):
#{{{
	total_event_list = []
	sub_folder_list = global_APIs.get_folder_file_list (folder_name)
	count = 0
	limit = 1
	total_event_length_count = {}
	for sub_folder in sub_folder_list:
		if sub_folder == "block_report/node_stack.txt":
			continue
		print sub_folder
		node_file_list = sequence_pattern_mining.one_sub_daily_folder_report_node_block_summary (sub_folder)
		for node_name in node_file_list:
			block_report_file = node_file_list[node_name]["block"]
			single_line_report_file = node_file_list[node_name]["single"]
			fl = open(block_report_file, "r")

			block_name_pattern = r'block\_([0-9]+)$'
			for line in fl.readlines():
				line = line.split()
				event_name = line[0]
				
				matchobj = re.match (block_name_pattern, event_name)
				if not matchobj:
					continue
				start_line = int(line[1])
				finish_line = int(line[2])
				length = finish_line - start_line + 1
				if event_name in total_event_length_count:
					tmp = total_event_length_count[event_name]
					tmp["count"] += 1
					tmp["total_length"] += length
				else:
					tmp = {}
					tmp["count"] = 1
					tmp["total_length"] = length
				total_event_length_count[event_name] = tmp
			fl.close()
	
	event_name_average_length_list = {}
	for event_name in total_event_length_count:
		average_length =  total_event_length_count[event_name]["total_length"] / total_event_length_count[event_name]["count"]
		event_name_average_length_list[event_name] = average_length

	length_count_list = {}
	for event_name in event_name_average_length_list:
		length = event_name_average_length_list[event_name]
		if length in length_count_list:
			length_count_list[length] += 1
		else:
			length_count_list[length] = 1
	for length in length_count_list:
		print "length " + str(length) + " count " + str(length_count_list[length])

#}}}

def block_report_folder_total_event_analyze (folder_name = "block_report", block_extract_report_folder_name = "block_extract_report"):
#{{{
	total_event_report_name = block_extract_report_folder_name + "/total_event_report.txt"
	total_single_line_report_name = block_extract_report_folder_name + "/single_line_report.txt"
	total_event_list = []
	sub_folder_list = global_APIs.get_folder_file_list (folder_name)
	count = 0
	limit = 1
	total_event_happen_count = {}
	total_event_count = 0
	single_line_happen_count = {}
	total_single_line_count = 0
	for sub_folder in sub_folder_list:
		if sub_folder == "block_report/node_stack.txt":
			continue
		node_file_list = sequence_pattern_mining.one_sub_daily_folder_report_node_block_summary (sub_folder)
		for node_name in node_file_list:
			block_report_file = node_file_list[node_name]["block"]
			single_line_report_file = node_file_list[node_name]["single"]
			fl = open(block_report_file, "r")
			for line in fl.readlines():
				line = line.split()
				event_name = line[0]
				if event_name in total_event_happen_count:
					tmp = total_event_happen_count[event_name]
					tmp += 1
				else:
					tmp = 1
				total_event_happen_count[event_name] = tmp
				total_event_count += 1
			fl.close()
			fl = open(single_line_report_file, "r")
			for line in fl.readlines():
				line = line.split()
				event_name = line[0]
				if event_name in single_line_happen_count:
					tmp = single_line_happen_count[event_name]
					tmp += 1
				else:
					tmp = 1
				single_line_happen_count[event_name] = tmp
				total_single_line_count += 1
			fl.close()
		count += 1
	fl = open(total_event_report_name, "w")
	happen_only_once = []
	for event in total_event_happen_count:
		if total_event_happen_count[event] == 1:
			happen_only_once.append(event)
			continue
		tmp = event
		tmp += ": "
		tmp += str (total_event_happen_count[event])
		tmp += "\n"
		fl.write(tmp)
	tmp = "total_event_count: " + str(total_event_count) + ("\n")
	fl.write(tmp)
	fl.write("\n")
	fl.write("\n")
	fl.write("\n")
	for event in happen_only_once:
		tmp = event + ("\n")
		fl.write(tmp)
	fl.close()

	fl = open(total_single_line_report_name, "w")
	happen_only_once = []
	for event in single_line_happen_count:
		if single_line_happen_count[event] == 1:
			happen_only_once.append(event)
			continue
		tmp = event
		tmp += ": "
		tmp += str (single_line_happen_count[event])
		tmp += "\n"
		fl.write(tmp)
	tmp = "total_single_line_count: " + str(total_single_line_count) + ("\n")
	fl.write(tmp)
	fl.write("\n")
	fl.write("\n")
	fl.write("\n")
	for event in happen_only_once:
		tmp = event + ("\n")
		fl.write(tmp)
	fl.close()
#}}}
	
def total_correct_fail_event_count(block_extract_report_path):
#{{{
    total_event_report_file = block_extract_report_path + '/total_event_report.txt'
    total_fail_report_file = block_extract_report_path + '/extract_error_report.txt'
    total_event_fl = open(total_event_report_file, 'r')
    block_pattern = 'block_([0-9]+): ([0-9]+)$'
    total_block_occur_list = { }
    for line in total_event_fl.readlines():
        matchobj = re.match(block_pattern, line)
        if matchobj:
            block_num = matchobj.group(1)
            block_occur = matchobj.group(2)
            total_block_occur_list['block_' + str(block_num)] = int(block_occur)
            continue
    total_event_fl.close()
    total_block_fail_list = { }
    fail_event_pattern = "\\[([0-9]+), \\'(block\\_[0-9]+)\\'\\]$"
    current_file = ''
    error_fl = open(total_fail_report_file, 'r')
    for line in error_fl.readlines():
        matchobj_event = re.match(fail_event_pattern, line)
        if matchobj_event:
            event_name = matchobj_event.group(2)
            if event_name in total_block_fail_list:
                total_block_fail_list[event_name] += 1
            else:
                total_block_fail_list[event_name] = 1
    for fail_block in total_block_fail_list:
        if total_block_fail_list[fail_block] > 10:
            print fail_block + ' ' + str(total_block_fail_list[fail_block])
            continue
    error_fl.close()
#}}}

def total_block_fail_event_summary (block_extract_report_path):
#{{{	
	extract_error_list_file_name = 	block_extract_report_path + "/" + "extract_error_report.txt"
	log_file_pattern = r'(.*)/([0-9]+)/(.*).txt$' 
	#../log_files/2_days/3/3_c0-0c0s9n3.txt
	
	event_pattern = r'\[([0-9]+), \'(block\_[0-9]+)\'\]$' 
	#[414, 'block_86']
	current_file = ""
	error_fl = open(extract_error_list_file_name, "r")

	total_block_fail_event_list = {} 
	for line in error_fl.readlines():
		matchobj_file = re.match (log_file_pattern, line) 
		matchobj_event = re.match (event_pattern, line)
		if matchobj_file:
			folder_name = matchobj_file.group(2)
			file_name = matchobj_file.group(3)
			file_path_name = folder_name + "/" + file_name
			current_file = file_path_name
		if matchobj_event:
			event_line = matchobj_event.group(1)	
			event_name = matchobj_event.group(2)	
			if event_name in total_block_fail_event_list:
				fail_event_record_list = total_block_fail_event_list[event_name]
			else:
				fail_event_record_list = []
			one_fail_event_record = [current_file, event_line]
			fail_event_record_list.append(one_fail_event_record)
			total_block_fail_event_list[event_name] = fail_event_record_list

	return total_block_fail_event_list	
#}}}

def generate_fail_block_summary_files(total_block_fail_event_list):
	fail_example_file_extract_folder = "fail_block_example_folder"
	if not os.path.isdir (fail_example_file_extract_folder):
		os.mkdir (fail_example_file_extract_folder)
	for block_name in total_block_fail_event_list:
		report_file = fail_example_file_extract_folder + "/" + block_name + ".txt"
		report_fl = open(report_file, "w")
		block_fail_list = total_block_fail_event_list[block_name]
		for fail_record in block_fail_list:
			record_file = fail_record[0]
			record_line = fail_record[1]
			orig_file_name = orig_log_file_folder + "/" + record_file + ".txt"
			orig_fl = open(orig_file_name, "r")
			orig_fl_lines = orig_fl.readlines()
			orig_file_lines_length = len(orig_fl_lines)
			report_fl.write(orig_file_name + "\n")
			report_fl.write("failed line: " + record_line + "\n")
			for i in range (int(record_line) - 5, int(record_line)  + 5):
				if int(record_line) - 5 < 0:
					continue
				if int(record_line) + 5 > orig_file_lines_length:
					continue
				report_fl.write("line " + str(i+1) + " " + orig_fl_lines[i])	
			report_fl.write("\n")
		report_fl.close()



