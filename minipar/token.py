from dataclasses import dataclass


@dataclass
class Token:
    label: str
    value: str
