import unittest

from dicewarepy import diceware
from dicewarepy.diceware import wordlist


class TestDiceware(unittest.TestCase):
    def test_diceware(self):
        """The ``diceware`` function must return a list of strings."""
        words = diceware()
        for word in words:
            self.assertIsInstance(word, str)

    def test_diceware_default_language(self):
        """The ``diceware`` function must return the English wordlist by default."""
        english_wordlist = wordlist(language="en")

        words = diceware()
        for word in words:
            self.assertIn(word, english_wordlist.values())

    def test_diceware_language_english(self):
        """The ``diceware`` function must return a list of strings when the language parameter is set to ``en``."""
        words = diceware(language="en")
        for word in words:
            self.assertIsInstance(word, str)

    def test_diceware_language_german(self):
        """The ``diceware`` function must return a list of strings when the language parameter is set to ``de``."""
        words = diceware(language="de")
        for word in words:
            self.assertIsInstance(word, str)

    def test_diceware_language_not_string(self):
        """The ``diceware`` function must raise a ``TypeError`` when the language parameter is not a string."""
        self.assertRaises(TypeError, diceware, language=1)
        self.assertRaises(TypeError, diceware, language=1.5)
        self.assertRaises(TypeError, diceware, language=None)

    def test_diceware_language_invalid(self):
        """The ``diceware`` function must raise a ``ValueError`` when an invalid language code is provided."""
        self.assertRaises(ValueError, diceware, language="la")

    def test_diceware_length(self):
        """The ``diceware`` function must return a list of the correct length when the number of words is specified."""
        for i in range(1, 8 + 1):
            words = diceware(n=i)
            self.assertEqual(len(words), i)

    def test_diceware_length_default(self):
        """The ``diceware`` function must return a list of 6 words by default when no number is specified."""
        words = diceware()
        self.assertEqual(len(words), 6)

    def test_diceware_number_not_integer(self):
        """The ``diceware`` function must raise a ``TypeError`` when the specified number of words is not an integer."""
        self.assertRaises(TypeError, diceware, n=1.5)
        self.assertRaises(TypeError, diceware, n="one")
        self.assertRaises(TypeError, diceware, n=None)

    def test_diceware_length_less_than_one(self):
        """The ``diceware`` function must raise a ``ValueError`` when the specified number of words is less than 1."""
        self.assertRaises(ValueError, diceware, n=0)
        self.assertRaises(ValueError, diceware, n=-5)


if __name__ == "__main__":
    unittest.main()
