from prysa.core.abstractions import RuffLinter, PylintLinter

LINTER_MAP = {
    "ruff": RuffLinter(),
    "pylint": PylintLinter(),
}

def get_linter(name: str):
    name = name.lower()
    if name not in LINTER_MAP:
        raise ValueError(f"Unknown linter: {name}")
    return LINTER_MAP[name]
