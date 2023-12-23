import os,json,time
from cpti.dispatcher.LSF import LSF_sub,LSF_head_gene,LSF_body_gene,LSF_tail_gene
from cpti.dispatcher.PBS import PBS_sub,PBS_head_gene,PBS_body_gene,PBS_tail_gene
from cpti import dlog
#from dispatcher.PBS import PBS_sub
def sub_generator(sub_para):
	if sub_para['queue_system']=='LSF' :
		LSF_sub(sub_para)
	elif sub_para['queue_system']=='PBS' :
		PBS_sub(sub_para)

#####design for iter_bader#####
def head_gene(sub_para):
	if sub_para['queue_system']=='LSF' :
		ret=LSF_head_gene(sub_para)
	elif sub_para['queue_system']=='PBS' :
		ret=PBS_head_gene(sub_para)
	return ret
def body_gene(file_name,sub_para):
	if sub_para['queue_system']=='LSF' :
		ret=LSF_body_gene(file_name,sub_para)
	elif sub_para['queue_system']=='PBS' :
		ret=PBS_body_gene(file_name,sub_para)
	return ret
def tail_gene(sub_para):
	if sub_para['queue_system']=='LSF' :
		ret=LSF_tail_gene()
	elif sub_para['queue_system']=='PBS' :
		ret=PBS_tail_gene()
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
def job_sub(job_type,para,iter_num,dir_num=1):
	dir_format='%02d'
	if job_type=='iter_MD':
		sub_para=para['iter_MD']
		ret=sub_generator(sub_para)
	elif job_type=='iter_bader':
		sub_para=para['iter_bader']
		for i in range(dir_num):
			do_sub(sub_para,dir_format %i)
			dlog.info('iter.%03d init_bader file_%02d is calculating' %(iter_num,i))

