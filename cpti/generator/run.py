import os
import sys,re
import argparse
import json
import logging
import logging.handlers
import time
from cpti import dlog
from cpti.generator.pathfinder import make_iter_path,make_step_path,gene_path_name,make_multi_path,make_path
from cpti.generator.generator import step_rec,step_log,keyword_replace,keyword_exract
from cpti.generator.iter_bader import INCAR_read,new_POSCAR_gene,atom_num_get
from cpti.generator.V_cal import V_cal,get_xyz,V2N
from cpti.dispatcher.Dispatcher import job_sub,head_gene,body_gene,tail_gene
from math import ceil

def finish_check():
	return (os.path.exists('./tag_finished'))
def get_average(list):
	sum = 0
	for item in list:
		sum += item
	return sum/len(list)
def correction(V_true,V_cal,Capacitance):
	xyz=get_xyz()
	Ncorr=-(((V_true-V_cal)*Capacitance*xyz[0]*xyz[1]*1e-3)/1.6)
	return Ncorr
def temp1(file):
	with open('%s'%file, 'r') as file:
		# 逐行读取文件内容
		for line in file:
			# 检查每一行是否包含参数变量
			if re.match(r'^NELECT',line):
				value=line.split('=')[1].strip()
				return value
def init_MD(iter_num,para,nodetag):
	raw_path=para['work_path']
	vasp_file=para['vasp_file_location']
	set_potential=para['set_potential']
	iter_path=make_iter_path(iter_num,raw_path)
	step_path=make_step_path(iter_path,'init_MD')
	os.chdir(step_path)
	if os.path.exists(vasp_file) and iter_num==0:
		os.system("cp %s/* %s/" %(vasp_file,step_path))
	elif os.path.exists(vasp_file) and iter_num!=0:
		os.system("cp %s/* %s/" %(vasp_file,step_path))
		last_iter_path=make_iter_path(int(iter_num)-1,raw_path)
		last_step_path=make_step_path(last_iter_path,'init_MD')
		os.system("cp %s/CONTCAR %s/POSCAR" %(last_step_path,step_path) )
	else : raise Exception('vasp file cannot find ,please check again')
	para['Nset'] += para['corr']
	keyword_replace('NELECT', str(para['Nset']), os.path.join(step_path,'INCAR'))
	keyword_replace('LBLUEOUT', '.TRUE.', os.path.join(step_path,'INCAR'))
	dlog.info('iter.%03d init_MD is calculating' %iter_num)
	job_sub('iter_MD',para,iter_num,1,nodetag)
	while not finish_check() :
		time.sleep(60)
	dlog.info('iter.%03d init_MD  finished' %iter_num)
def init_bader(iter_num,para,nodetag):
	raw_path=para['work_path']
	vasp_file=para['vasp_file_location']
	iter_path=make_iter_path(iter_num,raw_path)
	step_path=make_step_path(iter_path,'init_MD')
	os.chdir(step_path)
	dlog.info('bader_file is generating' )
	sub_para=para['iter_bader']
	bader_each_file=sub_para['bader_each_file']
	relax_step=sub_para['relaxtion_step']
	TI_tag_path=os.path.join(os.path.join(raw_path,gene_path_name(iter_num-1)),'V_calculate/TI_tag')
	if not os.path.exists(TI_tag_path):
		interval=sub_para['interval']
	else:
		interval=sub_para['interval-TI']
	iter_path=os.path.join(raw_path,gene_path_name(iter_num))
	step_path=make_step_path(iter_path,'init_bader')
	NSW=INCAR_read('NSW')
	NBLOCK=INCAR_read('NBLOCK')
	n_max=int((NSW-relax_step)/interval)
	if nodetag:
		bader_each_file = n_max + 1
		dlog.info('work on node, bader_each_file will be neglected')
	dir_max=int(ceil(n_max/bader_each_file))
	atom=atom_num_get()
	dir_index=0
	dir_format='%02d'
	make_multi_path(step_path,dir_max)
	for i in range(n_max):
		if i%bader_each_file == 0 :
			dir_index +=1 if i!=0 else 0
			sub_file_path=os.path.join(step_path, dir_format %dir_index)
			bader_path=os.path.join(sub_file_path,dir_format %i)
			make_path(bader_path)
			if not nodetag:
				with open(sub_file_path+'/mission.sub','a+') as fp :
					fp.write(head_gene(sub_para))
					fp.write(body_gene(dir_format %i ,sub_para))
					fp.write(tail_gene(sub_para)) if (i+1)==n_max else 0
			else:
				with open(sub_file_path+'/mission.sub','a+') as fp :	
					fp.write(body_gene(dir_format %i ,sub_para))
					fp.write(tail_gene(sub_para)) if (i+1)==n_max else 0					
		else :
			sub_file_path=os.path.join(step_path, dir_format %dir_index)
			bader_path=os.path.join(sub_file_path,dir_format %i)
			make_path(bader_path)
			with open(sub_file_path+'/mission.sub','a+') as fp :
				fp.write(body_gene(dir_format %i,sub_para))
				fp.write(tail_gene(sub_para)) if (i+1)%bader_each_file==0 or (i+1)==n_max else 0
		ret=new_POSCAR_gene(i,relax_step,interval,NBLOCK,atom) 
		with open(bader_path+'/POSCAR','w') as fp :
			fp.write(ret)
		os.system('cp POTCAR KPOINTS %s'%bader_path)
		os.system('cp ./INCAR-bader %s/INCAR '%bader_path)
		keyword_replace('NELECT', temp1('INCAR'), os.path.join(bader_path,'INCAR'))
	dlog.info('bader file generation complete' )
	dlog.info('-----iter.%03d init_bader starts-----' %iter_num)
	os.chdir(step_path)
	job_sub('iter_bader',para,iter_num,dir_max,nodetag)
	for i in range(dir_max) :
		os.chdir(os.path.join(step_path,dir_format %i))
		while not finish_check() :
			time.sleep(30)
		dlog.info('iter.%03d init_bader file_%02d finished' %(iter_num,i))
		os.chdir(os.path.dirname(os.getcwd()))
def do_ti(iter_num,para,nodetag):
	raw_path=para['work_path']
	iter_path=make_iter_path(iter_num,raw_path)
	raw_path=para['work_path']
	iter_path=os.path.join(raw_path,gene_path_name(iter_num))
	last_iter_path=os.path.join(raw_path,gene_path_name(iter_num-1))
	POSCAR_path=os.path.join(last_iter_path,'init_MD')
	TI_path=make_step_path(iter_path,'init_MD')
	os.chdir(TI_path)
	try:
		os.system('cp %s/CONTCAR %s/POSCAR '%(POSCAR_path,TI_path))
		os.system('cp %s/KPOINTS %s/POTCAR %s/INCAR %s/ICONST %s/INCAR-bader %s/ '\
			%(POSCAR_path,POSCAR_path,POSCAR_path,POSCAR_path,POSCAR_path,TI_path))
	except:
		print('the MD_traj does not exists in the path %s\n plz check your file \n'%(POSCAR_path))
		raise Exception(' ')
	keyword_replace('LBLUEOUT', '.TRUE.', os.path.join(TI_path,'INCAR'))
	keyword_replace('NSW', str(para['TI_step']), os.path.join(TI_path,'INCAR'))
	job_sub('iter_MD',para,iter_num,1,nodetag)
	while not finish_check() :
		time.sleep(60)


def V_calculate(iter_num,para):
	raw_path=para['work_path']
	sub_para=para['V_calculate']
	iter_path=os.path.join(raw_path,gene_path_name(iter_num))
	bader_path=os.path.join(iter_path,'init_bader')
	step_path=make_step_path(iter_path,'V_calculate')
	V_path=os.path.join(os.path.join(raw_path,gene_path_name(iter_num)),'V_calculate')
	TI_tag_path=os.path.join(os.path.join(raw_path,gene_path_name(iter_num-1)),'V_calculate/TI_tag')
	Capacitance=float(sub_para['Capacitance'])
	PZC=float(sub_para['PZC'])
	surface_atom=sub_para['surface_atom']
	#if sub_para['is_metal_surf']:
		#V_ave=0.5*get_average(V_cal(bader_path,Capacitance,PZC,surface_atom))
	#else:
	V_list=V_cal(bader_path,Capacitance,PZC,surface_atom)
	with open(V_path+'/V.dat','a+') as fp :
		for i in range(len(V_list)):
			fp.write( str(i+1) + ',' + str(V_list[i]) + '\n' )
	V_ave=get_average(V_list)
	if abs(V_ave-float(para['set_potential'])) <float(para['convergence']):
		os.chdir(step_path)
		if not os.path.exists(TI_tag_path):
			dlog.info('current potential is %f V, reached the precision of setting %s'%(V_ave,para['convergence']))
			dlog.info('start to do TI!')
			os.system('touch TI_tag')
		else:
			dlog.info('after bader checking, the average potential has reached the convergence, workflow finish.')
			dlog.info('current potential is %f V, CPTI reach the precision of setting %s'%(V_ave,para['convergence']))
			os._exit(0) 

	elif iter_num==para['max_iter']:
		dlog.info('reach the max iter times , quitting.....')
		dlog.info('the V value may not converge, please check your iteration file')
		dlog.info('done!')
		os._exit(0) 

	else:
		Ncorr=correction(para['set_potential'],V_ave,Capacitance)
		dlog.info('iter %03d task V_calculate result in the V=%s ,recalulating......'%(iter_num,V_ave))
		dlog.info('still not reach the setting V=%s ,recalulating......'%(para['set_potential']))
		dlog.info('the NELECT correction is %f'%Ncorr)
		para['corr']=Ncorr

def run_iter(param_file,nodetag): 
	try:
		with open (param_file, 'r') as fp :
			para = json.load (fp)
	except:
		raise Exception('unreadfile input file , please check your input')
	os.chdir(para['vasp_file_location'])
	recordfile=os.path.join(para['work_path'],"step.record")
	#restart module
	raw_path=para['work_path']
	restart=False
	para['corr'] = float(0)
	if os.path.exists(recordfile):
		with open(recordfile, "r") as f:
			lines = f.readlines()
			vectors = [list(map(int, line.split())) for line in lines]
			ii = vectors[-1][0]
			record_step = vectors[-1][1]+1
			restart=True
			para['Nset'] = float(keyword_exract('NELECT',os.path.join(os.path.join(raw_path,gene_path_name(ii)),'init_MD/INCAR')))
		dlog.info ("detect the record file , CPTI will restart from iter %s %s"%(ii,record_step))
	else:
		ii = 0
		para['Nset'] = float(V2N(para))
	##excate old NELECT
	max_tasks=3
	index=True
	while index:
		for jj in range (max_tasks) :
			if restart and jj<record_step:
				continue
			restart=False
			if jj == 0 :
				if os.path.exists(os.path.join(os.path.join(raw_path,gene_path_name(ii-1)),'V_calculate/TI_tag')):
					do_ti(ii, para,nodetag)
				else:
					step_log ("init_MD", ii, jj) 
					step_rec(recordfile,ii,jj)
					init_MD (ii, para,nodetag)
			elif jj == 1 :
				step_log ("init_bader", ii, jj) 
				step_rec(recordfile,ii,jj)
				init_bader (ii, para,nodetag)
			elif jj == 2 :
				step_log ("V_calculate", ii, jj)
				step_rec(recordfile,ii,jj)
				V_calculate (ii,para)
		ii += 1
def gene_run(args) :
	if args.PARAM :
		dlog.info ("start running")
		run_iter (args.PARAM,False)
		dlog.info ("finished")

def gene_noderun(args) :
	if args.PARAM :
		dlog.info ("start running")
		run_iter (args.PARAM,True)
		dlog.info ("finished")

def _main () :
	parser = argparse.ArgumentParser()
	parser.add_argument("PARAM", type=str,
						help="The parameters of the generator")
	args = parser.parse_args()
	logging.basicConfig (level=logging.INFO, format='%(asctime)s %(message)s')
	# logging.basicConfig (filename="compute_string.log", filemode="a", level=logging.INFO, format='%(asctime)s %(message)s')
	logging.getLogger("paramiko").setLevel(logging.WARNING)
	logging.info ("start running")
	run_iter (args.PARAM)
	logging.info ("finished!")
	