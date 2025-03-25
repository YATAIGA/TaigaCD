import sys
import os
import json

# 將專案根目錄加入 Python 模組搜尋路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)

# noqa: E402
from taigacd.structure.factory import get_structure_builder  # noqa: E402


def validate_json(json_file: str):
    errors = []

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"JSON 格式錯誤: {e}")
        return False, errors

    if "material" not in data:
        errors.append("缺少'material'欄位")
    else:
        material = data["material"]
        required_material_keys = ["formula", "type", "crystal_structure"]
        for key in required_material_keys:
            if key not in material:
                errors.append(f"material 欄位缺少 '{key}'")

    if "calculation" not in data:
        errors.append("缺少'calculation'欄位")
    else:
        calculation = data["calculation"]
        if "type" not in calculation:
            errors.append("calculation 欄位缺少 'type'")
        if "parameters" not in calculation:
            errors.append("calculation 欄位缺少 'parameters'")
        else:
            parameters = calculation["parameters"]
            required_calc_keys = [
                "workflow", "ecutwfc", "ecutrho",
                "pseudopotential", "kpoints"
            ]
            for key in required_calc_keys:
                if key not in parameters:
                    errors.append(f"parameters 欄位缺少 '{key}'")

    if "material" in data:
        try:
            structure_params = {
                "formula": material["formula"],
                "crystal_structure": material["crystal_structure"],
                "lattice": material.get("lattice", {"a": 5.431})
            }
            builder = get_structure_builder("crystal")
            _ = builder.build(structure_params)
        except Exception as e:
            errors.append(f"結構建置失敗: {e}")

    if errors:
        return False, errors
    return True, ["JSON 檔案正確且有效。"]


if __name__ == "__main__":
    json_file = sys.argv[1]

    is_valid, messages = validate_json(json_file)
    if is_valid:
        print("✅ JSON 驗證成功！")
    else:
        print("❌ JSON 驗證失敗，錯誤訊息如下：")
        for msg in messages:
            print(f"- {msg}")
