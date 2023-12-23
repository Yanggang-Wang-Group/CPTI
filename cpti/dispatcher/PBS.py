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
def sub_head_gene(res):
    ret=''
    ret +="#!/bin/bash \n"
    if res['gpu_switch']==0:
        ret += '#PBS -l nodes=%s:ppn=%s\n' %(
            res['numb_node'] ,res['core_per_task'])
    ret  += '#PBS -e error.o\n#PBS -o output.o\n'
    if res['set_mem'] > 0 :
        ret += "#PBS -M %d \n" % (res['set_mem'])
    if len(res['queue_type']) > 0 :
        ret += '#PBS -q %s\n' % res['queue_type']
    ret += '#PBS -V \n'
    ret += '#PBS -j oe \n'
    ret += 'NP=`cat $PBS_NODEFILE | wc -l`\n'
    ret += 'cd $PBS_O_WORKDIR\n'
    ret += 'JOB_NAME=cal\n'
    for ii in res['module_list'] :
        ret += "module load %s\n" % ii
    ret += "\n"
    for ii in res['source_list'] :
        ret += "source %s\n" %ii
    ret += "\n"
    return ret
def sub_mission_gene(res,ret):
    if res['snapshot_exacted']==0:
        ret += 'if [ ! -f ./tag_finished ] ;then \n'
        ret += 'mpiexec.hydra -machinefile $PBS_NODEFILE -np %d %s > stdout  2>&1\n' %(
            res['core_per_task'],res['vaspsol_path'])
        ret += 'if test $? -ne 0; then touch tag_failure; fi \n'
        ret +='touch tag_finished\n'
        ret +='fi'
        ret += "\n"
    return ret
def bader_body_gene(res,file_name):
    ret=''
    ret += 'if [ ! -f ./%s/tag_finished ] ;then \n'%file_name
    ret += 'cd %s \n'%file_name
    ret += 'mpiexec.hydra -machinefile $PBS_NODEFILE -np %d %s > stdout 2>&1\n' %(
        res['core_per_task'],res['vaspsol_path'])
    ret += 'if test $? -ne 0; then touch tag_failure; fi \n'
    ret += 'chgsum.pl AECCAR0 AECCAR2 \n'
    ret += 'bader CHGCAR -ref CHGCAR_sum \n'
    ret += 'touch tag_finished\n'
    ret += 'rm CHGCAR\n'
    ret += 'cd .. \n'
    ret += 'fi'
    ret += '\n'
    return ret
def PBS_tail_gene():
    ret='touch tag_finished'
    ret += '\n'
    return ret
def PBS_head_gene(res=None):
    res=init_head(res)
    ret=sub_head_gene(res)
    return ret
def PBS_body_gene(file_name,res):
    res=init_head(res)
    ret=bader_body_gene(res,file_name)
    return ret
def PBS_gene(res=None):
    res=init_head(res)
    ret=sub_head_gene(res)
    ret=sub_mission_gene(res,ret)
    return ret
def PBS_sub(res):
    ret=PBS_gene(res)
    with open('mission.sub','w+') as file:
        file.write(ret)
    os.system('qsub -N %s  mission.sub'%('cpti'))

