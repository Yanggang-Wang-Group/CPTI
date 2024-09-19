import os,logging,time,re,fileinput
from math import ceil
import numpy as np
def line_exacted(s_line,e_line):
	temp=''
	line_num=0
	str=fileinput.FileInput('POSCAR')
	for line in str:
		if line_num >= s_line and line_num <=e_line :
			temp +=line
		elif line_num >e_line:
			break
		line_num +=1
	return temp
def XDAR_read(n,relaxtion_step,interval,NBLOCK):
	index=-1
	xyz_coor=''
	for line in fileinput.FileInput('XDATCAR'):
		if line.split(' ')[0]!='':
			index += 1
			continue
		elif index == int((relaxtion_step+interval*n)/NBLOCK):
			xyz_coor += line
	return xyz_coor

def fix_dect():
	for line in fileinput.FileInput('POSCAR'):
		if re.match('^Selective' ,line):
			return True
		else:
			continue
	return False
def atom_num_get():
	number=0
	file=fileinput.FileInput('POSCAR')
	for line in file:
		if file.lineno()==7:
			number_list=line.split()
			break
	file.close()
	for i in range(len(number_list)):
		number += int(number_list[i])
	return number
def new_POSCAR_gene(n,relaxtion_time,interval,NBLOCK,atom):
	ret=''
	if fix_dect():
		head=line_exacted(0,7)
		head+='Direct \n'
		TF_boy=line_exacted(9, atom+8).split("\n")
		xyz_coor=XDAR_read(n,relaxtion_time,interval,NBLOCK).split("\n")
		for i in range(len(xyz_coor)-1):
			TF=TF_boy[i].split()
			if len(TF) == 6:
				ret +=xyz_coor[i]+' '+TF[-3]+' '+TF[-2]+' '+TF[-1]+ '\n'
			elif len(TF) == 7:
				ret +=xyz_coor[i]+' '+TF[-4]+' '+TF[-3]+' '+TF[-2]+' '+TF[-1]+ '\n'
		ret=head+ret
		return ret

	else :
		head=line_exacted(0,6)
		head+='Direct \n'
		xyz_coor=XDAR_read(n,relaxtion_time,interval,NBLOCK)
		ret=head+xyz_coor
		return ret
#NSW=re.findall('[0-9]+',os.system("sed -n '/^NSW/p' ./INCAR &" ))
#NBLCOK=re.findall('[0-9]+',os.system("sed -n '/^NBLOCK/p' ./INCAR &" ))
def INCAR_read(keyword):
	pass
	for line in fileinput.FileInput('INCAR'):
		if re.match('^%s'%keyword, line):
			key=float(re.findall('[0-9.]+',line)[0])
			break
		else :
			key=1
#       elif re.match('^NBLOCK',line):
#           NBLOCK=int(re.findall('[0-9]+',line)[0])
#       elif re.match('^POTIM',line):
#           POTIM=float(re.findall('[0-9.]+',line)[0])
	return key


dir_format='%02d'
'''
def bader_file_gene(step_path,para):
	NSW=INCAR_read('NSW')
	relax_time=para['relaxtion_time']
	interval=para['interval']
	dir_max=int(ceil(n_max/bader_each_time))
	n_max=int((NSW-relax_time)/interval)
	dir_index=0
	for i in range(dir_max):
		os.mkdir(os.path.join(step_path,dir_format %i))
	for i in range(n_max):
		if i%bader_each_time == 0:
			dir_index +=1
		bader_path=os.path.join(os.path.join(step_path,dir_format %dir_index),dir_format %i)
		ret=new_POSCAR_gene(i)
		with open(bader_path+'POSCAR'，'w') as fp :
			f.write(ret)
		sp_INCAR_gene(para)
		os.system('cp POTCAR KPOINTS %s'%bader_path)
	job_sub('iter_bader',para)

'''
