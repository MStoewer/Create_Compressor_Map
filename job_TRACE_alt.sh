#!/bin/bash
###############################################################################
###                              job_TRACE.sh                               ###
###       start vom run-directory auf dem RRZN mit TRACE 9.1       	    ###
###                      10 July 2009 Florian Herbst                        ###
###                   modified by Hendrik Seehausen Mar 2019                ###
###############################################################################
JOBNAME="REPLACE_JOB"
EMAIL="m.stoewer@stud.uni-hannover.de"
NODES="REPLACE_NODES"
NPROCS="REPLACE_CPUS"
MEMORY="REPLACE_MEM"
QUEUE="all"
WALLTIME="12:00:00"



################################################################################
#DON'T CHANGE PART BELOW
################################################################################
BASENAME="TRACE.cgns"
CONTROLFILE="TRACE_control.input"

#BALANCE FILE VIA PREP ESRTELLEN (dazu wird Umgebung von Schumacher geladen)
let CPUS=($NPROCS \* $NODES)
source /home/nhkcssch/load_trace_env.sh
module load prep/9.1.538.TFD.0

BALANCE_FILE="BALANCE_"$CPUS"PROC"

RUNDIR=$PWD
echo $CPUS
#
cd ../
WORKDIR=$PWD
cd input/
PREP -cgns $BASENAME -clb -np $CPUS

#Argumente an MPI(Parallelisierung) übergeben: bind-to core sinnvoll, sobald Knoten nicht komplett ausgelastet wird
MPIARGS="-x PATH -x LD_LIBRARY_PATH"
IMG=/bigwork/nhkcmast/debian_jessie_trace.img

cd $RUNDIR
#
#################################################################################
#Write tempscript to start TRACE
rm -f $RUNDIR/tempscript.sh
touch $RUNDIR/tempscript.sh
chmod +x $RUNDIR/tempscript.sh
echo -e "#!/bin/bash" >> $RUNDIR/tempscript.sh;
echo -e "#PBS -N $JOBNAME" >> $RUNDIR/tempscript.sh;
echo -e "#PBS -M $EMAIL" >> $RUNDIR/tempscript.sh;
echo -e "#PBS -m abe" >> $RUNDIR/tempscript.sh;
echo -e "#PBS -o TRACE_job.dat" >> $RUNDIR/tempscript.sh;
echo -e "#PBS -l nodes=$NODES:ppn=$NPROCS" >> $RUNDIR/tempscript.sh;
echo -e "#PBS -l walltime=$WALLTIME" >> $RUNDIR/tempscript.sh;
echo -e "#PBS -l mem=$MEMORY" >> $RUNDIR/tempscript.sh;
echo -e "#PBS -q $QUEUE" >> $RUNDIR/tempscript.sh;
echo -e "#PBS -W x=PARTITION:tane:lena:haku" >> $RUNDIR/tempscript.sh;
##Hier wird die neue Umgebung für TRACE geladen (aktuell noch aus dem Ordner von nhkchese --> demnächst Umstellung auf nhkcssch)
echo -e "module load GCC/4.9.3-2.25 Singularity/2.4.2" >> $RUNDIR/tempscript.sh;
echo -e "export LD_LIBRARY_PATH=/home/nhkchese/sw/numerics/openmpi/lib/openmpi/:\$LD_LIBRARY_PATH" >> $RUNDIR/tempscript.sh;
echo -e "export LD_LIBRARY_PATH=/home/nhkchese/sw/numerics/openmpi/lib/:\$LD_LIBRARY_PATH" >> $RUNDIR/tempscript.sh;
echo -e "export PATH=/home/nhkchese/sw/numerics/openmpi/bin/:\$PATH" >> $RUNDIR/tempscript.sh;
echo -e "cd $RUNDIR" >> $RUNDIR/tempscript.sh;

##### Mit Controle-File
#echo -e "mpirun -x PATH -x LIBRARY_PATH -x LD_LIBRARY_PATH -d -machinefile \$PBS_NODEFILE TRACE -cgns $WORKDIR/input/$BASENAME -cntl $WORKDIR/input/$CONTROLFILE -lb $WORKDIR/input/$BALANCE_FILE -o TRACE.lst." >> $RUNDIR/tempscript.sh;
echo -e "mpirun $MPIARGS --machinefile \$PBS_NODEFILE singularity exec $IMG TRACE -cgns $WORKDIR/input/$BASENAME -cntl $WORKDIR/input/$CONTROLFILE -lb $WORKDIR/input/$BALANCE_FILE -o TRACE.lst." >> $RUNDIR/tempscript.sh;

##### Copy and run merge journal
echo -e "source /home/nhkcssch/load_trace_env.sh" >> $RUNDIR/tempscript.sh;
echo -e "module load gmc" >> $RUNDIR/tempscript.sh;
echo -e "cd $RUNDIR/../output/cgns/" >> $RUNDIR/tempscript.sh;
echo -e "cp $RUNDIR/../../TRACE_tools/merge.journal ." >> $RUNDIR/tempscript.sh;
echo -e "/home/nhkcssch/sw/sandy_bridge/gmc/9.0.26/gmcPlay_v9_0_26 merge.journal" >> $RUNDIR/tempscript.sh;
echo -e "cd $RUNDIR" >> $RUNDIR/tempscript.sh;

##### Run post
echo -e "module load post/9.1.538.TFD.0" >> $RUNDIR/tempscript.sh;
echo -e "mpirun -x PATH -x LIBRARY_PATH -x LD_LIBRARY_PATH -d -N 2 /home/nhkcssch/sw/sandy_bridge/post/9.1.538.TFD.0/POST --input $WORKDIR/output/cgns/TRACE_merged.cgns -rbc --intersectPanel -gf $WORKDIR/../TRACE_tools/s2m_generated_undefined.dat -cf $WORKDIR/../TRACE_tools/cut_S3.dat -bf $WORKDIR/../TRACE_tools/cut_band.dat --interpolate2d --createBandedInterfaces --averaging --buildTurbomachine --globalTurbomachineryAnalysis --writeGta -tecplotASCII $WORKDIR/post -vertexBased $WORKDIR/post/ >> $WORKDIR/post.log" >> $RUNDIR/tempscript.sh

#################################################################################
#submit job to queue
qsub $RUNDIR/tempscript.sh
