import os
import importlib.util


def get_atoms(
):
    """ Atomic structures generated.

    Returns:
        atoms (ase.Atoms)
    """
    INPUT_FILE_PATH = os.path.join('.', 'inputs', 'get_atoms.py')

    if not os.path.isfile(INPUT_FILE_PATH):
        raise FileNotFoundError(f"File {INPUT_FILE_PATH} does not exist!")

    spec = importlib.util.spec_from_file_location("get_atoms", INPUT_FILE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    atoms = module.get_atoms()
    
    return atoms
