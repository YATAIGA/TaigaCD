from taigacd.input_parser import parse_input
from taigacd.structure.factory import get_structure_builder
from taigacd.calculators import get_qe_calculator


def test_calculator():
    input_data = parse_input("inputs/Si_bandstructure.json")

    structure_data = input_data["material"]
    builder = get_structure_builder("crystal")
    atoms = builder.build({
        "formula": structure_data["formula"],
        "crystal_structure": structure_data["crystal_structure"],
        "lattice": {"a": 5.431}
    })

    calc_params = input_data["calculation"]["parameters"]
    calculator = get_qe_calculator(
        atoms,
        calc_params,
        pw_executable='pw.x',
        mpi_command='mpirun -np 4',  # 若有其他MPI指令可修改，如：srun, mpirun等
        pseudo_dir='~/pseudos'
    )

    atoms.calc = calculator

    print(calculator.parameters)


if __name__ == "__main__":
    test_calculator()
