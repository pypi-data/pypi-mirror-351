from typing import Any


def remove_nulls(obj: Any) -> Any:
    """remove all null elements from object"""
    if isinstance(obj, dict):
        return {
            k: remove_nulls(v)
            for k, v in obj.items()
            if v is not None
        }
    elif isinstance(obj, list):
        return [remove_nulls(i) for i in obj if i is not None]
    return obj
