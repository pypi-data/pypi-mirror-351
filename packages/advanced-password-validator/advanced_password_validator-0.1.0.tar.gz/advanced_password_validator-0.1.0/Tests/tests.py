import unittest

from src.validator import PasswordValidator
from src.mode import Mode

validator = PasswordValidator(
    min_length=8,
    max_length=65,
    require_uppercase=True,
    require_numbers=True,
    require_symbols=True,
    no_spaces=True
    )

common_validator = PasswordValidator(
    not_common=True,
)

test_password1 = "MegaSecret10+"
test_password2 = "megasecret"
test_password3 = "MegaSecret10"
test_password4 = "MegaSecret+"
test_password5 = "SuperSecret10+"
test_password6 = "Super Secret10+"
test_password7 = "Super_Secret10+"
test_password8 = "biggessecretever"
test_password10 = "iloveyou21"
test_password11 = "taishan2011"
test_password12 = "sephiroth"


class MyTestCase(unittest.TestCase):
    def test_example(self):
        # Ordinary tests
        valid1, errors1 = validator.validate(test_password1)
        self.assertTrue(valid1, msg=f"Unexpacted failure - got error: {errors1}")
        valid2, errors2 = validator.validate(test_password2)
        self.assertFalse(valid2, msg=f"Unexpacted failure - got error: {errors2}")
        valid3, errors3 = validator.validate(test_password3)
        self.assertFalse(valid3, msg=f"Unexpacted failure - got error: {errors3}")
        valid4, errors4 = validator.validate(test_password4)
        self.assertFalse(valid4, msg=f"Unexpacted failure - got error: {errors4}")
        valid5, errors5 = validator.validate(test_password5)
        self.assertTrue(valid5, msg=f"Unexpacted failure - got error: {errors5}")
        valid6, errors6 = validator.validate(test_password6)
        self.assertFalse(valid6, msg=f"Unexpacted failure - got error: {errors6}")
        valid7, errors7 = validator.validate(test_password7)
        self.assertTrue(valid7, msg=f"Unexpacted failure - got error: {errors7}")
        valid8, errors8 = validator.validate(test_password8)
        self.assertFalse(valid8, msg=f"Unexpacted failure - got error: {errors8}")

        #Most Common Passwords List Test
        valid9, errors9 = common_validator.validate(test_password1)
        self.assertTrue(valid9, msg=f"Unexpacted failure - got error: {errors9}")
        valid10, errors10 = common_validator.validate(test_password10)
        self.assertFalse(valid10, msg=f"Unexpacted failure - got error: {errors10}")
        valid11, errors11 = common_validator.validate(test_password11)
        self.assertFalse(valid11, msg=f"Unexpacted failure - got error: {errors11}")
        valid12, errors12 = common_validator.validate(test_password12)
        self.assertFalse(valid12, msg=f"Unexpacted failure - got error: {errors12}")
        
        
if __name__ == "__main__":
    unittest.main()