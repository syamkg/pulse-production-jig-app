import enum


class Target(str, enum.Enum):
    TA3K = "ta3k"
    PULSE_R1B_PHASE_1 = "pulse-r1b-p1"
    PULSE_R1B_PHASE_2 = "pulse-r1b-p2"
    FAKE = "fake"
