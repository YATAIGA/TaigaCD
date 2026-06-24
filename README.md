# TaigaCD

AI Agent for material design — a lightweight pipeline for running
[Quantum ESPRESSO](https://www.quantum-espresso.org/) DFT calculations through
[ASE](https://wiki.fysik.dtu.dk/ase/) (the Atomic Simulation Environment).

TaigaCD takes a user-defined atomic structure and a Quantum ESPRESSO input
specification, then dispatches the appropriate calculation — structural
relaxation, an SCF energy calculation, or a band-structure calculation — and
writes the results to an `outputs/` directory.

## How it works

The pipeline is split into three layers:

1. **Inputs** (`inputs/`) — user-editable Python modules that describe *what* to
   simulate. You define the structure and the Quantum ESPRESSO parameters here.
2. **Portal** (`portal/`) — dynamically loads the user input modules at runtime
   and returns the parsed objects to the core.
3. **Core + plugins** (`taigacd/`, `plugins/dft/`) — reads the calculation type
   and drives the `DFT` engine, which wraps ASE's Espresso calculator.

```
inputs/get_atoms.py      ──┐
                           ├──► portal ──► taigacd.core.main() ──► plugins.dft.DFT ──► Quantum ESPRESSO (pw.x)
inputs/get_qe_input.py   ──┘                                                                   │
                                                                                               ▼
                                                                                          outputs/
```

The calculation type is read from `input_data["control"]["calculation"]` and
routed to one of `DFT.relax`, `DFT.scf`, or `DFT.bands`.

## Repository layout

| Path | Purpose |
| --- | --- |
| `taigacd/core.py` | Entry point (`main()`); dispatches by calculation type. |
| `portal/` | Dynamically loads the user input modules from `inputs/`. |
| `inputs/get_atoms.py` | **User-editable.** Returns the `ase.Atoms` structure. |
| `inputs/get_qe_input.py` | **User-editable.** Returns `(input_data, kpts)` for Quantum ESPRESSO. |
| `plugins/dft/engine.py` | `DFT` class wrapping the ASE Espresso calculator (relax / scf / bands). |
| `pseudos/` | Pseudopotential files (`.UPF`), e.g. `Si.pbe-n-kjpaw_psl.1.0.0.UPF`. |
| `run_simulation.sh` | Example SLURM batch script for running on an HPC cluster. |
| `requirements.txt` | Python dependencies. |

## Requirements

- **Python** 3.10+ (the code uses `str | None` type syntax).
- **Python packages:** `ase`, `numpy`, `scipy` (see `requirements.txt`).
- **Quantum ESPRESSO** — the `pw.x` executable must be on your `PATH`.
- **An MPI runtime** (e.g. `mpirun`); the engine defaults to `mpirun -np 4 pw.x`.
- **Pseudopotentials** matching your elements, placed in `pseudos/`.

## Installation

```bash
git clone <repository-url>
cd TaigaCD

python -m venv taigacd_env
source taigacd_env/bin/activate

pip install -r requirements.txt
```

Quantum ESPRESSO and MPI are external tools and must be installed separately
(via your package manager, [Spack](https://spack.io/), conda-forge, or your HPC
environment modules).

## Usage

### 1. Define the structure — `inputs/get_atoms.py`

Return an `ase.Atoms` object. For example, bulk silicon:

```python
from ase.build import bulk

def get_atoms():
    atoms = bulk('Si', 'diamond', a=5.43)
    return atoms
```

### 2. Define the Quantum ESPRESSO input — `inputs/get_qe_input.py`

Return a `(input_data, kpts)` tuple. `input_data` follows ASE's
`Espresso` calculator format, and `control.calculation` selects the run type
(`relax`, `scf`, or `bands`):

```python
def get_qe_input():
    input_data = {
        "control": {
            "calculation": "relax",
            "prefix": "si",
            "pseudo_dir": "./pseudos",
            "outdir": "./tmp",
        },
        "system": {
            "ecutwfc": 40,
            "ecutrho": 320,
            "occupations": "smearing",
            "smearing": "mp",
            "degauss": 0.01,
        },
        "electrons": {
            "conv_thr": 1e-6,
        },
    }
    kpts = (8, 8, 8)
    return input_data, kpts
```

For a **band-structure** run, set `control.calculation = "bands"` and return a
k-point path dictionary instead of a Monkhorst–Pack grid, e.g.
`{"path": "GXWKGL", "npoints": 100}`.

### 3. Run

```bash
python -m taigacd.core
```

Or submit to an HPC scheduler:

```bash
sbatch run_simulation.sh
```

## Calculation types

| `calculation` | Method | Output |
| --- | --- | --- |
| `relax` | Structural relaxation via ASE's `BFGS` optimizer (`fmax=0.03`). | `outputs/relaxed.cif`, `outputs/relax.log` |
| `scf` | Self-consistent field total-energy calculation. | Total energy printed to stdout. |
| `bands` | Band-structure calculation along a k-point path. | `outputs/bs.json` |

Results are written to the `outputs/` directory (created relative to the working
directory). Pseudopotentials are resolved from the `pseudo_dir` configured on the
`DFT` engine (default `../pseudos`).

## Notes

- The `DFT` engine defaults to `mpirun -np 4 pw.x`. Adjust the `command`
  argument in `plugins/dft/engine.py` (or instantiate `DFT(atoms, command=...)`)
  to match your cluster and core count.
- Pseudopotential filenames are derived automatically per element as
  `{symbol}.pbe-n-kjpaw_psl.1.0.0.UPF`; make sure matching files exist in
  `pseudos/`.

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).
