"""Тесты для модуля флагов"""

import unittest
from pproto_py.flags import MsgFlag
from pproto_py.flags import Type, ExecStatus, Priority, Compression, SerializationFormat


class MsgFlagTests(unittest.TestCase):
    """Тесты для структуры хранения флагов"""

    def test_default_by_name(self) -> None:
        """Проверка значений по имени созданого по умолчанию флага"""
        flag = MsgFlag()
        self.assertEqual(flag.get_flag_value("type"), Type.Unknown)
        self.assertEqual(flag.get_flag_value("execStatus"), ExecStatus.Unknown)
        self.assertEqual(flag.get_flag_value("priority"), Priority.Normal)
        self.assertEqual(flag.get_flag_value("compression"), Compression.Disable)
        self.assertEqual(flag.get_flag_value("tagsIsEmpty"), 0)
        self.assertEqual(flag.get_flag_value("maxTimeLifeIsEmpty"), 0)
        self.assertEqual(flag.get_flag_value("contentIsEmpty"), 1)
        self.assertEqual(flag.get_flag_value("reserved2"), 0)
        self.assertEqual(flag.get_flag_value("reserved3"), 0)
        self.assertEqual(flag.get_flag_value("contentFormat"), SerializationFormat.Json)
        self.assertEqual(flag.get_flag_value("reserved4"), 0)
        self.assertEqual(flag.get_flag_value("flags2IsEmpty"), 0)

    def test_default_by_order(self) -> None:
        """Проверка значений по имени созданого по умолчанию флага"""
        values = MsgFlag().values
        self.assertEqual(values[0].value, Type.Unknown)
        self.assertEqual(values[1].value, ExecStatus.Unknown)
        self.assertEqual(values[2].value, Priority.Normal)
        self.assertEqual(values[3].value, Compression.Disable)
        self.assertEqual(values[4].value, 0)
        self.assertEqual(values[5].value, 0)
        self.assertEqual(values[6].value, 1)
        self.assertEqual(values[7].value, 0)
        self.assertEqual(values[8].value, 0)
        self.assertEqual(values[9].value, SerializationFormat.Json)
        self.assertEqual(values[10].value, 0)
        self.assertEqual(values[11].value, 0)

    def test_change_flag_value(self) -> None:
        """Проверка работы изменения флагов"""
        flag = MsgFlag()
        default_digit = flag.get_digit()
        flag.set_flag_value("execStatus", ExecStatus.Success)
        new_digit = flag.get_digit()
        self.assertNotEqual(default_digit, new_digit)

    def test_digit(self) -> None:
        """Проверка работы методов get_digit и from_digit"""
        flag = MsgFlag()
        digit = flag.get_digit()
        self.assertEqual(flag.get_digit(), MsgFlag.from_digit(digit).get_digit())


if __name__ == "__main__":
    unittest.main()
