"""Модуль с тестами регистратора команд"""

import unittest
from pproto_py import Command


class TestCommandRegistrar(unittest.TestCase):
    """Тесты для проверки работы реестра команд"""

    def setUp(self) -> None:
        """Обнуляем список имен и id комманд перед каждым тестом"""
        Command.commands_names = []
        Command.commands_uuids = []

    def test_command_registartion(self) -> None:
        """Регистрация уникальных комманд должна происходить без ошибок"""
        Command("SOME_COMMAND_1", "86491a9a-f270-4ac1-835a-0618060393e6")
        Command("SOME_COMMAND_2", "07D720BA-759F-4AE8-95DF-4d3312a7e6a0")

    def test_dublicat_name(self) -> None:
        """При регистрации команды с не уникальным именем, должно выбрасываться исключение"""
        Command("SOME_COMMAND_1", "86491a9a-f270-4ac1-835a-0618060393e6")
        with self.assertRaises(ValueError):
            Command("SOME_COMMAND_1", "07D720BA-759F-4AE8-95DF-4d3312a7e6a0")

    def test_dublicat_uuid(self) -> None:
        """При регистрации команды с не уникальным id, должно выбрасываться исключение"""
        Command("SOME_COMMAND_1", "86491a9a-f270-4ac1-835a-0618060393e6")
        with self.assertRaises(ValueError):
            Command("SOME_COMMAND_2", "86491a9a-f270-4ac1-835a-0618060393e6")

    def test_dublicat_command(self) -> None:
        """При повторной регистрации команды, должно выбрасываться исключение"""
        Command("SOME_COMMAND_1", "86491a9a-f270-4ac1-835a-0618060393e6")
        with self.assertRaises(ValueError):
            Command("SOME_COMMAND_1", "86491a9a-f270-4ac1-835a-0618060393e6")


if __name__ == "__main__":
    unittest.main()
