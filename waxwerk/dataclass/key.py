from dataclasses import dataclass
from waxwerk.enums.key_enums import Tonic, Mode, CamelotKey, get_camelot_from_tonic_and_mode

@dataclass
class Key:
    tonic: Tonic
    mode: Mode
    camelot: CamelotKey = None

    def __post_init__(self):
        self.camelot = get_camelot_from_tonic_and_mode(self.tonic, self.mode)

    def __str__(self):
        return f"[{self.tonic} {self.mode}] [{self.camelot}]"

    def __repr__(self):
        return f"[{self.tonic} {self.mode}] [{self.camelot}]"