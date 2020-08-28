#!/bin/sh
module load python/3.6.0
module load gcc/7.3.0
module load cuda/10.2
module load openmpi/2.1.2
module load libmatheval
module load anaconda/3

export PATH
source /cluster/tufts/ysl8/jovan/gromacs_linlab_avx2/bin/GMXRC.bash
export PLUMED_KERNEL=/cluster/tufts/ysl8/jovan/gromacs_linlab_avx2/plumed/lib/libplumedKernel.so
export GMXLIB=/cluster/tufts/ylin12/tim/localGMXLIB

conda activate research360

echo "Enter the sequence with uppercase letter indicating L-aa and lowercase letter indicating D-aa: "
read sequence
sed -i s/SEQUENCETOCHANGE/${sequence}/ submit.job

for i in 1 2
do
    cd 1pdb2gmx/s${i}
    gmx_mpi pdb2gmx -f *.pdb -o prot.gro -p cx_amber99sbMod_tip3p_temp.top -ter -inter -chainsep id -merge interactive
    python add_improper.py --ori cx_amber99sbMod_tip3p_temp.top --out cx_amber99sbMod_tip3p.top --gro prot.gro
    python g_mod_top_RSFF2_cyclic.py cx_amber99sbMod_tip3p.top cx_rsff2_tip3p.top

    cp cx_rsff2_tip3p.top ../../2em_genion/s${i}
    cp posre.itp ../../2em_genion/s${i}
    cp prot.gro ../../2em_genion/s${i}

    cd ../../2em_genion/s${i}
    gmx_mpi grompp -v -f em.mdp -c prot.gro -p cx_rsff2_tip3p.top -o em.tpr &> grompp.log
    gmx_mpi mdrun -v -s em.tpr -deffnm em &> mdrun.log
    python check_trajectory.py --seq ${sequence} --gro em.gro

    gmx_mpi editconf -f em.gro -o box.gro -bt cubic -d 1.0 &> editconf.log
    gmx_mpi solvate -cp box.gro -cs spc216.gro -p cx_rsff2_tip3p.top -o solvate.gro &> isolvate.log

    gmx_mpi grompp -v -f ion.mdp -c solvate.gro -p cx_rsff2_tip3p.top -o ion.tpr &> grompp.log
    gmx_mpi genion -s ion.tpr -p cx_rsff2_tip3p.top -o ion.gro -neutral

    cp ion.gro ../../3em_npt/s${i}/
    cp cx_rsff2_tip3p.top ../../3em_npt/s${i}/

    cd ../../
done

