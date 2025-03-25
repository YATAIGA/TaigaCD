from ase.build import bulk

from plugins.dft import DFT

atoms = bulk('Si', 'diamond', a=5.43)

dft = DFT(atoms)

print(dft.pseudopotentials)
