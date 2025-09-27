from typing import Any, Mapping, MutableMapping

# Deep Merge Function for Main

def deep_merge(existing: Any, new: Any) -> Any:
    if new is None:
        return None

    if isinstance(new, list):
        return list(new)

    if isinstance(new, Mapping) and isinstance(existing, Mapping):
        out: MutableMapping[str, Any] = dict(existing)
        for key, value in new.items():
            if key in existing:
                out[key] = deep_merge(existing[key], value)
            else:
                out[key] = deep_merge(None, value) if isinstance(value, Mapping) else value
        return out

    return new 
