"""Модуль тестов для парсера команд."""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../src'))
)
from main import parse_command


class TestParser(unittest.TestCase):
    """Тесты для функции parse_command."""

    def test_simple_args(self):
        """Тест простых аргументов через пробел."""
        self.assertEqual(parse_command("ls -l"), ["ls", "-l"])

    def test_quoted_args(self):
        """Тест аргументов в кавычках."""
        raw = 'cd "my secret folder"'
        expected = ["cd", "my secret folder"]
        self.assertEqual(parse_command(raw), expected)

    def test_invalid_quotes(self):
        """Тест невалидных кавычек."""
        self.assertIsNone(parse_command('cd "unclosed'))


if __name__ == "__main__":
    unittest.main()