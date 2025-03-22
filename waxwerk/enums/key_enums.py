from enum import Enum

class Tonic(Enum):
    C = "C"
    C_SHARP = "C#"
    D = "D"
    D_SHARP = "D#"
    E = "E"
    F = "F"
    F_SHARP = "F#"
    G = "G"
    G_SHARP = "G#"
    A = "A"
    A_SHARP = "A#"
    B = "B"

class Mode(Enum):
    MAJOR = "major"
    MINOR = "minor"

class CamelotKey(Enum):
    _1A = "1A"
    _2A = "2A"
    _3A = "3A"
    _4A = "4A"
    _5A = "5A"
    _6A = "6A"
    _7A = "7A"
    _8A = "8A"
    _9A = "9A"
    _10A = "10A"
    _11A = "11A"
    _12A = "12A"
    _1B = "1B"
    _2B = "2B"
    _3B = "3B"
    _4B = "4B"
    _5B = "5B"
    _6B = "6B"
    _7B = "7B"
    _8B = "8B"
    _9B = "9B"
    _10B = "10B"
    _11B = "11B"
    _12B = "12B"

def get_camelot_from_tonic_and_mode(tonic: Tonic, mode: Mode) -> CamelotKey:
    if mode == Mode.MAJOR:
        return {
            Tonic.C: CamelotKey._8B,
            Tonic.C_SHARP: CamelotKey._3B,
            Tonic.D: CamelotKey._10B,
            Tonic.D_SHARP: CamelotKey._5B,
            Tonic.E: CamelotKey._12B,
            Tonic.F: CamelotKey._7B,
            Tonic.F_SHARP: CamelotKey._2B,
            Tonic.G: CamelotKey._9B,
            Tonic.G_SHARP: CamelotKey._4B,
            Tonic.A: CamelotKey._11B,
            Tonic.A_SHARP: CamelotKey._6B,
            Tonic.B: CamelotKey._1B
        }[tonic]
    else:
        return {
            Tonic.C: CamelotKey._5A,
            Tonic.C_SHARP: CamelotKey._12A,
            Tonic.D: CamelotKey._7A,
            Tonic.D_SHARP: CamelotKey._2A,
            Tonic.E: CamelotKey._9A,
            Tonic.F: CamelotKey._4A,
            Tonic.F_SHARP: CamelotKey._11A,
            Tonic.G: CamelotKey._6A,
            Tonic.G_SHARP: CamelotKey._1A,
            Tonic.A: CamelotKey._8A,
            Tonic.A_SHARP: CamelotKey._3A,
            Tonic.B: CamelotKey._10A
        }[tonic]