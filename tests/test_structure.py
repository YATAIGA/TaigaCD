from taigacd.input_parser import parse_input
from taigacd.structure.factory import get_structure_builder


def test_structure():
    input_data = parse_input("inputs/Si_crystal.json")
    structure_data = input_data["structure"]

    builder = get_structure_builder(structure_data["type"])
    atoms = builder.build(structure_data["parameters"])

    print(atoms)


if __name__ == "__main__":
    test_structure()
