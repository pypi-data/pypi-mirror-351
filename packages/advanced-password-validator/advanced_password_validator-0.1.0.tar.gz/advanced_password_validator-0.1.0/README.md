# 🔐 Advanced Password Validator


[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![PyPI - Coming Soon](https://img.shields.io/badge/PyPI-coming--soon-yellow)](https://pypi.org/)

---

> A dynamic, rule-based password validation system for Python. Supports configurable validation rules and pre-set security modes to suit different application needs.

## 🚀 Features

- ✅ Rule-based architecture — plug & play validation rules
- 🔁 Preconfigured modes: `lenient`, `moderate`, `strict`
- 🔒 Supports: min/max length, symbols, blacklist, common password checks, etc.
- 📂 Compare passwords to a list of over 30000 already-registered passwords for added security
- 🧪 Designed for unit testing & integration

---

## 📦 Installation

```python

pip install advanced_password_validator
poetry add advanced_password_validator

```

## 🌎 Code Usage:
> An overview of a common coding example utilizing the advanced_password_validator
to validate a password using customizable rules

```python
from advanced_password_validator import PasswordValidator, Mode

# Instantiate a validator object:
validator = PasswordValidator(
    min_length = 8,                     # Integer / Defaults to None
    max_length = 65,                    # Integer / Defaults to None
    require_uppercase = True,           # Boolean / Defaults to False
    require_numbers = True,             # Boolean / Defaults to False
    require_symbols = True,             # Boolean / Defaults to False
    no_spaces = True,                   # Boolean / Defaults to False
    must_include_char = None,           # String / Defaults to None
    no_repeating_chars = 5,             # Integer / Defaults to None
    blacklisted_pattern = False,        # Boolean / Defaults to False
    not_common = False,                 # Boolean / Defaults to False
    mode = None                         # Mode (Enum) / Defaults to None
)

# validate against password strings:
password_valid1 = validator.validate("ThisIsSuperValid123+")[0]
password_valid2 = validator.validate("nouppercase123+")[0]
password_valid3 = validator.validate("NoNumbers++")[0]

print(password_valid1)  # <= Returns True
print(password_valid2)  # <= Returns False
print(password_valid3)  # <= Returns False
```

## 0️⃣ Return Type
> The validate method returns a tuple: (bool, list) 
* [0] = a boolean value determining if the password passed the validation
* [1] = a list of errors based on what Rules the password didn't pass 
(the list will be empty if validation passes) 


## 📜 Rules Overview:
> A rudimentary overview of the rules that can enabled for custom validation

| **Rules**           |      **Description**                                                                                 |
|---------------------|-------------------------------------------------------------------------------------------------|
| min_length          | Specifies the minimum length required for the password (Integer)                                |
| max_length          | Specifies the maximum length possible for the password (Integer)                                |
| require_uppercase   | Specifies if the password must include at least 1 uppercase letter (Boolean)                    |
| require_numbers     | Specifies if the password must include at least 1 digit (Boolean)                               |
| require_symbols     | Specifies if the password must include at least 1 special character (Boolean)                   |
| no_spaces           | Specifies if the password can include spaces (Boolean)                                          |
| must_include_char   | Specifies one of more required characters in the password (String)                        |
| no_repeating_chars  | Specifies how many sequentially, repeating characters can be included in the password (Integer) |
| blacklisted_pattern | Specifies whether to check the password against a list of blacklisted patterns (Boolean)        |
| not_common          | Specifies whether to check the password against a list of commonly used passwords (Boolean)     |
| mode                | Specifies whether to use one of the 3 preconfigured modes (Mode)                                |


## 🤖 Preconfigured Modes:
> The advanced password validator package supports 3 preconfigured validator modes:
1. Lenient
2. Moderate
3. Strict
Each of these individual modes come preconfigured with different values, and are meant
to be utilised for quick out-of-the-box solutions.

```python
from advanced_password_validator import PasswordValidator, Mode

validator = PasswordValidator(
    mode=Mode.lenient
)
# The mode param takes in a Mode-object (Enum) - Mode.lenient, Mode.moderate, Mode.strict

```

**Lenient**
- min_length = 8
- max_length = 65

**Moderate**
- min_length = 8
- max_length = 65
- require_uppercase = True
- require_numbers = True
- no_spaces = True
- no_repeating_chars = 4

**Strict**
- min_length = 12
- max_length = 65
- require_uppercase = True
- require_numbers = True
- require_symbols = True
- no_spaces = True
- no_repeating_chars = 3
- blacklisted_pattern = True
- not_common = True


## 📄 License Details:
This project is licensed under the MIT License – see the LICENSE section for further details.
