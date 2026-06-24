# TaigaCD

**AI Agent for materials design and simulation.**

TaigaCD is a prototype platform that combines large language model (LLM) agents
with established atomistic simulation tools to automate materials simulation
workflows. It pairs a self-improving code-generation agent loop with a DFT
engine built on top of [ASE](https://wiki.fysik.dtu.dk/ase/) and
[Quantum ESPRESSO](https://www.quantum-espresso.org/), and exposes a small
FastAPI service for triggering runs.

---

## Overview

The project has two complementary execution paths:

1. **Agentic code generation (`taigacd/core.py`)** — A *worker* agent generates
   a complete Python/ASE simulation snippet from a natural-language request, the
   code is executed in a sandboxed namespace, and an *evaluator* agent reviews
   the output for physical/chemical correctness. Feedback is fed back to the
   worker and the loop repeats until the result passes (or the iteration limit
   is reached).

2. **DFT engine (`plugins/dft/engine.py`)** — A reusable `DFT` class that wraps
   ASE's Quantum ESPRESSO calculator to perform structural relaxation, SCF, and
   band-structure calculations on a given `ase.Atoms` object.

---

## Repository layout

```
TaigaCD/
├── taigacd/
│   └── core.py            # Agent loop (worker + evaluator) and FastAPI app
├── plugins/
│   ├── dft/
│   │   └── engine.py      # DFT class: relax / scf / bands via ASE + Quantum ESPRESSO
│   └── sim/
│       └── sim.py         # Placeholder for a pure-ASE simulation plugin
├── portal/
│   ├── get_atoms.py       # Dynamically loads inputs/get_atoms.py
│   └── get_qe_input.py    # Dynamically loads inputs/get_qe_input.py
├── inputs/
│   ├── get_atoms.py       # User/portal-generated atomic structure
│   └── get_qe_input.py    # User/portal-generated Quantum ESPRESSO input
├── pseudos/               # Pseudopotential files (.UPF)
├── run_simulation.sh      # SLURM batch submission script
├── requirements.txt       # Python dependencies
├── LICENSE
└── README.md
```

---

## Installation

A Python 3.10+ environment is recommended (the code uses modern type-hint
syntax such as `str | None`).

```bash
# Create and activate an environment (conda shown; venv works too)
conda create -n taiga python=3.11
conda activate taiga

# Install Python dependencies
pip install -r requirements.txt
```

`requirements.txt` covers the simulation and web stack:

- `ase` — atomic simulation environment
- `numpy`, `scipy` — numerics
- `fastapi`, `uvicorn` — web service

> **Note:** The agent loop in `taigacd/core.py` additionally depends on the
> `agents` (OpenAI Agents SDK) package and a configured LLM API key. Install it
> separately (e.g. `pip install openai-agents`) and export the relevant API key
> in your environment before running the agentic workflow.

For DFT calculations you also need a working **Quantum ESPRESSO** installation
(providing `pw.x`) and matching pseudopotentials in `pseudos/`.

---

## Usage

### 1. Run the FastAPI service

```bash
python -m taigacd.core
```

This starts a Uvicorn server on `http://0.0.0.0:8000`. A test endpoint is
available:

```bash
curl -X POST "http://localhost:8000/run?req=relax%20silicon"
```

### 2. Run the agent loop directly

The interactive worker/evaluator loop lives in `main()` in `taigacd/core.py`.
To use it, enable the `asyncio.run(main())` call at the bottom of the file (it
is commented out by default), then run the module. You will be prompted for a
simulation request, for example:

```
Enter your materials simulation request: Compute the cohesive energy of bulk copper using EMT.
```

The worker is restricted to **pure-Python ASE calculators** (EMT, EAM,
Lennard-Jones, Morse, Tersoff, HarmonicCalculator). Generated code, outputs, and
logs are written under `outputs/` and `logs/`.

### 3. Run a DFT calculation programmatically

```python
from ase.build import bulk
from plugins.dft import DFT

atoms = bulk("Si", "diamond", a=5.43)

dft = DFT(atoms, pseudo_dir="./pseudos", command="mpirun -np 4 pw.x")

# Structural relaxation
relax_input = {
    "control": {"calculation": "relax", "prefix": "si"},
    "system": {"ecutwfc": 40, "ecutrho": 320,
               "occupations": "smearing", "smearing": "mp", "degauss": 0.01},
    "electrons": {"conv_thr": 1e-6},
}
dft.relax(relax_input, kpts=(8, 8, 8))

# SCF
scf_input = {**relax_input, "control": {"calculation": "scf", "prefix": "si"}}
dft.scf(scf_input, kpts=(12, 12, 12))

# Band structure
bands_input = {**relax_input, "control": {"calculation": "bands", "prefix": "si"}}
dft.bands(bands_input, band_kpts={"path": "GXWLGK", "npoints": 100})
```

Helper functions `portal.get_atoms()` and `portal.get_qe_input()` dynamically
load the structure and QE input definitions from the `inputs/` directory, which
is where portal- or user-generated definitions are placed.

### 4. Run on an HPC cluster (SLURM)

`run_simulation.sh` is a SLURM batch script that loads Quantum ESPRESSO and a
conda environment, then runs `python -m taigacd.core`. Adjust the SBATCH
directives, account, partition, and module names for your cluster:

```bash
sbatch run_simulation.sh
```

---

## License

See [LICENSE](LICENSE).
