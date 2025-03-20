import nekoton as nt


def from_wei(value: int | nt.Tokens | float) -> float:
    return int(value) / 10**9

