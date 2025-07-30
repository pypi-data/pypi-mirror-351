#-------------------- Imports --------------------

from abc import ABC, abstractmethod
from functools import lru_cache
from importlib.resources import files
from dataclasses import dataclass

import re

#-------------------- Common Passwords & Blacklist --------------------

PACKAGE_NAME = "advanced_password_validator.data"

@lru_cache(maxsize=1)
def get_passwords_list() -> set[str]:
    try:
        data_path = files(PACKAGE_NAME).joinpath("common_passwords.txt")
        data = data_path.read_text(encoding='utf-8')
        return set(word.lower() for word in data.splitlines())
    except FileNotFoundError as err:
        return set()
    
@lru_cache(maxsize=1)
def get_blacklist() -> set[str]:
    try:
        data_path = files(PACKAGE_NAME).joinpath("blacklist.txt")
        data = data_path.read_text(encoding='utf-8')
        return set(word.lower() for word in data.splitlines())
    except FileNotFoundError as err:
        return set()

#-------------------- Validator Rules --------------------


class BaseRule(ABC):
    code: str = "base_rule"

    @abstractmethod
    def validate(self, password: str) -> bool:
        """
        Returns True is the password passes all specified rules
        """
        raise NotImplementedError
    
    @abstractmethod
    def message(self) -> str:
        """
        Returns the apporpriate Error message if validation fails
        """
        raise NotImplementedError
    
    def __str__(self):
        return self.message()
    

@dataclass
class MinLengthRule(BaseRule):
    min_length: int = 8
    _message: str = None
    code: str = "min_length"

    def validate(self, password: str) -> bool:
        if password is None:
            raise ValueError(f"Password can not be None: {self.code}")
  
        return len(password) >= self.min_length
    
    def message(self):
        return self._message or f"Password must be at least {self.min_length} characters long"


@dataclass
class MaxLengthRule(BaseRule):
    max_length: int = 65
    _message: str = None
    code: str = "max_length"

    def validate(self, password: str) -> bool:
        if password is None:
            raise ValueError(f"Password can not be None: {self.code}")

        return len(password) <= self.max_length
    
    def message(self):
        return self._message or f"Passwords must be under {self.max_length} characters long"


@dataclass
class UppercaseRule(BaseRule):
    _message: str = None
    code: str = "uppercase_required"

    def validate(self, password: str) -> bool:
        if password is None:
            raise ValueError(f"Password can not be None: {self.code}")

        return any(c.isupper() for c in password)
    
    def message(self):
        return self._message or "Password must include at least one uppercase character"


@dataclass
class NumbersRule(BaseRule):
    _message: str = None
    code: str = "digit_required"

    def validate(self, password: str) -> bool:
        if password is None:
            raise ValueError(f"Password can not be None: {self.code}")

        return any(c.isdigit() for c in password)
    
    def message(self):
        return self._message or "Password must include at least one digit (0 - 9)"


@dataclass
class SymbolsRule(BaseRule):
    _message: str = None
    code: str = "symbol_required"

    def validate(self, password: str) -> bool:
        if password is None:
            raise ValueError(f"Password can not be None: {self.code}")

        return bool(re.search(r"[!\"#$%&'()*+,\-./:;<=>?@[\\\]^_`{|}~]", password))
    
    def message(self):
        return self._message or "Password must include at least one special character/symbol"


@dataclass
class NoSpacesRule(BaseRule):
    _message: str = None
    code: str = "no_space_allowed"

    def validate(self, password: str) -> bool:
        if password is None:
            raise ValueError(f"Password can not be None: {self.code}")

        return not bool(re.search(r"\s", password))
    
    def message(self):
        return self._message or "Password must not include spaces"
    

@dataclass
class MustIncludeCharRule(BaseRule):
    character: str = None
    _message: str = None
    code: str = "must_include_character"

    def validate(self, password: str) -> bool:
        if password is None:
            raise ValueError(f"Password can not be None: {self.code}")
        
        return True if self.character in password else False
    
    def message(self):
        return self._message or f"Password must include the specified character: {self.character}"
    

@dataclass
class NoRepeatingCharsRule(BaseRule):
    repeating_limit: int = 3
    _message: str = None
    code: str = "no_repeating_chars"

    def validate(self, password: str) -> bool:
        if password is None:
            raise ValueError(f"Password can not be None: {self.code}")

        if not password:
            return True
        
        count = 1

        for i in range(1, len(password)):
            if password[i] == password[i - 1]:
                count += 1
                if count >= self.repeating_limit:
                    return False
            else:
                count = 1
        
        return True
    
    def message(self):
        return self._message or f"Password must not include more than {self.repeating_limit} repeating characters"
    

@dataclass
class BlacklistRule(BaseRule):
    _message: str = None
    code: str = "blacklisted_password"
    
    def validate(self, password: str) -> bool:
        if password is None:
            raise ValueError(f"Password can not be None: {self.code}")
        
        blacklist = get_blacklist()
        password_lower = password.lower()
        return not any(blacklisted in password_lower for blacklisted in blacklist)
        
    def message(self):
        return self._message or "Password includes a blacklisted string pattern"


@dataclass
class MostCommonPasswordsRule(BaseRule):
    _message: str = None
    code: str = "common_password"

    def validate(self, password: str) -> bool:
        if password is None:
            raise ValueError(f"Password can not be None: {self.code}")
        
        common_list = {p.lower() for p in get_passwords_list()}
        return password.lower() not in common_list
    
    def message(self):
        return self._message or "Password is too common and easy to guess"