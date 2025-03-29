from plugins.dft import DFT
import portal


def main():
    # Get input files from Portal
    atoms = portal.get_atoms()
    input_data, kpts = portal.get_qe_input()

    sim = DFT(atoms)

    # Check calculation type (e.g. relax, scf, etc.)
    calc_type = input_data.get("control", {}).get("calculation")
    print(f"calc_type = {calc_type}")
    if calc_type == "relax":
        sim.relax(
            input_data = input_data,
            kpts = kpts
        )
    elif calc_type == "scf":
        sim.scf(
            input_data = input_data,
            kpts = kpts
        )
    elif calc_type == "bands":
        sim.bands(
            input_data = input_data,
            band_kpts = kpts
        )

if __name__ == "__main__":
    main()
