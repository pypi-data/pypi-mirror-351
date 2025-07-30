from prysa.core.abstractions import PytestTester, UnittestTester

TESTER_MAP = {
    "pytest": PytestTester(),
    "unittest": UnittestTester(),
}

def get_tester(name: str):
    name = name.lower()
    if name not in TESTER_MAP:
        raise ValueError(f"Unknown tester: {name}")
    return TESTER_MAP[name]
