#-------------------- Imports --------------------

from rules import *
from mode import Mode
from typing import Optional, Tuple, List, Dict

#-------------------- PasswordValidator Object --------------------


class PasswordValidator:
    def __init__(
        self,
        min_length: int = None,
        max_length: int = None,
        require_uppercase: bool = False,
        require_numbers: bool = False,
        require_symbols: bool = False,
        no_spaces: bool = False,
        must_include_char: str = None,
        no_repeating_chars: int = None,
        blacklisted_pattern: bool = False,
        not_common: bool = False,
        mode: Optional[Mode] = None
    ):
        self.rules = []

        if mode == Mode.lenient:
            min_length = 8
            max_length = 65
            require_uppercase = False
            require_numbers = False
            require_symbols = False
            no_spaces = False
            must_include_char = None
            no_repeating_chars = None
            blacklisted_pattern = False
            not_common = False

        elif mode == Mode.moderate:
            min_length = 8
            max_length = 65
            require_uppercase = True
            require_numbers = True
            require_symbols = False
            no_spaces = True
            must_include_char = None
            no_repeating_chars = 4
            blacklisted_pattern = False
            not_common = False
            
        elif mode == Mode.strict:
            min_length = 12
            max_length = 65
            require_uppercase = True
            require_numbers = True
            require_symbols = True
            no_spaces = True
            must_include_char = None
            no_repeating_chars = 3
            blacklisted_pattern = True
            not_common = True

        if min_length is not None:
            self.rules.append(MinLengthRule(min_length=min_length))
        
        if max_length is not None:
            self.rules.append(MaxLengthRule(max_length=max_length))

        if require_uppercase:
            self.rules.append(UppercaseRule())

        if require_numbers:
            self.rules.append(NumbersRule())

        if require_symbols:
            self.rules.append(SymbolsRule())

        if no_spaces:
            self.rules.append(NoSpacesRule())

        if must_include_char is not None:
            self.rules.append(MustIncludeCharRule(character=must_include_char))

        if no_repeating_chars is not None:
            self.rules.append(NoRepeatingCharsRule(repeating_limit=no_repeating_chars))

        if blacklisted_pattern:
            self.rules.append(BlacklistRule())

        if not_common:
            self.rules.append(MostCommonPasswordsRule())

    def validate(self, password: str = None) -> Tuple[bool, List[Dict[str, str]]]:
        errors = [
            {"code": rule.code, "message": rule.message()}
            for rule in self.rules if not rule.validate(password)
        ]
        return len(errors) == 0, errors
