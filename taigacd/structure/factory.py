from .crystal import CrystalBuilder

BUILDER_MAP = {
    "crystal": CrystalBuilder,
    # 未來擴充其他結構建置方式
}


def get_structure_builder(structure_type: str):
    builder_cls = BUILDER_MAP.get(structure_type)
    if not builder_cls:
        raise ValueError(f"Unsupported structure type: {structure_type}")
    return builder_cls()
