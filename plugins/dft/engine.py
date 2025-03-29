import ase
from ase.io import read, write
from ase.calculators.espresso import Espresso, EspressoProfile
from ase.calculators.calculator import all_changes
from ase.spectrum.band_structure import BandStructure
from ase.dft.kpoints import bandpath
from ase.optimize import BFGS


OUTPUT_DIR = "./outputs"
class DFT:
    """Class for managing DFT calculations.

    using ASE and Quantum ESPRESSO.
    """
    def __init__(
        self,
        atoms: ase.Atoms,
        pseudo_dir: str | None = "../pseudos",
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
        kpts: tuple | dict,
        calc_type: str
    ) -> Espresso:
        """Internal method to create an Espresso calculator.

        Parameters:
            input_data (dict): Full Quantum ESPRESSO input parameters.
            kpts (tuple or dict): K-point settings.

        Returns:
            Espresso: ASE Espresso calculator object.
        """

        # Set pseudo_dir
        input_data["control"]["pseudo_dir"] = self.pseudo_dir

        return Espresso(
            profile=self.profile,
            pseudopotentials=self.pseudopotentials,
            input_data=input_data,
            kpts=kpts,
            directory='./outputs'
            # directory=f'./outputs/{calc_type}'
        )

    def relax(
        self,
        input_data: dict,
        kpts: tuple = (8, 8, 8),
        output_file=f"{OUTPUT_DIR}/relaxed.cif"
    ):
        """Perform structural relaxation.

        Parameters:
            input_data (dict): Full QE input for relaxation.
            kpts (tuple): Monkhorst-Pack k-point grid.
            output_file (str): File to save relaxed structure.
        """
        if input_data.get("control", {}).get("calculation") != "relax":
            raise ValueError("Input data must specify 'calculation = relax'.")

        self.atoms.calc = self._set_calculator(input_data, kpts, calc_type="relax")

        # opt = BFGS(self.atoms, logfile=f"{self.prefix}_relax.log")
        opt = BFGS(self.atoms, logfile=f"{OUTPUT_DIR}/relax.log")
        opt.run(fmax=0.03)

        write(output_file, self.atoms)
        print(f"[INFO] Relaxation complete. Saved to '{output_file}'.")

    def scf(
        self, 
        input_data: dict,
        kpts: tuple=(12, 12, 12)
    ):
        """Perform self-consistent field (SCF) calculation.

        Parameters:
            input_data (dict): Full QE input for SCF.
            kpts (tuple): K-point mesh.
        """
        if input_data.get("control", {}).get("calculation") != "scf":
            raise ValueError("Input data must specify 'calculation = scf'.")

        self.atoms.calc = self._set_calculator(input_data, kpts, calc_type="scf")

        energy = self.atoms.get_potential_energy()
        print(f"[INFO] SCF complete. Total energy: {energy:.6f} eV")
    def bands(
        self,
        input_data: dict,
        band_kpts: dict,
    ):
        """Perform band structure calculation.

        Parameters:
            input_data (dict): Full QE input for bands.
            band_kpts (dict): K-point path info: {'path': str, 'npoints': int}.
        """
        if input_data.get("control", {}).get("calculation") != "bands":
            raise ValueError("Input data must specify 'calculation = bands'.")

        self.atoms.calc = self._set_calculator(input_data, band_kpts, calc_type="bands")
        results_bands = self.atoms.get_properties(['eigenvalues'])
        
        path = bandpath(list(band_kpts["path"]), cell=self.atoms.cell, npoints=band_kpts["npoints"])

        bs = BandStructure(
            path=path,
            energies=results_bands['eigenvalues']
            # reference=self.atoms.calc.get_fermi_level()
        )
        bs.write("outputs/bs.json")

        print("[INFO] Band structure calculation complete.")
