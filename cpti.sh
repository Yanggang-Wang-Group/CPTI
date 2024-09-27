#!/bin/bash 
#PBS -l nodes=1:ppn=24
#PBS -e error.o
#PBS -o output.o
#PBS -q medium
#PBS -V 
#PBS -j oe 
NP=`cat $PBS_NODEFILE | wc -l`
cd $PBS_O_WORKDIR
JOB_NAME=cal
module load intel
module load vaspsol544
#----------------------------------------------------------------------
ulimit -s unlimited
echo "job ${JOB_NAME} starts at `date`" >${JOB_NAME}.out
echo "running on the following nodes, with $NP processes in total" >>${JOB_NAME}.out
cat $PBS_NODEFILE | sort | uniq -c >>${JOB_NAME}.out
echo "Start Time:" `date` > time

cpti noderun input.json > cptiout 2>&1

echo "END Time:" `date` >> time
date_end=`date "+%s"`
hour=`awk -v y=$date_start -v x=$date_end 'BEGIN {printf "%.2f\n",(x-y)/3600.0}'`
echo "Runing Time(h):" $hour "(h)">> time

module unload intel
module unload vaspsol544
