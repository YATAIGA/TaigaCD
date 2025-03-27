from plugins.dft import DFT
import portal


def main():
    # Get input files from Portal
    atoms = portal.get_atoms()
    input_data, kpts = portal.get_qe_input()

    sim = DFT(atoms)

    # Check calculation type (e.g. relax, scf, etc.)
    calc_type = input_data.get("control", {}).get("calculation")
    if calc_type == "relax":
        print(f"calc_type = {calc_type}")
        sim.relax(
            input_data=input_data,
            kpts = kpts
        )
    # Start simulation

if __name__ == "__main__":
    main()
