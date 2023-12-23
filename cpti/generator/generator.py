import os,logging,re
import fileinput
iter_format = "%06d"
task_format = "%02d"
log_iter_head = "iter " + iter_format + " task " + task_format + ": "
def step_log (task, ii, jj) :
	logging.info ((log_iter_head + "%s") % (ii, jj, task))
def step_rec(record,ii,jj):
	with open (record, "a") as frec :
		frec.write ("%d %d\n" % (ii, jj)) 
def keyword_replace(keyword,key,path):
	index=0
	file = fileinput.FileInput(path, inplace=True)
	for line in file :
		if re.match('^%s'%keyword, line):
			key_old=line.split('=')[1]
			print(line.replace(key_old, key))
			index += 1
			continue
		print(line,end='')
	file.close()
	if index==0:
		with open (path,'a+') as fp:
			fp.write(keyword+'='+key+'\n')
def keyword_exract(keyword,path):
    with open(path, 'r') as file:
        for line in file:
            if re.match('^%s'%keyword, line):
                value = line.split('=')[1].strip()
                return float(value)
    return None