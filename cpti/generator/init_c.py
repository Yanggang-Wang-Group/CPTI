import os
from cpti import dlog

def gene_c(para):
	print("Oops! This function is under building，may release in the next version")
	
	os._exit(0) 



def init_c(args) :
	if args.PARAM :
		dlog.info ("start running")
		gene_c (args.PARAM)
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
