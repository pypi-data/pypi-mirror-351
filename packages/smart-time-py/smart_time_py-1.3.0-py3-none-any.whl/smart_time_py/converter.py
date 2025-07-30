from datetime import datetime

import pytz
from dateutil import parser
from dateutil.relativedelta import relativedelta


def string_to_datetime(date_str: str, date_format: str) -> datetime:
    """
    🕒 Converte uma string para um objeto datetime com o formato especificado.
    """
    try:
        return datetime.strptime(date_str, date_format)
    except ValueError as e:
        raise ValueError(f"❌ Erro na conversão: {str(e)}")


def datetime_to_string(date_obj: datetime, date_format: str) -> str:
    """
    📝 Converte um objeto datetime para uma string com o formato especificado.
    """
    if not isinstance(date_obj, datetime):
        raise TypeError("❌ O parâmetro 'date_obj' deve ser um objeto datetime.") # noqa501
    return date_obj.strftime(date_format)


def validate_date_string(date_str: str, date_format: str) -> bool:
    """
    ✅ Valida se uma string de data/hora corresponde ao formato especificado.
    """
    try:
        datetime.strptime(date_str, date_format)
        return True
    except ValueError:
        return False


# 🔄 Novos formatos de data/hora
def convert_to_format(date_str, from_format, to_format):
    """🔄 Converte uma string de data de um formato para outro."""
    try:
        date_obj = datetime.strptime(date_str, from_format)
        return date_obj.strftime(to_format)
    except ValueError:
        return None


def convert_with_timezone(date_str, timezone):
    """🌐 Converte uma data para o fuso horário especificado."""
    try:
        date_obj = parser.parse(date_str)
        target_timezone = pytz.timezone(timezone)
        return date_obj.astimezone(target_timezone)
    except Exception:
        return None


# ⏳ Manipulações de tempo
def add_time(date_obj, days=0, months=0, years=0):
    """➕ Adiciona dias, meses e anos a uma data."""
    return date_obj + relativedelta(days=days, months=months, years=years)


def subtract_time(date_obj, days=0, months=0, years=0):
    """➖ Subtrai dias, meses e anos de uma data."""
    return date_obj - relativedelta(days=days, months=months, years=years)


def calculate_difference(date1, date2, unit='days'):
    """📏 Calcula a diferença entre duas datas na unidade especificada."""
    delta = abs(date2 - date1)
    if unit == 'days':
        return delta.days
    elif unit == 'seconds':
        return delta.total_seconds()
    elif unit == 'minutes':
        return delta.total_seconds() / 60
    elif unit == 'hours':
        return delta.total_seconds() / 3600
    else:
        return None


# 🕐 Validações aprimoradas
def is_valid_date(date_str, date_format):
    """✅ Verifica se a string corresponde ao formato de data especificado."""
    try:
        datetime.strptime(date_str, date_format)
        return True
    except ValueError:
        return False


def auto_validate_date(date_str):
    """🤖 Tenta identificar automaticamente se uma string é uma data válida."""
    try:
        parser.parse(date_str)
        return True
    except ValueError:
        return False


# 🌟 Exemplos rápidos de uso
if __name__ == "__main__":
    dt = string_to_datetime("2025-02-24 14:30:00", "%Y-%m-%d %H:%M:%S")
    print("🕒 String para datetime:", dt)

    dt_str = datetime_to_string(dt, "%d/%m/%Y %H:%M")
    print("📝 Datetime para string:", dt_str)

    is_valid = validate_date_string("24/02/2025", "%d/%m/%Y")
    print("✅ String de data válida:", is_valid)

    print(convert_to_format("2025-02-25", "%Y-%m-%d", "%d/%m/%Y"))
    print(convert_with_timezone("2025-02-25 15:00:00", "America/Sao_Paulo"))
    print(add_time(datetime.now(), days=10, months=2))
    print(subtract_time(datetime.now(), years=1))
    print(calculate_difference(datetime(2025, 1, 1), datetime(2025, 2, 1)))
    print(is_valid_date("25/02/2025", "%d/%m/%Y"))
    print(auto_validate_date("February 25, 2025"))
