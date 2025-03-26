from plugins.dft import DFT
import portal


def main():
    # Get input files from Portal
    atoms = portal.get_atoms()
    input_data, kpts = portal.get_qe_input()
    print(atoms)
    print(input_data, kpts)

    # Check calculation type (e.g. relax, scf, etc.)
    # Start simulation

if __name__ == "__main__":
    main()
