#!/bin/bash
#SBATCH --job-name="REPLACE_JOB"
#SBATCH --partition=amo
#SBATCH --nodes="REPLACE_NODES"
#SBATCH --ntasks-per-node="REPLACE_CPUS"
#SBATCH --mem-per-cpu="REPLACE_MEM"
#SBATCH --time=12:00:00
#SBATCH --mail-user=m.stoewer@stud.uni-hannover.de
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --error err.run
#SBATCH --output log.run
##-----------------------------------------------------
##------------- EDIT HERE AS WELL AS THE ABOVE-------------

##All input must be in quotation mark

## TRACE version (93, 941, or 943). Note that TRACE9.1 installation does not work on the new systems (skylake, cascade lake). Use pbs instead to reach the old systems.
## Note also that having modules loaded in bashrc can cause conflicts and problems.
TRACE_VERSION="943"

## Precision (dp or sp):
TRACE_PRECISION="dp"

##/bigwork/nhkcmast/10_MA/Test/TRACE_tools/TRACE.cgns

##  TRACE input cgns:
CGNS_FILE="../input/TRACE.cgns"

## Control input file:
CONTROL_INPUT_FILE="../input/TRACE_control.input"

## BALANCE file. It can be left empty:
BALANCE_FILE=""

##------------------------------------------------------


echo "The CPU architecture is $ARCH "

# pre-append "-lb" to BALANCE_FILE if not empty
if [ "$BALANCE_FILE" != "" ]; then
 BALANCE_FILE="-lb ":$BALANCE_FILE
fi


# Change to my work dir
cd $SLURM_SUBMIT_DIR

# record some info
echo "$SLURM_NTASKS tasks requested. The list of nodes: $SLURM_NTASKS_PER_CORE "
echo "run on $(hostname)"

# Load modules
source /bigwork/nhkckcen/sw/trace${TRACE_VERSION}_${TRACE_PRECISION}_profile.sh




# Run application
srun --cpu_bind=cores --distribution=block:cyclic $(which TRACE) -cgns $CGNS_FILE -cntl $CONTROL_INPUT_FILE $BALANCE_FILE

