from enum import Enum

class ReturnCode(Enum): 
    EXECUTED = 0
    COMMAND_NOT_FOUND = 1
    UNHANDLED_ERROR = 2

class PackageCode(Enum):
    FOUND = 0
    VERSION_INVALID = 1
    VERSION_MISMATCH = 2
    MISSING = 3
    ERROR = 4
