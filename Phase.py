from enum import Enum

class Phase(Enum):
    CONFIRM = 0
    ROUTINE_CHECKS = 1
    DEBUGGING = 2
    SWAP = 4
    HOLD = 3
    FINISH = 5
