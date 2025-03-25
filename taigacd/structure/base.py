from abc import ABC, abstractmethod
from ase.atoms import Atoms


class StructureBuilder(ABC):
    @abstractmethod
    def build(self, parameters: dict) -> Atoms:
        pass
