import os,time
def _default_item(resources, key, value) :
	if key not in resources :
		resources[key] = value
def init_head(res_):
	if res_ == None :
		res = {}
	else:
		res = res_
	_default_item(res, 'numb_node', 1)
	_default_item(res, 'gpu_switch', 0)
	_default_item(res, 'core_per_task', 24)
	_default_item(res, 'queue_type', '')
	_default_item(res, 'license_list', [])
	_default_item(res, 'exclude_list', [])
	_default_item(res, 'module_unload_list', [])
	_default_item(res, 'module_list', [])
	_default_item(res, 'source_list', [])
	_default_item(res, 'with_mpi', False)
	_default_item(res, 'snapshot_exacted', 0)
	return res

def sub_mission_gene(res):
	if res['snapshot_exacted']==0:
		ret = 'if [ ! -f ./tag_finished ] ;then \n'
		ret += 'mpiexec.hydra -machinefile $PBS_NODEFILE -np %d %s > stdout  2>&1\n' %(
			res['core_per_task'],res['vasp_path'])
		ret += 'if test $? -ne 0; then touch tag_failure; fi \n'
		ret +='touch tag_finished\n'
		ret +='fi'
		ret += "\n"
	return ret

# def bader_body_gene(res,file_name):
# 	ret = 'if [ ! -f ./%s/tag_finished ] ;then \n'%file_name
# 	ret += 'cd %s \n'%file_name
# 	ret += 'mpiexec.hydra -machinefile $PBS_NODEFILE -np %d %s > stdout 2>&1\n' %(
# 		res['core_per_task'],res['vasp_path'])
# 	ret += 'if test $? -ne 0; then touch tag_failure; fi \n'
# 	ret += 'chgsum.pl AECCAR0 AECCAR2 \n'
# 	ret += 'bader CHGCAR -ref CHGCAR_sum \n'
# 	ret += 'touch tag_finished\n'
# 	ret += 'rm CHGCAR\n'
# 	ret += 'cd .. \n'
# 	ret += 'fi'
# 	ret += '\n'
# 	return ret

# def Onnode_body_gene(res,filename):
# 	res=init_head(res)
# 	ret=bader_body_gene(res,filename)
# 	return ret

def Onnode_gene(res=None):
	res=init_head(res)
	ret=sub_mission_gene(res)
	return ret

def Onnode_sub(res):
	ret=Onnode_gene(res)
	os.system(ret)

