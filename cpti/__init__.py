import os
import logging
NAME="cpti"
SHORT_CMD="cpti"
dlog = logging.getLogger(__name__)
dlog.setLevel(logging.INFO)
dlogf = logging.FileHandler(os.getcwd()+os.sep+SHORT_CMD+'.log', delay=True)
dlogf_formatter=logging.Formatter('%(asctime)s - %(levelname)s : %(message)s')
#dlogf_formatter=logging.Formatter('%(asctime)s - %(name)s - [%(filename)s:%(funcName)s - %(lineno)d ] - %(levelname)s \n %(message)s')
dlogf.setFormatter(dlogf_formatter)
dlog.addHandler(dlogf)
__author__    = "Lv Xinmao"
__copyright__ = "Copyright 2022"
__status__    = "unrelease"
__version__ = '0.1.6'
__date__ = 'unknown'
def info():
	"""
		Show basic information about NAME, its location and version.
	"""
	print('software:cpti\n------------')
	print('Version: ' + __version__)
	print('Date:    ' + __date__)
	#print('Path:    ' + ROOT_PATH)
	print('')
	print('Dependency')
	print('------------')
	for modui in ['numpy','ase']:
		try:
			mm = __import__(modui)
			print('{} {}   {}'.format(modui, mm.__version__, mm.__path__[0]))
		except ImportError:
			print('{}}   {} Nowhere or not installed' % (modui, ''))
		except AttributeError:
			print('{}}   {} Unknown version' %(modui, ''))
	print()

	# reference
	print("Please cite: J. Phys. Chem. Lett. 2024, 15, 5, 1314–1320")
