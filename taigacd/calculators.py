from ase.calculators.espresso import Espresso, EspressoProfile
from ase.atoms import Atoms


def get_qe_calculator(atoms: Atoms, calc_params: dict,
                      pw_executable='pw.x',
                      mpi_command='mpirun -np 4',
                      pseudo_dir='~/pseudos') -> Espresso:
    """
    建立 Quantum Espresso ASE Calculator (適用於ASE最新版)。

    Parameters:
        atoms (Atoms): ASE Atoms 物件。
        calc_params (dict): 包含 QE calculator 參數。
        pw_executable (str): pw.x 執行檔路徑。
        mpi_command (str): MPI 指令及核心數量，如 'mpirun -np 8'。
        pseudo_dir (str): 贗勢檔案資料夾路徑。

    Returns:
        Espresso: ASE Quantum Espresso 計算器。
    """
    pseudopotentials = {
        symbol: calc_params["pseudopotential"]
        for symbol in set(atoms.get_chemical_symbols())
    }

    input_data = {
        'control': {
            'calculation': calc_params.get("relax_type", "scf"),
            'verbosity': 'high',
            'restart_mode': 'from_scratch',
            'pseudo_dir': pseudo_dir,
            'tstress': True,
            'tprnfor': True,
        },
        'system': {
            'ecutwfc': calc_params["ecutwfc"],
            'ecutrho': calc_params["ecutrho"],
            'occupations': 'smearing',
            'smearing': calc_params["smearing"]["type"],
            'degauss': calc_params["smearing"]["degauss"],
            'nspin': 2 if calc_params.get("spin_polarized", False) else 1,
        },
        'electrons': {
            'conv_thr': calc_params["convergence_threshold"],
        }
    }

    # 最新 ASE EspressoProfile 的正確設定方式
    full_command = f"{mpi_command} {pw_executable}"

    profile = EspressoProfile(
        command=full_command,
        pseudo_dir=pseudo_dir
    )

    calculator = Espresso(
        profile=profile,
        pseudopotentials=pseudopotentials,
        input_data=input_data,
        kpts=calc_params["kpoints"]["optimization"],
        symmetry=calc_params.get("use_symmetry", True)
    )

    return calculator
