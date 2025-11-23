from typing import Any, Dict


def php_serialize_value(v: Any) -> str:
    if isinstance(v, bool):
        return f"b:{1 if v else 0};"
    if isinstance(v, int):
        return f"i:{v};"
    if isinstance(v, float):
        return f"d:{v};"
    if isinstance(v, str):
        return f"s:{len(v)}:\"{v}\";"
    if isinstance(v, dict):
        parts = []
        for k, val in v.items():
            parts.append(php_serialize_value(k))
            parts.append(php_serialize_value(val))
        return f"a:{len(v)}:{{" + "".join(parts) + "}"
    if isinstance(v, list):
        parts = []
        for i, val in enumerate(v):
            parts.append(f"i:{i};")
            parts.append(php_serialize_value(val))
        return f"a:{len(v)}:{{" + "".join(parts) + "}"
    return f"N;"


def php_serialize_object(class_name: str, props: Dict[str, Any]) -> str:
    parts = []
    for k, v in props.items():
        parts.append(f"s:{len(k)}:\"{k}\";")
        parts.append(php_serialize_value(v))
    body = "".join(parts)
    return f"O:{len(class_name)}:\"{class_name}\":{len(props)}:{{" + body + "}}"
