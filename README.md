# ABACUS Finite Difference (abacus-fd)

A Python library for computing forces (unit: eV/Angstrom) and electronic states via finite difference with ABACUS DFT software. 

This tool is specifically optimized for **FSSH (Fewest Switches Surface Hopping)** workflows, allowing ABACUS to delegate intensive SCF and LR-TDDFT calculations to a task-parallelized external process.

## Installation

```bash
pip install .
```

Or install in development mode:

```bash
pip install -e .
```

## Dependencies

- `ase` (Atomic Simulation Environment) for reading/writing ABACUS STRU files
- `ase` with ABACUS IO support (auto-installed from `https://gitlab.com/1041176461/ase-abacus.git` by `pip install .`)
- `numpy`
- ABACUS executable (external, not included)

## Command Line Interface

```bash
abacus-fd --help
```

### Command Categories

| Command | Description | Atoms | Directions |
|---------|-------------|-------|------------|
| `kslr-all` | KSDFT + LR-TDDFT excited state forces | All atoms | x, y, z |
| `kslr-custom` | KSDFT + LR-TDDFT excited state forces | Specified | Specified |
| `kslr-states` | Single point SCF + LR-TDDFT (for WFC/Amplitudes) | 1 config | N/A |
| `gs-all` | Ground state forces | All atoms | x, y, z |
| `gs-custom` | Ground state forces | Specified | Specified |
| `lr-all` | LR-TDDFT excited state forces | All atoms | x, y, z |
| `lr-custom` | LR-TDDFT excited state forces | Specified | Specified |
| `vib` | Vibration analysis (Harmonic frequencies) | All atoms | x, y, z |

- `all`: Compute forces for all atoms, displacement directions are x, y, z
- `custom`: Compute forces only for specified atoms and directions
- Atom indices are 0-based
- Central difference (displacement ±dx/2)

### Common Parameters

| Short | Long | Description | Default |
|-------|------|-------------|---------|
| `-d` | `--dir` | Working directory | Current dir |
| `-a` | `--abacus` | ABACUS executable path | `abacus` |
| `-x` | `--dx` | Displacement (Angstrom) | `0.001` |
| `-n` | `--nproc` | MPI ranks **per task** | `1` |
| `-j` | `--nparallel` | Number of **concurrent tasks** | `1` |
| `-i` | `--indices` | Atom indices (comma-separated) | - |
| `-s` | `--skip-gs` | Skip ground state calculation | False |
| | `--cleanup` | Delete temporary `points/` after extraction | True |
| | `--no-cleanup` | Keep temporary folders for debugging | False |

## Parallelism and Resource Management

`abacus-fd` supports two levels of parallelism:
1. **Task-level parallelism (`-j / --nparallel`)**: Uses Python's `ProcessPoolExecutor` to run multiple atomic displacement configurations simultaneously.
2. **MPI-level parallelism (`-n / --nproc`)**: Uses `mpirun -np <nproc>` to run each individual ABACUS instance.

**Best Practice:**
Ensure your total core count matches the product: 
`Total Cores >= nparallel * nproc`.

For small systems (like LiH), it is often more efficient to use higher `nparallel` and `nproc=1` to avoid MPI overhead and potential numerical instabilities in ScaLAPACK.

---

### kslr-all

KSDFT + LR-TDDFT excited state forces for all atoms along x/y/z.

**Usage:**
```bash
abacus-fd kslr-all [-d DIR] [-a ABACUS] [-x DX] [-n NPROC] [-j NPARALLEL] [--no-cleanup]
```

**Examples:**
```bash
# Run 4 concurrent tasks, each task using 1 core
abacus-fd kslr-all -j 4 -n 1
```

**Input files:** `STRU`, `INPUT` (must set `lr_nstates`, `esolver_type ks-lr`)

**Output files:**
- `excited_forces.npy`: numpy array, shape `(2, nstates, natoms, 3)`
- `excited_forces.txt`: text format, columns `S/T  state_idx  atom_idx  x  y  z`

---

### kslr-states

Runs a single ABACUS calculation (SCF + LR-TDDFT) and outputs wavefunctions and excitation amplitudes. This is used by the FSSH "hijack" logic to sync electronic states.

**Usage:**
```bash
abacus-fd kslr-states [-d DIR] [-a ABACUS] [-n NPROC]
```

**Output:**
- `wf_nao.txt`: LCAO wavefunctions.
- `Excitation_Amplitude_singlet_*.dat`: Casida X coefficients for each rank.
- `Excitation_Energy_singlet.dat`: Excitation energies.

---

### kslr-custom

KSDFT + LR-TDDFT excited state forces for specified atoms and directions.

**Usage:**
```bash
abacus-fd kslr-custom [-d DIR] [-a ABACUS] -i INDICES --axes AXES [-x DX] [-n NPROC] [-j NPARALLEL] [--no-cleanup]
```

---

### gs-all / gs-custom

Ground state forces using task-parallelized finite difference.

---

### vib

Numerical vibration analysis (Harmonic frequencies and normal modes) using finite difference of analytical forces.

**Usage:**
```bash
abacus-fd vib [-d DIR] [-a ABACUS] [-x DX] [-n NPROC] [-j NPARALLEL] [--no-cleanup]
```

**Output files:**
- `vibration.log`: Harmonic frequencies (cm⁻¹) and normalized displacement vectors (standard ABACUS format).
- `hessian.npy`: Raw Hessian matrix ($3N \times 3N$).

---

## Notes

- **Central Difference**: Used by default (splits displacement into +dx/2 and -dx/2).
- **Automatic Cleanup**: By default, `abacus-fd` deletes massive temporary folders (`points/`, `moved_STRU/`) after extracting forces to prevent **"Disk quota exceeded"** errors in long FSSH runs. Use `--no-cleanup` if you need to inspect individual task logs.
- **Environment Isolation**: `abacus-fd` aggressively cleans MPI-related environment variables (`SLURM_*`, `OMPI_*`, `PMIX_*`, `I_MPI_*`) and sets `KMP_AFFINITY=disabled` before spawning tasks. This prevents nested MPI deadlocks and resource contention, resolving performance lags in cluster environments.
- **Requirements**: `lr-*` commands require both `INPUT_gs` and `INPUT_lr` files.
- **Atom Indices**: 0-based (first atom is index 0).

## Testing

No formal test suite. Test data in `test/` directory is for manual verification with real ABACUS runs.
