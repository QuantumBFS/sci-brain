#!/usr/bin/env bash
# Adapt the SBATCH header, module lines, QE_ROOT, NPOOL, and resource request
# to the target cluster before submitting.
# This template uses one Slurm task with many CPUs and launches NP MPI ranks
# inside that cpuset. If the target cluster expects one Slurm task per MPI
# rank, change to --ntasks-per-node=<NP>, --cpus-per-task=1, and
# NP="${SLURM_NTASKS}".
#SBATCH --job-name=qe-epc-example
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=64
#SBATCH --mem=128GB
#SBATCH --time=7-00:00:00
#SBATCH --output=slurm-%x-%j.out

set -euo pipefail

: "${QE_ROOT:?set QE_ROOT to a Quantum ESPRESSO prefix containing bin/pw.x and bin/ph.x}"
NP="${SLURM_CPUS_PER_TASK:-4}"
NPOOL="${NPOOL:-1}"

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1

archive_existing_outputs() {
  shopt -s nullglob
  local existing=()
  local path
  for path in tmp _ph0 run_steps.tsv \
    scf.out ph_ifc.out q2r.out matdyn_disp.out ph_dvscf_epc.out elph_densek.out alpha2f.out \
    scf.err ph_ifc.err q2r.err matdyn_disp.err ph_dvscf_epc.err elph_densek.err alpha2f.err \
    *.a2F* *.lambda* *.freq *.fc *.modes *.dyn* CRASH; do
    [[ -e "$path" ]] && existing+=("$path")
  done
  if (( ${#existing[@]} > 0 )); then
    local archive="archive_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$archive"
    mv "${existing[@]}" "$archive"/
    echo "[archive] moved existing outputs to $archive"
  fi
  shopt -u nullglob
}

archive_ifc_ph_scratch() {
  if [[ -d tmp/_ph0 ]]; then
    local archive="tmp/_ph0_ifc_$(date +%Y%m%d_%H%M%S)"
    mv tmp/_ph0 "$archive"
    echo "[scratch] moved IFC PH scratch to $archive before EPC branch"
  fi
}

run_mpi_qe() {
  local label=$1
  local executable=$2
  local input=$3
  local output=$4
  shift 4
  echo "[start] $(date -Is) $label input=$input host=$(hostname)"
  local start_epoch
  start_epoch=$(date +%s)
  set +e
  mpirun -np "$NP" "$QE_ROOT/bin/$executable" "$@" -in "$input" > "$output" 2> "${label}.err"
  local status=$?
  set -e
  local end_epoch
  end_epoch=$(date +%s)
  printf "%s\t%s\t%s\t%s\n" "$label" "$status" "$start_epoch" "$end_epoch" >> run_steps.tsv
  echo "[finish] $(date -Is) $label status=$status elapsed=$((end_epoch - start_epoch))s"
  if [[ "$status" -ne 0 ]]; then
    exit "$status"
  fi
}

run_serial_qe() {
  local label=$1
  local executable=$2
  local input=$3
  local output=$4
  echo "[start] $(date -Is) $label input=$input host=$(hostname)"
  local start_epoch
  start_epoch=$(date +%s)
  set +e
  "$QE_ROOT/bin/$executable" -in "$input" > "$output" 2> "${label}.err"
  local status=$?
  set -e
  local end_epoch
  end_epoch=$(date +%s)
  printf "%s\t%s\t%s\t%s\n" "$label" "$status" "$start_epoch" "$end_epoch" >> run_steps.tsv
  echo "[finish] $(date -Is) $label status=$status elapsed=$((end_epoch - start_epoch))s"
  if [[ "$status" -ne 0 ]]; then
    exit "$status"
  fi
}

echo "[job] $(date -Is) job_id=${SLURM_JOB_ID:-none} np=$NP npool=$NPOOL"
echo "[job] nodes=${SLURM_JOB_NODELIST:-$(hostname)}"
echo "[job] qe_root=$QE_ROOT"
echo "[job] threads OMP=$OMP_NUM_THREADS MKL=$MKL_NUM_THREADS OPENBLAS=$OPENBLAS_NUM_THREADS"

archive_existing_outputs
mkdir -p tmp
printf "step\tstatus\tstart_epoch\tend_epoch\n" > run_steps.tsv

run_mpi_qe scf pw.x scf.in scf.out -npool "$NPOOL"
run_mpi_qe ph_ifc ph.x ph_ifc.in ph_ifc.out -npool "$NPOOL"
run_serial_qe q2r q2r.x q2r.in q2r.out
run_serial_qe matdyn_disp matdyn.x matdyn_disp.in matdyn_disp.out
archive_ifc_ph_scratch
run_mpi_qe ph_dvscf_epc ph.x ph_dvscf_epc.in ph_dvscf_epc.out -npool "$NPOOL"
run_mpi_qe elph_densek ph.x elph_densek_alpha2f.in elph_densek.out -npool "$NPOOL"
run_serial_qe alpha2f alpha2f.x elph_densek_alpha2f.in alpha2f.out

echo "[done] $(date -Is) job_id=${SLURM_JOB_ID:-none}"
