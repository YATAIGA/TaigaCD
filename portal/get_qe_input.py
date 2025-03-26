import os
import importlib.util


def get_qe_input(
):
    """ ASE Espresso calculator input.

    Returns:
        input_data (dict)
        kpts (tuple | dict)
    """
    INPUT_FILE_PATH = os.path.join('.', 'inputs', 'get_qe_input.py')

    if not os.path.isfile(INPUT_FILE_PATH):
        raise FileNotFoundError(f"File {INPUT_FILE_PATH} does not exist!")

    spec = importlib.util.spec_from_file_location("get_qe_input", INPUT_FILE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    input_data, kpts = module.get_qe_input()

    return input_data, kpts
