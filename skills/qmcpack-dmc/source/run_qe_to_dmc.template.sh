#!/usr/bin/env bash
# Generic QE -> pw2qmcpack -> QMCPACK Slater-Jastrow/DMC launcher.
# Adapt executable paths, MPI flags, K_POINTS, pseudopotentials, and XML files
# to the active project before running.
set -euo pipefail

: "${QE_BIN:?set QE_BIN to a pw.x executable from the QE build paired with pw2qmcpack.x}"
: "${PW2QMCPACK:?set PW2QMCPACK to pw2qmcpack.x}"
: "${QMCPACK_COMPLEX_BIN:?set QMCPACK_COMPLEX_BIN to qmcpack_complex}"

MPIRUN="${MPIRUN:-mpirun}"
MPI_FLAGS="${MPI_FLAGS:-}"
QE_NP="${QE_NP:-4}"
QE_NPOOL="${QE_NPOOL:-1}"
PW2QMCPACK_NP="${PW2QMCPACK_NP:-1}"
PARALLEL_TWISTS="${PARALLEL_TWISTS:-1}"
QMC_NP="${QMC_NP:-1}"
QMC_MPI_FLAGS="${QMC_MPI_FLAGS:---bind-to none}"
TWIST_LIST="${TWIST_LIST:-00}"
FORCE_QE="${FORCE_QE:-0}"
FORCE_QMC="${FORCE_QMC:-0}"

export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"
export OMP_PROC_BIND="${OMP_PROC_BIND:-false}"

run_mpi_or_serial() {
  local np=$1
  shift
  local exe=$1
  shift
  if [[ "$np" -gt 1 ]]; then
    # shellcheck disable=SC2206
    local flags=( ${MPI_FLAGS} )
    "$MPIRUN" "${flags[@]}" -np "$np" "$exe" "$@"
  else
    "$exe" "$@"
  fi
}

run_qmc() {
  local xml=$1
  local out=${xml%.xml}.out
  if [[ "$FORCE_QMC" != "1" && -s "$out" ]] && grep -q "QMCPACK execution completed successfully" "$out"; then
    echo "[skip] $xml already completed"
    return 0
  fi
  # shellcheck disable=SC2206
  local qmc_flags=( ${QMC_MPI_FLAGS} )
  if [[ "$QMC_NP" -gt 1 ]]; then
    "$MPIRUN" "${qmc_flags[@]}" -np "$QMC_NP" "$QMCPACK_COMPLEX_BIN" "$xml" > "$out"
  else
    "$QMCPACK_COMPLEX_BIN" "$xml" > "$out"
  fi
  grep -q "QMCPACK execution completed successfully" "$out"
}

echo "[job] QE_BIN=$QE_BIN"
echo "[job] PW2QMCPACK=$PW2QMCPACK"
echo "[job] QMCPACK_COMPLEX_BIN=$QMCPACK_COMPLEX_BIN"
echo "[job] QE_NP=$QE_NP QE_NPOOL=$QE_NPOOL PW2QMCPACK_NP=$PW2QMCPACK_NP"
echo "[job] PARALLEL_TWISTS=$PARALLEL_TWISTS QMC_NP=$QMC_NP OMP_NUM_THREADS=$OMP_NUM_THREADS"
echo "[job] MPI_FLAGS=$MPI_FLAGS QMC_MPI_FLAGS=$QMC_MPI_FLAGS"

mkdir -p qe_tmp

if [[ "$FORCE_QE" == "1" || ! -s qe_tmp/qmc_solid.pwscf.h5 ]]; then
  echo "[run] QE SCF"
  run_mpi_or_serial "$QE_NP" "$QE_BIN" -npool "$QE_NPOOL" -in qe_scf.in > qe_scf.out
  grep -q "JOB DONE." qe_scf.out

  echo "[run] QE NSCF"
  run_mpi_or_serial "$QE_NP" "$QE_BIN" -npool "$QE_NPOOL" -in qe_nscf.in > qe_nscf.out
  grep -q "JOB DONE." qe_nscf.out

  echo "[run] pw2qmcpack"
  run_mpi_or_serial "$PW2QMCPACK_NP" "$PW2QMCPACK" < pw2qmcpack.in > pw2qmcpack.out
  grep -q "JOB DONE." pw2qmcpack.out
  test -s qe_tmp/qmc_solid.pwscf.h5
else
  echo "[reuse] qe_tmp/qmc_solid.pwscf.h5"
fi

declare -a batch_pids=()
declare -a batch_xmls=()
slot=0
for twist in $TWIST_LIST; do
  xml="sj_vmc_dmc_tw${twist}.xml"
  test -s "$xml"
  ( run_qmc "$xml" ) &
  batch_pids+=( "$!" )
  batch_xmls+=( "$xml" )
  slot=$((slot + 1))

  if [[ "$slot" -ge "$PARALLEL_TWISTS" ]]; then
    for idx in "${!batch_pids[@]}"; do
      if ! wait "${batch_pids[idx]}"; then
        echo "[error] ${batch_xmls[idx]} failed" >&2
        exit 1
      fi
    done
    batch_pids=()
    batch_xmls=()
    slot=0
  fi
done

for idx in "${!batch_pids[@]}"; do
  if ! wait "${batch_pids[idx]}"; then
    echo "[error] ${batch_xmls[idx]} failed" >&2
    exit 1
  fi
done

echo "[done] QE -> pw2qmcpack -> QMCPACK run completed"
