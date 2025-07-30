"""
Testes para o módulo smart_time_py
"""
import pytest
from datetime import datetime, date, timedelta
from smart_time_py.core.converter import (
    string_to_datetime,
    datetime_to_string,
    convert_to_format,
    convert_with_timezone
)
from smart_time_py.core.time_operations import (
    add_time,
    subtract_time,
    calculate_difference,
    is_leap_year,
    get_days_in_month
)
from smart_time_py.core.validation import (
    is_valid_date,
    auto_validate_date,
    validate_date_range
)
from smart_time_py.holidays import (
    is_holiday,
    add_holiday,
    remove_holiday,
    get_holidays
)
from smart_time_py.periods import (
    TimePeriod,
    DateRange,
    get_overlapping_periods
)
from smart_time_py.formatters import (
    format_relative,
    format_natural,
    format_iso
)
from smart_time_py.timezone import (
    get_timezone_info,
    convert_timezone,
    get_timezone_abbreviation
)


def test_string_to_datetime():
    """Testa a conversão de string para datetime"""
    result = string_to_datetime("2024-02-25 14:30:00", "%Y-%m-%d %H:%M:%S")
    assert isinstance(result, datetime)
    assert result.year == 2024
    assert result.month == 2
    assert result.day == 25
    assert result.hour == 14
    assert result.minute == 30


def test_datetime_to_string():
    """Testa a conversão de datetime para string"""
    date_obj = datetime(2024, 2, 25, 14, 30)
    result = datetime_to_string(date_obj, "%d/%m/%Y %H:%M")
    assert result == "25/02/2024 14:30"


def test_convert_to_format():
    """Testa a conversão entre formatos"""
    result = convert_to_format(
        "2024-02-25",
        "%Y-%m-%d",
        "%d/%m/%Y"
    )
    assert result == "25/02/2024"


def test_convert_with_timezone():
    """Testa a conversão com fuso horário"""
    result = convert_with_timezone(
        "2024-02-25 14:30:00",
        "America/Sao_Paulo"
    )
    assert isinstance(result, datetime)
    assert result.tzinfo is not None


def test_add_time():
    """Testa a adição de tempo"""
    date_obj = datetime(2024, 2, 25)
    result = add_time(date_obj, days=5)
    assert result == datetime(2024, 3, 1)


def test_subtract_time():
    """Testa a subtração de tempo"""
    date_obj = datetime(2024, 2, 25)
    result = subtract_time(date_obj, days=5)
    assert result == datetime(2024, 2, 20)


def test_calculate_difference():
    """Testa o cálculo de diferença entre datas"""
    date1 = datetime(2024, 2, 25)
    date2 = datetime(2024, 3, 1)
    result = calculate_difference(date1, date2, "days")
    assert result == 5


def test_is_leap_year():
    """Testa a verificação de ano bissexto"""
    assert is_leap_year(2024) is True
    assert is_leap_year(2023) is False


def test_get_days_in_month():
    """Testa o cálculo de dias no mês"""
    assert get_days_in_month(2024, 2) == 29  # Fevereiro em ano bissexto
    assert get_days_in_month(2023, 2) == 28  # Fevereiro em ano não bissexto


def test_is_valid_date():
    """Testa a validação de data"""
    assert is_valid_date("2024-02-25", "%Y-%m-%d") is True
    assert is_valid_date("2024-13-25", "%Y-%m-%d") is False


def test_auto_validate_date():
    """Testa a validação automática de data"""
    assert auto_validate_date("2024-02-25") is True
    assert auto_validate_date("25/02/2024") is True
    assert auto_validate_date("data inválida") is False


def test_validate_date_range():
    """Testa a validação de intervalo de datas"""
    start = datetime(2024, 2, 25)
    end = datetime(2024, 3, 1)
    assert validate_date_range(start, end) is True
    assert validate_date_range(end, start) is False


def test_holiday_functions():
    """Testa as funções de feriado"""
    # Testa feriado existente
    assert is_holiday(datetime(2024, 1, 1)) is True
    
    # Adiciona um novo feriado
    assert add_holiday(datetime(2024, 4, 1), "Dia da Mentira") is True
    
    # Verifica se o feriado foi adicionado
    assert is_holiday(datetime(2024, 4, 1)) is True
    
    # Remove o feriado
    assert remove_holiday(datetime(2024, 4, 1)) is True
    
    # Verifica se o feriado foi removido
    assert is_holiday(datetime(2024, 4, 1)) is False


def test_time_period():
    """Testa a classe TimePeriod"""
    period = TimePeriod(
        start=datetime(2024, 2, 25),
        end=datetime(2024, 3, 1)
    )
    
    assert period.days == 5
    assert period.contains(datetime(2024, 2, 28)) is True
    assert period.contains(datetime(2024, 3, 2)) is False


def test_date_range():
    """Testa a classe DateRange"""
    date_range = DateRange(
        start=datetime(2024, 2, 25),
        end=datetime(2024, 3, 1),
        include_weekends=False
    )
    
    assert len(date_range) == 5  # 5 dias úteis
    assert len(date_range.to_list()) == 5


def test_format_relative():
    """Testa a formatação relativa"""
    now = datetime.now()
    assert "agora mesmo" in format_relative(now)
    assert "ontem" in format_relative(now - timedelta(days=1))


def test_format_natural():
    """Testa a formatação natural"""
    date_obj = datetime(2024, 2, 25, 14, 30)
    result = format_natural(date_obj)
    assert "25" in result
    assert "fevereiro" in result
    assert "2024" in result


def test_format_iso():
    """Testa a formatação ISO"""
    date_obj = datetime(2024, 2, 25, 14, 30)
    result = format_iso(date_obj)
    assert result == "2024-02-25T14:30:00"


def test_timezone_functions():
    """Testa as funções de fuso horário"""
    # Testa informações do fuso horário
    tz_info = get_timezone_info("America/Sao_Paulo")
    assert tz_info is not None
    assert "name" in tz_info
    assert "offset" in tz_info
    
    # Testa conversão de fuso horário
    date_obj = datetime(2024, 2, 25, 14, 30)
    result = convert_timezone(
        date_obj,
        "America/Sao_Paulo",
        "Europe/London"
    )
    assert result is not None
    assert result.tzinfo is not None
    
    # Testa abreviação do fuso horário
    abbreviation = get_timezone_abbreviation("America/Sao_Paulo")
    assert abbreviation is not None 