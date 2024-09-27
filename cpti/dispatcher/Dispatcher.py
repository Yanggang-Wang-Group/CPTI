import os,json,time
from cpti.dispatcher.LSF import LSF_sub,LSF_head_gene,LSF_body_gene,LSF_tail_gene
from cpti.dispatcher.PBS import PBS_sub,PBS_head_gene,PBS_body_gene,PBS_tail_gene
from cpti.dispatcher.Slurm import Slurm_sub,Slurm_head_gene,Slurm_body_gene,Slurm_tail_gene
from cpti.dispatcher.Onnode import Onnode_sub
from cpti import dlog
import subprocess

def finish_check():
	return (os.path.exists('./tag_finished'))

def sub_generator(sub_para,nodetag):
	if nodetag:
		Onnode_sub(sub_para)
	else:
		if sub_para['queue_system']=='LSF' :
			LSF_sub(sub_para)
		elif sub_para['queue_system']=='PBS' :
			PBS_sub(sub_para)
		elif sub_para['queue_system']=='Slurm' :
			Slurm_sub(sub_para)
#####design for iter_bader#####
def head_gene(sub_para):
	if sub_para['queue_system']=='LSF' :
		ret=LSF_head_gene(sub_para)
	elif sub_para['queue_system']=='PBS' :
		ret=PBS_head_gene(sub_para)
	elif sub_para['queue_system']=='Slurm' :
		ret=Slurm_head_gene(sub_para)
	return ret
def body_gene(file_name,sub_para):
	if sub_para['queue_system']=='LSF' :
		ret=LSF_body_gene(file_name,sub_para)
	elif sub_para['queue_system']=='PBS' :
		ret=PBS_body_gene(file_name,sub_para)
	elif sub_para['queue_system']=='Slurm' :
		ret=Slurm_body_gene(file_name,sub_para)
	return ret
def tail_gene(sub_para):
	if sub_para['queue_system']=='LSF' :
		ret=LSF_tail_gene()
	elif sub_para['queue_system']=='PBS' :
		ret=PBS_tail_gene()
	elif sub_para['queue_system']=='Slurm' :
		ret=Slurm_tail_gene()
	return ret
def do_sub(sub_para,dir_index):
	if sub_para['queue_system']=='LSF' :
		os.chdir('./%s'%dir_index)
		os.system('bsub -J %s < ./mission.sub &'%('cpti'))
		os.chdir(os.path.dirname(os.getcwd()))
	elif sub_para['queue_system']=='PBS' :
		os.chdir('./%s'%dir_index)
		os.system('qsub -N %s  ./mission.sub & '%('cpti' ))
		os.chdir(os.path.dirname(os.getcwd()))
	elif sub_para['queue_system']=='Slurm' :
		os.chdir('./%s'%dir_index)
		os.system('sbatch ./mission.sub &')
		os.chdir(os.path.dirname(os.getcwd()))

def job_sub(job_type,para,iter_num,dir_num,nodetag):
	dir_format='%02d'
	if job_type=='iter_MD':
		sub_para=para['iter_MD']
		ret=sub_generator(sub_para,nodetag)
	elif job_type=='iter_bader':
		sub_para=para['iter_bader']
		for i in range(dir_num):
			dir_index = dir_format %i
			if nodetag:
				os.chdir('./%s'%dir_index)
				with open('mission.sub','r') as f:
					mission=f.read()
				os.system(mission)
				os.chdir(os.path.dirname(os.getcwd()))
				dlog.info('iter.%03d init_bader file_%02d is calculating' %(iter_num,i))
			else:
				do_sub(sub_para,dir_index)
				dlog.info('iter.%03d init_bader file_%02d is calculating' %(iter_num,i))

