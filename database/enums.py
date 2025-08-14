import enum


class SolvedStatus(enum.IntEnum):
    ERROR = -2
    NOT_SOLVED = -1
    UNSOLVED = 0
    SOLVED = 1


class Difficulty(enum.IntEnum):
    UNKNOWN = 0
    EASY = 1
    MEDIUM = 2
    HARD = 3
    VERY_HARD = 4
