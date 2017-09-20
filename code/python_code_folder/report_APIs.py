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

def block_report_folder_total_event_analyze (folder_name = "block_report"):
#{{{
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
	fl = open("total_event_report.txt", "w")
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

	fl = open("single_line_report.txt", "w")
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

