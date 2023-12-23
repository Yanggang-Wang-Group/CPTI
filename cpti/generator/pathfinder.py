#!/usr/bin/env python3

import os, re, shutil, logging
import glob
from cpti import dlog
iter_format = "%06d"
dir_format='%02d'
def gene_path_name (iter_index) :
	return "iter." + (iter_format % iter_index)
def make_iter_path(iter_name,work_path):
	name=gene_path_name(iter_name)
	whole_path=os.path.join(work_path,name)
	if os.path.exists(whole_path)!=1:
		os.mkdir(whole_path)
	else :
		pass
		#dlog.info ('%s path exists! Old file may be covered.' %whole_path)
	return whole_path
def make_step_path(iter_path,step_path):
	whole_path=os.path.join(iter_path,step_path)
	if os.path.exists(whole_path)!=1:
		os.mkdir(whole_path)
	else :
		pass
		#dlog.info ('%s path exists! Old file may be covered.' %whole_path)
	return whole_path
def make_path(path):
	if os.path.exists(path)!=1:
		os.mkdir(path)
	else :
		dlog.info ('%s path exists! Old file may be covered.' %path)
def make_multi_path(path,dir_max):
	for i in range(dir_max):
		if os.path.exists(os.path.join(path,dir_format %i))!=1:
			os.mkdir(os.path.join(path,dir_format %i))
		else :
			dlog.info ('%s path exists! \n Old file may be covered.' %os.path.join(path,dir_format %i))
