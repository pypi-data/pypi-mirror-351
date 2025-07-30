from prysa.core.abstractions import PoetryManager, PipManager, UvManager

MANAGER_MAP = {
    "poetry": PoetryManager(),
    "pip": PipManager(),
    "uv": UvManager(),
}

def get_manager(name: str):
    name = name.lower()
    if name not in MANAGER_MAP:
        raise ValueError(f"Unknown dependency manager: {name}")
    return MANAGER_MAP[name]
