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
	_default_item(res, 'job_name', 'cpti')
	_default_item(res, 'qos', '')
	_default_item(res, 'account', '')
	return res
def sub_head_gene(res):
	ret=''
	ret +="#!/bin/bash \n"
	if res['gpu_switch']==0:
		ret +='#SBATCH -ntasks=%d\n#SBATCH -ntasks-per-node=%d\n' %(res['core_per_task'],res['core_per_task'])
	if res['set_mem'] > 0 :
		ret += "#SBATCH --mem=%dG \n" % res['set_mem']
	if len(res['queue_type']) > 0 :
		ret += '#SBATCH --partition=%s\n' % res['queue_type']
	if len(res['account']) > 0 :
		ret += "#SBATCH --account=%s \n" % res['account']
	if len(res['qos']) > 0 :
		ret += "#SBATCH --qos=%s \n" % res['qos']
	ret += "#SBATCH --nodes=%d \n" % res['numb_node']
	ret += "#SBATCH --job-name=%s \n" %(res['job_name'])
	ret += '#SBATCH --output=output.log\n'
	for ii in res['module_list'] :
		ret += "module load %s\n" % ii
	ret += "\n"
	for ii in res['source_list'] :
		ret += "source %s\n" %ii
	ret += "\n"
	for flag in res.get('custom_flags', []):
		ret += '%s \n' % flag
	ret += "\n"
	ret += 'srun hostname -s | sort -n > slurm.hosts\n'
	ret += 'NP=`cat slurm.hosts | wc -l`\n'
	return ret
def sub_mission_gene(res,ret):
	if res['snapshot_exacted']==0:
		ret += 'if [ ! -f ./tag_finished ] ;then \n'
		ret += 'mpiexec.hydra -np %d %s > stdout  2>&1\n' %(
			res['core_per_task'],res['vasp_path'])
		ret += 'if test $? -ne 0; then touch tag_failure; fi \n'
		ret +='touch tag_finished\n'
		ret +='fi\n'
	return ret
def bader_body_gene(res,file_name):
	ret=''
	ret += 'if [ ! -f ./%s/tag_finished ] ;then \n'%file_name
	ret += 'cd %s \n'%file_name
	ret += 'mpiexec.hydra -np %d %s > stdout 2>&1\n' %(
		res['core_per_task'],res['vasp_path'])
	ret += 'if test $? -ne 0; then touch tag_failure; fi \n'
	ret += 'chgsum.pl AECCAR0 AECCAR2 \n'
	ret += 'bader CHGCAR -ref CHGCAR_sum \n'
	ret += 'touch tag_finished\n'
	ret += 'rm CHGCAR\n'
	ret += 'cd .. \n'
	ret += 'fi\n'
	ret += '\n'
	return ret
def Slurm_tail_gene():
	ret = "rm -rf slurm.hosts\n"
	ret +='touch tag_finished'
	ret += '\n'
	return ret
def Slurm_head_gene(res=None):
	res=init_head(res)
	ret=sub_head_gene(res)
	return ret
def Slurm_body_gene(file_name,res):
	res=init_head(res)
	ret=bader_body_gene(res,file_name)
	return ret
def Slurm_gene(res=None):
	res=init_head(res)
	ret=sub_head_gene(res)
	ret=sub_mission_gene(res,ret)
	return ret
def Slurm_sub(res):
	ret=Slurm_gene(res)
	with open('mission.sub','w+') as file:
		file.write(ret)
	os.system('sbatch mission.sub')

