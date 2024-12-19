from ast import Num
import os
import os.path 
import numpy as np 
import fileinput
import re
import glob
from cpti.generator.iter_bader import atom_num_get
from cpti.generator.generator import keyword_exract
def statelem():
	file=fileinput.FileInput('POSCAR')
	for line in file:
		if file.lineno()==6 :
			element=line.split()
		elif file.lineno()==7 :
			index=np.asarray((line.split()),dtype='int')
		else :
			continue
	file.close()
	for i in range(1,len(index)):
		index[i]=index[i]+index[i-1]
	#a=np.asarray(zip(index,element))
	indexf=dict(zip(element,index))
	#返回一个元素的list和字典对应的indexf
	return element,indexf
def getzval(element):
	a=[]
	file=fileinput.FileInput('POTCAR')
	for line in file:
		if re.search('ZVAL',line):
			temp=line.split()
			a.append((temp[5]))
	a=dict(zip(element,a))
	file.close()
	#返回一个字典对应元素的zval值
	return a
#atomnum=input("input the Surface atomic number(eg.1-122,128-130)\n")
def sort(atomnum):
	atomnumber=[]
	if re.search(",", atomnum):
		temp=atomnum.split(",")
		length=len(temp)
		for i in range(0,length):
			a=(temp[i].split('-'))
			atomnumber.extend(range(int(min(a)),int(max(a))+1))
			atomnumber.sort()
	else:
		atomnum=np.asarray(atomnum.split("-"),dtype='int')
		atomnumber.extend(range(min(atomnum),max(atomnum)+1))
	#对输入的原子进行整理，返回原子数
	return atomnumber
#   for i in range(0,length):
def cal_std(atomnum, zval,element,index):
	elem_std=[]
	ele_std=0
	i,j=0,0
	num_elem=np.zeros(len(element))
	while i < len(atomnum):
		if atomnum[i] <= index[element[j]]:
			num_elem[j] += 1
			i += 1
		else:
			j += 1
	for i in range(0,len(element)):
		ele_std=ele_std+num_elem[i]*int(float(zval[element[i]]))
	return ele_std
def calele(atomnum, zval,element,index):
	ele_bdr=0
	ele_std=cal_std(atomnum, zval, element, index)
	file=fileinput.input('ACF.dat')
	for line in file:
		if ((fileinput.lineno()-2) in atomnum):
			temp=np.asarray(line.split(),dtype='float64')
			ele_bdr=ele_bdr+temp[4]
	bader=ele_std-ele_bdr
	file.close()
	return bader
def get_xyz():
	xyz=[]
	file=fileinput.FileInput('POSCAR')
	for line in file:
		if file.lineno()<6 and file.lineno()>2:
			a=line.split()
			xyz.append(float(a[file.lineno()-3]))
		elif  file.lineno()>6:
			break
	file.close()
	return xyz
def Ucalc(bader_sur,PZC:float=0.0,C:float=21.0):
	xyz=np.array([0,0,0],dtype='float64')
	xyz=get_xyz()
	C=1/C*pow(10,2)
	p=16*bader_sur/(xyz[0]*xyz[1])
	return C*p+PZC
def V2N(para):
	sub_para=para['V_calculate']
	Capacitance=float(sub_para['Capacitance'])
	PZC=float(sub_para['PZC'])
	element,index=statelem()
	atomnum=range(1,atom_num_get()+1)
	zval=getzval(element)
	xyz=get_xyz()
	ele_std=cal_std(atomnum, zval, element, index)
	Nbias=-(Capacitance*(para['set_potential']-PZC)*1e-3)*(xyz[0]*xyz[1])/1.6
	return (Nbias+ele_std)
def V_cal(step_path,Capacitance,PZC,surface_atom):
	link=os.path.join(step_path,'[0-9][0-9]/[0-9][0-9]')
	V_value,bader_sur=[],[]
	for i in glob.glob(link):
		os.chdir(i)
		element,index=statelem()
		atomnum=sort(surface_atom)
		zval=getzval(element)
		bader_sur1 = calele(atomnum,zval,element,index)
		bader_sur.append(bader_sur1)
		V_value.append(Ucalc(bader_sur1,PZC,Capacitance))
	return V_value,bader_sur

def get_Nbias(para,iter_path):
	MD_path = os.path.join(iter_path,'init_MD','INCAR')
	element,index=statelem()
	atomnum=range(1,atom_num_get()+1)
	zval=getzval(element)
	ele_std=cal_std(atomnum, zval, element, index)
	N_now=float(keyword_exract('NELECT',MD_path))
	N_bias = N_now - ele_std
	return N_bias
	

def correction(V_true,V_cal,Capacitance,record_path,iternum):
	bias,bader_sur = [],[]
	with open(record_path,'r') as fp:
		for line in fp:
			temp = line.split()
			bias.append(float(temp[0]))
			bader_sur.append(float(temp[1]))
	bias = np.array(bias)
	bader_sur = np.array(bader_sur)
	if iternum == 0 or iternum == 1:
		b = 0
                try:
		   k = float(sub_para['init_k'])
		   dlog.info("User defined init_k:%f"(k))
		except:
			k = bader_sur[0] / bias[0]
			R2 = 1
	else:
		fit = np.polyfit(bias,bader_sur,1)
		k = fit[0]
		b = fit[1]
		linear = np.poly1d(fit)
		bader_fit = linear(bias)
		bader_mean = np.mean(bader_sur)
		ss_res = np.sum((bader_sur - bader_fit) ** 2)
		ss_tot = np.sum((bader_sur - bader_mean) ** 2)
		R2 = 1 - (ss_res / ss_tot)
	xyz=get_xyz()
	Ndiff = (((V_true-V_cal)*Capacitance*xyz[0]*xyz[1]*1e-3)/1.6)
	Ncorr = (Ndiff)/k
	return Ncorr,k,b,R2
