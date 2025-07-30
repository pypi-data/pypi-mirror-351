#-------------------- Imports --------------------

from enum import Enum, auto

#-------------------- Mode Class --------------------


class Mode(Enum):
    lenient = auto()
    moderate = auto()
    strict = auto()