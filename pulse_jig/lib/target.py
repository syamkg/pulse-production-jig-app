import enum


class Target(str, enum.Enum):
    TA3K = "ta3k"
    TA6K = "ta6k"
    TA11K = "ta11k"
    PULSE_PHASE_1 = "pulse-phase1"
    PULSE_PHASE_2 = "pulse-phase2"
    PULSE_PHASE_3 = "pulse-phase3"
