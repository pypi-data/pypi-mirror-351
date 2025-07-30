import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime

from smart_time_py.converter import (add_time, auto_validate_date,
                                     calculate_difference, convert_to_format,
                                     convert_with_timezone, datetime_to_string,
                                     is_valid_date, string_to_datetime,
                                     subtract_time, validate_date_string)


def test_string_to_datetime():
    date_str = "2025-02-24 14:30:00"
    date_format = "%Y-%m-%d %H:%M:%S"
    resultado = string_to_datetime(date_str, date_format)
    assert resultado == datetime(2025, 2, 24, 14, 30)


def test_datetime_to_string():
    date_obj = datetime(2025, 2, 24, 14, 30)
    date_format = "%d/%m/%Y %H:%M"
    resultado = datetime_to_string(date_obj, date_format)
    assert resultado == "24/02/2025 14:30"


def test_validate_date_string():
    assert validate_date_string("24/02/2025", "%d/%m/%Y") is True
    assert validate_date_string("2025-02-24", "%d/%m/%Y") is False


def test_convert_to_format():
    resultado = convert_to_format("2025-02-25", "%Y-%m-%d", "%d/%m/%Y")
    assert resultado == "25/02/2025"


def test_convert_with_timezone():
    resultado = convert_with_timezone("2025-02-25 15:00:00", "America/Sao_Paulo")
    assert resultado.strftime("%Y-%m-%d %H:%M:%S %Z%z").endswith("-0300")


def test_add_time():
    base_date = datetime(2025, 1, 1)
    resultado = add_time(base_date, days=10, months=1)
    assert resultado == datetime(2025, 2, 11)


def test_subtract_time():
    base_date = datetime(2025, 2, 11)
    resultado = subtract_time(base_date, years=1)
    assert resultado == datetime(2024, 2, 11)


def test_calculate_difference():
    date1 = datetime(2025, 1, 1)
    date2 = datetime(2025, 2, 1)
    assert calculate_difference(date1, date2, "days") == 31
    assert calculate_difference(date1, date2, "hours") == 744


def test_is_valid_date():
    assert is_valid_date("25/02/2025", "%d/%m/%Y") is True
    assert is_valid_date("2025/02/25", "%d/%m/%Y") is False


def test_auto_validate_date():
    assert auto_validate_date("February 25, 2025") is True
    assert auto_validate_date("31/02/2025") is False


if __name__ == "__main__":
    pytest.main(["-v"])
