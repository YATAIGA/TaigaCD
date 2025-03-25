import ase
from ase.io import read, write
from ase.calculators.espresso import Espresso, EspressoProfile
from ase.optimize import BFGS


class DFT:
    """Class for managing DFT calculations.

    using ASE and Quantum ESPRESSO.
    """
    def __init__(
        self,
        atoms: ase.Atoms,
        pseudo_dir: str | None = None,
        command: str = "mpirun -np 4 pw.x"
    ):
        """Initialize DFT object.

        Parameters:
            atoms (ase.Atoms): Atomic structure.
            pseudo_dir (str): Path to pseudopotentials.
            command (str): Command to run Quantum ESPRESSO.
        """
        self.atoms = atoms
        self.pseudo_dir = pseudo_dir
        self.profile = EspressoProfile(
            command=command,
            pseudo_dir=pseudo_dir
        )

        # Default pseudopotentials map (override if needed)
        self.pseudopotentials = {
            symbol: f"{symbol}.pbe-n-kjpaw_psl.1.0.0.UPF"
            for symbol in set(atoms.get_chemical_symbols())
        }

    def _set_calculator(
        self, 
        input_data: dict,
        kpts: tuple | dict
    ) -> Espresso:
        """Internal method to create an Espresso calculator.

        Parameters:
            input_data (dict): Full Quantum ESPRESSO input parameters.
            kpts (tuple or dict): K-point settings.

        Returns:
            Espresso: ASE Espresso calculator object.
        """
        return Espresso(
            profile=self.profile,
            pseudopotentials=self.pseudopotentials,
            input_data=input_data,
            kpts=kpts
        )

    def relax(
        self,
        input_data: dict,
        kpts: tuple = (8, 8, 8),
        output_file="relaxed.xyz"
    ):
        """Perform structural relaxation.

        Parameters:
            input_data (dict): QE input_data for relaxation.
            kpts (tuple): Monkhorst-Pack k-point grid.
            output_file (str): File to save relaxed structure.
        """
        if input_data.get("control", {}).get("calculation") != "relax":
            raise ValueError("Input data must specify 'calculation = relax'.")

        self.atoms.calc = self._set_calculator(input_data, kpts)

        #opt = BFGS(self.atoms, logfile=f"{self.prefix}_relax.log")
        opt = BFGS(self.atoms, logfile=f"relax.log")
        opt.run(fmax=0.03)

        write(output_file, self.atoms)
        print(f"[INFO] Relaxation complete. Saved to '{output_file}'.")
