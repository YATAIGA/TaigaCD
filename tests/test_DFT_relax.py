from ase.build import bulk

from plugins.dft import DFT

# Set ase.Atoms and DFT engines
atoms = bulk('Si', 'diamond', a=5.43)
dft = DFT(atoms)

# ASE Espresso calculator input
relax_input = {
    "control": {
        "calculation": "relax",
        "prefix": "si",
        "pseudo_dir": "./pseudos",
        "outdir": "./tmp"
    },
    "system": {
        "ecutwfc": 40,
        "ecutrho": 320,
        "occupations": "smearing",
        "smearing": "mp",
        "degauss": 0.01
    },
    "electrons": {
        "conv_thr": 1e-6
    }
}

dft.relax(input_data=relax_input, kpts=(8, 8, 8), output_file="si_relaxed.xyz")
