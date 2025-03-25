from ase.build import bulk
from .base import StructureBuilder


class CrystalBuilder(StructureBuilder):
    def build(self, parameters: dict):
        formula = parameters["formula"]
        crystal_structure = parameters["crystal_structure"]
        lattice = parameters["lattice"]

        atoms = bulk(
            formula,
            crystal_structure,
            a=lattice.get("a"),
            b=lattice.get("b", lattice.get("a")),
            c=lattice.get("c", lattice.get("a"))
        )
        return atoms
