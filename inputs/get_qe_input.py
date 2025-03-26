def get_qe_input(
):
    """ ASE Espresso calculator input.

    Returns:
        input_data (dict)
        kpts (tuple | dict)
    """
    input_data = {
        "control": {
            "calculation": "relax",
            "prefix": "si",
            "pseudo_dir": "./pseudos",
            "outdir": "./tmp"
        },
        "system": {
            "ecutwfc": 40,
            "ecutrho": 320,
            "occupations": "smearing",
            "smearing": "mp",
            "degauss": 0.01
        },
        "electrons": {
            "conv_thr": 1e-6
        }
    }
    kpts = (8, 8, 8)

    return input_data, kpts
