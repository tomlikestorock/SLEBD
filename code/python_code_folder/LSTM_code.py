#!/usr/bin/python
import os
import re
import shutil
import time 
import math
import global_APIs
import report_APIs
import sequence_pattern_mining

import math
import numpy
from keras.datasets import imdb
from keras.models import Sequential
from keras.models import load_model 
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers.embeddings import Embedding
from keras.preprocessing import sequence

max_length = 500
min_length = 100 
max_review_length = 500

#fail, correct file generate
#block_fail_event_summary
#correct_sequences_extract
#fail_sequences_extract
#event_name_convert
#find_event_sequence_extract_range
#{{{
def block_fail_event_summary(care_block_name, block_extract_report_path):
#{{{
	total_block_fail_event_list = report_APIs.total_block_fail_event_summary(block_extract_report_path)
	return total_block_fail_event_list["care_block_name"]

#}}}

def correct_sequences_extract (care_block_name, block_report_path):
#{{{
	sub_folder_list = global_APIs.get_folder_file_list(block_report_path)
	#be safe, sort it
	sub_folder_list = global_APIs.sub_folder_number_sort(block_report_path, sub_folder_list)
	total_event_sequence_list = []
	for sub_folder in sub_folder_list:
		if sub_folder == "block_report/150":
			break
		print sub_folder
		sub_file_list = global_APIs.get_folder_file_list(sub_folder)
		for file_name in sub_file_list:
			#print file_name
			if not global_APIs.this_report_file_is_block_file(file_name, block_report_path):
				continue
			fl = open (file_name, "r")
			event_list = []
			for line in fl.readlines():
				event_list.append(line.split()[0])
			fl.close()
			last_care_block_num = -1
			for i in range (0, len( event_list)):
				event = event_list[i]
				care_block_num = -1
				if event == care_block_name:
					care_block_num = i
				else:
					continue
				start_num = find_event_sequence_extract_range(care_block_num, last_care_block_num)
				
				last_care_block_num = care_block_num	
				if not start_num == -1:
					event_sequence = event_list[start_num: care_block_num]
					total_event_sequence_list.append(event_sequence)
	
	care_block_work_path_name = care_block_name + "_work_path"
	sequence_file_name = care_block_work_path_name + "/correct_sequences.txt"
	fl = open(sequence_file_name, "w")
	
	for event_sequence in total_event_sequence_list:
		new_event_sequence = ""
		for event in event_sequence:
			#new_event_sequence += event + " "	
			new_event_sequence += event_name_convert(event) + " "	
		new_event_sequence += ("\n")		
		fl.write(new_event_sequence)	
	fl.close()
#}}}

def fail_sequences_extract (care_block_name, fail_event_record_list, block_report_path):
#{{{
	#['0/0_c0-0c1s0n1', '1879']
	#block_report/0/0_c0-0c1s10n2.txt_block_report.txt
	total_fail_event_sequence_list = []
	for fail_event in fail_event_record_list:
		file_name = fail_event[0]
		fail_line = fail_event[1]
			
		file_path = block_report_path + "/" + file_name + ".txt" + "_block_report.txt"
		print file_path
		care_event_point_list = []
		event_list = []
		fl = open(file_path, "r")
		event_num = 0
		
		for line in fl.readlines ():
			event_list.append(line.split()[0])
			start_line_num = line.split()[1]
			finish_line_num = line.split()[2]
			if int(start_line_num) == int(fail_line):
				care_event_point_list.append(event_num)
			event_num += 1
		fl.close()	

		last_care_block_num = -1
		for care_block_num in care_event_point_list:
			start_num = find_event_sequence_extract_range(care_block_num, last_care_block_num)
			
			last_care_block_num = care_block_num
			if not start_num == -1:
				event_sequence = event_list[start_num: care_block_num]
				total_fail_event_sequence_list.append(event_sequence)
	
	care_block_work_path_name = care_block_name + "_work_path"
	sequence_file_name = care_block_work_path_name + "/fail_sequences.txt"
	fl = open(sequence_file_name, "w")
	for event_sequence in total_fail_event_sequence_list:
		new_event_sequence = ""
		for event in event_sequence:
			#new_event_sequence += event + " "	
			new_event_sequence += event_name_convert(event) + " "	
		new_event_sequence += ("\n")		
		fl.write(new_event_sequence)	
	fl.close()
#}}}

def event_name_convert (event_name):
#{{{
	new_event_name = ""
	message_pattern = r'message_([0-9]+)$'
	block_pattern = r'block_([0-9]+)$'
	message_matchobj = re.match(message_pattern, event_name)
	block_matchobj = re.match(block_pattern, event_name)
	number = -1 
	if message_matchobj:
		number = int(message_matchobj.group(1))
	if block_matchobj:
		number = int(block_matchobj.group(1)) + 3000
	
	new_event_name = str(number)

	return new_event_name
#}}}

def find_event_sequence_extract_range (care_block_num, last_care_block_num):
#{{{
	start_num = -1	
	if last_care_block_num == -1:
		range_start = 0
	else:
		range_start = last_care_block_num + 1
	
	if care_block_num - 1 - range_start < min_length:
		start_num = -1
	elif care_block_num - 1 - range_start > max_length:
		start_num = care_block_num - 1 - max_length
	else :
		start_num = range_start
	return start_num				
#}}}
#}}}

#SMOTE operation
#SMOTE_gen
#	generate_test_file
#	generate_learn_file
#{{{
def SMOTE_gen(care_block_name, SMOTE_config_list):
#{{{
	#[positive_fold, negative_fold, positive_repeat, negative_repeat]
	care_block_work_path_name = care_block_name + "_work_path"
	correct_file = care_block_work_path_name + "/" + "correct_sequences.txt"
	fail_file = care_block_work_path_name + "/" + "fail_sequences.txt"
	
	correct_list = []
	fl = open(correct_file, "r")
	for line in fl.readlines():
		line = line.split()
		correct_list.append(line)
	fl.close() 	
	
	fail_list = []
	fl = open(fail_file, "r")
	for line in fl.readlines():
		line = line.split()
		fail_list.append(line)
	fl.close() 	
	for SMOTE_config in SMOTE_config_list:
		SMOTE_config_sub_name = str(SMOTE_config[0]) + "_" + str(SMOTE_config[1]) + "_" + str(SMOTE_config[2]) + "_" + str(SMOTE_config[3])
		SMOTE_config_sub_path = care_block_work_path_name + "/" + SMOTE_config_sub_name
		if not os.path.isdir (SMOTE_config_sub_path):
			os.mkdir (SMOTE_config_sub_path)
		

		correct_fold_num = SMOTE_config[0]
		fail_fold_num = SMOTE_config[1]
		correct_repeat_num = SMOTE_config[2]
		fail_repeat_num = SMOTE_config[3]

		#assign each part's length 
		#{{{
		correct_length = len(correct_list) 
		fail_length = len(fail_list)
		if correct_fold_num <= 1:
			correct_learn_length = correct_length
			correct_test_length = 0
		else:
			correct_test_length = int(math.ceil((float(correct_length) / float(correct_fold_num ))))
			correct_learn_length = correct_length - correct_test_length
		
		if fail_fold_num <= 1:
			fail_learn_length = fail_length
			fail_test_length = 0
		else:
			fail_test_length = int(math.ceil((float(fail_length) / float(fail_fold_num ))))
			fail_learn_length = fail_length - fail_test_length
		#}}}

		#get each part's real list
		#{{{
		#now I just set the test part range from 0 to test_length - 1, the rest part is learning part. maybe in the future I can change it.
		fail_test_range_start = 0
		fail_test_range_finish = fail_test_length - 1
		
		correct_test_range_start = 0
		correct_test_range_finish = correct_test_length - 1 
	
		fail_test_part = []
		fail_learn_part = []
		correct_test_part = []
		correct_learn_part = []
	
		if fail_fold_num <= 1:
			fail_learn_part = fail_list
			fail_test_part = fail_list
		else:
			for i in range(0, len(fail_list)):
				if i >= fail_test_range_start and i <= fail_test_range_finish:
					fail_test_part.append(fail_list[i])
				else:
					fail_learn_part.append(fail_list[i])
 
		if correct_fold_num <= 1:
			correct_learn_part = correct_list
			correct_test_part = correct_list
		else:
			for i in range(0, len(correct_list)):
				if i >= correct_test_range_start and i <= correct_test_range_finish:
					correct_test_part.append(correct_list[i])
				else:
					correct_learn_part.append(correct_list[i])
		#}}}

		generate_test_file(SMOTE_config_sub_path, correct_test_part, fail_test_part)
		generate_learn_file(SMOTE_config_sub_path, correct_learn_part, fail_learn_part, correct_repeat_num, fail_repeat_num)
#}}}

def generate_test_file(SMOTE_config_sub_path, correct_test_part, fail_test_part):
#{{{
	total_test_file_name = SMOTE_config_sub_path + "/total_test.txt"
	fail_test_file_name = SMOTE_config_sub_path + "/fail_test.txt"
	correct_test_file_name = SMOTE_config_sub_path + "/correct_test.txt"
	total_fl = open(total_test_file_name, "w")
	fail_fl = open(fail_test_file_name, "w")
	correct_fl = open(correct_test_file_name, "w")
	for sequence in correct_test_part:
		event_num_sequence = ""
		for event in sequence:
			event_num_sequence += event + " "
		event_num_sequence += "0" + "\n"
		total_fl.write(event_num_sequence)
		correct_fl.write(event_num_sequence)
	
	for sequence in fail_test_part:
		event_num_sequence = ""
		for event in sequence:
			event_num_sequence += event + " "
		event_num_sequence += "1" + "\n"
		total_fl.write(event_num_sequence)
		fail_fl.write(event_num_sequence)

	total_fl.close()
	fail_fl.close()
	correct_fl.close()
#}}}

def generate_learn_file(SMOTE_config_sub_path, correct_learn_part, fail_learn_part, correct_repeat_num, fail_repeat_num):
#{{{
	#my current strategie is:
	#correct part have 312 events, fail part have 31 events, fail repeat 5 times
	#have 31 parts, each part fail have 5 events, correct have 10 events
	#[fail(0-4), correct (0-10), fail(1-5), correct(11-20), fail(2-6), correct(21-30)]


	#if correct part and fail part number similar, for example, 60: 50 
	#total_part_num is the less one's length = 50
	#each part have 1 correct and 1 fail
	#one part make the less one start pos push forward 1
	#one part make the more one start pos push forward length/total_part_num
	print len (correct_learn_part)
	print len (fail_learn_part)



	correct_learn_length = len(correct_learn_part)
	fail_learn_length = len(fail_learn_part)
	if fail_learn_length > correct_learn_length:
		total_part_num = correct_learn_length
	else:
		total_part_num = fail_learn_length

	each_part_correct_event_num = correct_learn_length / total_part_num
	each_part_fail_event_num = fail_learn_length / total_part_num
	
	learn_file_name = SMOTE_config_sub_path + "/learn.txt"
	
	correct_start_pos = 0
	fail_start_pos = 0
	
	fl = open(learn_file_name, "w")
	for i in range (0, total_part_num):
		for k in range (0, each_part_fail_event_num):
			for j in range (0, fail_repeat_num):
				append_pos = 0
				if fail_start_pos + j >= fail_learn_length:
					append_pos = fail_start_pos + j - fail_learn_length
				else:
					append_pos = fail_start_pos + j
				fail_sequence = fail_learn_part[append_pos]
				event_sequence = ""
				for event in fail_sequence:
					event_sequence += event + " "
				event_sequence += "1\n"
				fl.write(event_sequence)
			fail_start_pos += 1

		for k in range (0, each_part_correct_event_num):
			for j in range (0, correct_repeat_num):
				append_pos = 0
				if correct_start_pos + j >= correct_learn_length:
					append_pos = correct_start_pos + j - correct_learn_length
				else:
					append_pos = correct_start_pos + j
				correct_sequence = correct_learn_part[append_pos]
				event_sequence = ""
				for event in correct_sequence:
					event_sequence += event + " "
				event_sequence += "0\n"
				fl.write(event_sequence)
			correct_start_pos += 1
	
	if total_part_num == fail_learn_length and correct_repeat_num == 1:
		#part number is based on fail length, means fail is less, correct could have left
		for i in range (correct_start_pos, correct_learn_length):
			correct_sequence = correct_learn_part[i]
			event_sequence = ""
			for event in correct_sequence:
				event_sequence += event + " "
			event_sequence += "0\n"
			fl.write(event_sequence)

	if total_part_num == correct_learn_length and fail_repeat_num == 1:
		for i in range (fail_start_pos, fail_learn_length):
			fail_sequence = fail_learn_part[i]
			event_sequence = ""
			for event in fail_sequence:
				event_sequence += event + " "
			event_sequence += "1\n"
			fl.write(event_sequence)



	fl.close()
#}}}
#}}}


#LSTM model operations
#block_LSTM_model_train
#block_LSTM_model_test
#sequence_file_read
#LSTM_run_main
#{{{
def block_LSTM_model_train(care_block_work_path):
#{{{
	learn_file = care_block_work_path + "/learn.txt"
	X_train, y_train = sequence_file_read(learn_file)
	X_train = sequence.pad_sequences(X_train, maxlen=max_review_length)
	
	# create the model
	embedding_vecor_length = 16
	top_words = 5000
	model = Sequential()
	model.add(Embedding(top_words, embedding_vecor_length, input_length=max_review_length))
	model.add(LSTM(150))
	model.add(Dense(1, activation='sigmoid'))
	model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
	print(model.summary())
	model.fit(X_train, y_train, nb_epoch=5, batch_size=32)
	
	json_string = model.to_json()
	json_file_name = care_block_work_path + "/LSTM_model_json.txt"
	json_fl = open(json_file_name, "w")
	for string in json_string:
		json_fl.write(string)
	json_fl.close

	model_h5_file = care_block_work_path + "/LSTM_model.h5"
	model.save(model_h5_file)
#}}}

def block_LSTM_model_test (care_block_work_path):
#{{{
	model_h5_file = care_block_work_path + "/LSTM_model.h5"
	model = load_model(model_h5_file)

	total_test_file = care_block_work_path + "/total_test.txt"
	total_test_x, total_test_y = sequence_file_read(total_test_file)
	correct_test_file = care_block_work_path + "/correct_test.txt"
	correct_test_x, correct_test_y = sequence_file_read(correct_test_file)
	fail_test_file = care_block_work_path + "/fail_test.txt"
	fail_test_x, fail_test_y = sequence_file_read(fail_test_file)
	

	total_test = sequence.pad_sequences(total_test_x, maxlen=max_review_length)
	correct_test = sequence.pad_sequences(correct_test_x, maxlen=max_review_length)
	fail_test = sequence.pad_sequences(fail_test_x, maxlen=max_review_length)
	
	# Final evaluation of the model
	total_scores = model.evaluate(total_test, total_test_y, verbose=0)
	correct_scores = model.evaluate(correct_test, correct_test_y, verbose=0)
	fail_scores = model.evaluate(fail_test, fail_test_y, verbose=0)
	#scores[1] useful, don't know what scores[0] is.
	return total_scores, correct_scores, fail_scores
#}}}

def sequence_file_read(sequence_file):
#{{{
	x = []
	y = []
	fl = open(sequence_file, "r")
	for line in fl.readlines():
		event_sequence = line.split()
		event_sequence_length = len(event_sequence)
		for i in range (0, len(event_sequence)):
			event_sequence[i] = int(event_sequence[i])
		learn_part = event_sequence[0: event_sequence_length - 2]
		x.append(learn_part)
		y.append(event_sequence[event_sequence_length - 1])
	fl.close()
	print x
	print y
	return x, y
#}}}

def LSTM_run_main (care_block_name, SMOTE_config):
#{{{
	care_block_work_path_name = care_block_name + "_work_path"
	SMOTE_config_sub_name = str(SMOTE_config[0]) + "_" + str(SMOTE_config[1]) + "_" + str(SMOTE_config[2])
	care_block_work_path = care_block_work_path_name + "/" + SMOTE_config_sub_name


	block_LSTM_model_train(care_block_work_path)
	total_scores, correct_scores, fail_scores = block_LSTM_model_test(care_block_work_path)
	
	print("total Accuracy: %.2f%%" % (total_scores[1]*100))
	print("correct Accuracy: %.2f%%" % (correct_scores[1]*100))
	print("fail Accuracy: %.2f%%" % (fail_scores[1]*100))
#}}}
#}}}

#TSM critical path
#block_TSM_sequence_pattern_detect
def block_TSM_sequence_pattern_detect (care_block_name):
#{{{
	care_block_work_path_name = care_block_name + "_work_path"
	correct_sequence_file_name = care_block_work_path_name + "/correct_sequences.txt"
	fail_sequence_file_name = care_block_work_path_name + "/fail_sequences.txt"
	#TSM only need to work once
	TSM_work_sub_path_name = care_block_work_path_name + "/TSM_path"
	if not os.path.isdir(TSM_work_sub_path_name):
		os.mkdir (TSM_work_sub_path_name)
	
	#correct TSM learn
	#########################################################
	#TSM_correct_work_sub_path_name = TSM_work_sub_path_name + "/correct"
	#if not os.path.isdir(TSM_correct_work_sub_path_name):
	#	os.mkdir (TSM_correct_work_sub_path_name)
	
	#correct_common_event_list = sequence_pattern_mining.sequence_list_common_block_summary(correct_sequence_file_name)
	#sequence_pattern_mining.common_event_list_store(correct_common_event_list, TSM_correct_work_sub_path_name + "/common_event_list.txt")	
	
	#sequence_list = sequence_pattern_mining.read_sequence_list_from_one_file(correct_sequence_file_name)
	#sequence_pattern_mining.TSM_on_sequence_list(sequence_list , TSM_correct_work_sub_path_name)
	#testing
	#sequence_pattern_mining.all_sub_path_test_on_sequences(sequence_list, TSM_correct_work_sub_path_name)


	#fail TSM learn
	#########################################################
	TSM_fail_work_sub_path_name = TSM_work_sub_path_name + "/fail"
	if not os.path.isdir(TSM_fail_work_sub_path_name):
		os.mkdir (TSM_fail_work_sub_path_name)
	
	#fail_common_event_list = sequence_pattern_mining.sequence_list_common_block_summary(fail_sequence_file_name)
	#sequence_pattern_mining.common_event_list_store(fail_common_event_list, TSM_fail_work_sub_path_name + "/common_event_list.txt")	
	
	sequence_list = sequence_pattern_mining.read_sequence_list_from_one_file(fail_sequence_file_name)
	sequence_pattern_mining.TSM_on_sequence_list(sequence_list , TSM_fail_work_sub_path_name)
	#testing
	sequence_pattern_mining.all_sub_path_test_on_sequences(sequence_list, TSM_fail_work_sub_path_name)

#}}}

def future_prediction (care_block_name, test_report_folder):
	care_block_work_path_name = care_block_name + "_work_path"
	care_block_critical_path_file = care_block_work_path_name + "/future_predict/critical_path.txt"
	care_block_LSTM_model_file = care_block_work_path_name + "/future_predict/LSTM_model.h5"
	need_test_file_list_file = care_block_work_path_name + "/future_predict/file_need_test.txt"

	#for critical_path
	fl = open (care_block_critical_path_file, "r")
	critical_path_line = fl.readline()
	critical_path = critical_path_line.split()
	#only use the first line in critical path file
	fl.close()

	#for test_file_list
	#this is only for test, in the future we don't need to focus on only a few files
	test_file_list = [] 
	fl = open(need_test_file_list_file, "r")
	for line in fl.readlines():
		line = line.replace("\n", "")
		test_file_list.append(test_report_folder + "/" + line)

	model = load_model(care_block_LSTM_model_file)

	#real time supervising
	#ARES very important!!!!!!!!!!!!!!!!!
	critical_path_pos = 0
	critical_path_look_forward_range = 4
	critical_path_length = len(critical_path)
	critical_path_start_event = critical_path[0]
	critical_path_finish_event = critical_path[critical_path_length - 1]
	for test_file in test_file_list:
		if not test_file == "150_180/153/153_c0-0c2s2n1.txt_block_report.txt":
			continue
		fl = open(test_file, "r")
		print "testing " + test_file
		event_list = []
		for line in fl.readlines():
			event = line.split()[0]
			event_list.append(event)
		fl.close()
		
		this_file_record_start_pos = -1 
		this_file_record_finish_pos = -1
		matched_sub_path = []
		now_predict = 0
		for event_list_pos in range (0, len(event_list)):
			if now_predict == 1:
				if event == care_block_name:
					print "predict occur correct!" + str(event_list_pos)
				
					now_predict = 0
				
					this_file_record_start_pos = -1 
					this_file_record_finish_pos = -1

			event = event_list[event_list_pos]
			#real time supervising feature add later
			if event == critical_path_start_event:
				this_file_record_start_pos = event_list_pos
			if event == critical_path_finish_event and not this_file_record_start_pos == -1:
				this_file_record_finish_pos = event_list_pos
				now_predict = 1

			if now_predict == 1:

				#ARES!!!!!!!!!!!!!!
				print "start " + str(this_file_record_start_pos)
				print "finish " + str(this_file_record_finish_pos)
				
				this_file_record_start_pos = 263 
				this_file_record_finish_pos = 278 
				
				LSTM_test_sequence = 	event_list[this_file_record_start_pos: this_file_record_finish_pos]

				LSTM_predict_correct = numpy.array([0])
				LSTM_predict_fail = numpy.array([1])
				
				new_event_sequence = []
				for event in LSTM_test_sequence:
					new_event_sequence.append(event_name_convert(event))

				total_test_x = []
				total_test_x.append(new_event_sequence)
				#print total_test_x

	
				total_test = sequence.pad_sequences(total_test_x, maxlen=max_review_length)
				correct_total_scores = model.evaluate(total_test, LSTM_predict_correct, verbose=0)
				fail_total_scores = model.evaluate(total_test, LSTM_predict_fail, verbose=0)
				print "predict correct " + str(correct_total_scores[1]*100)
				print "predict fail " + str(fail_total_scores[1]*100)
				now_predict = 0

		break
