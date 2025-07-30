"""
Módulo de manipulação de fusos horários
"""
from datetime import datetime
from typing import Optional, Dict, List
import pytz
from dateutil import tz


def get_timezone_info(timezone_str: str) -> Dict:
    """
    Retorna informações sobre um fuso horário.
    
    Args:
        timezone_str (str): Nome do fuso horário (ex: "America/Sao_Paulo")
        
    Returns:
        Dict: Informações do fuso horário
    """
    try:
        tz_info = pytz.timezone(timezone_str)
        now = datetime.now(tz_info)
        
        return {
            "name": timezone_str,
            "offset": now.utcoffset().total_seconds() / 3600,
            "abbreviation": now.tzname(),
            "is_dst": now.dst() is not None,
            "current_time": now.strftime("%Y-%m-%d %H:%M:%S")
        }
    except pytz.exceptions.UnknownTimeZoneError:
        return None


def convert_timezone(
    date_obj: datetime,
    from_timezone: str,
    to_timezone: str
) -> Optional[datetime]:
    """
    Converte uma data de um fuso horário para outro.
    
    Args:
        date_obj (datetime): Data a ser convertida
        from_timezone (str): Fuso horário de origem
        to_timezone (str): Fuso horário de destino
        
    Returns:
        Optional[datetime]: Data convertida ou None se a conversão falhar
    """
    try:
        from_tz = pytz.timezone(from_timezone)
        to_tz = pytz.timezone(to_timezone)
        
        # Se a data não tiver fuso horário, assume o fuso de origem
        if date_obj.tzinfo is None:
            date_obj = from_tz.localize(date_obj)
        
        return date_obj.astimezone(to_tz)
    except (pytz.exceptions.UnknownTimeZoneError, ValueError):
        return None


def get_timezone_abbreviation(timezone_str: str) -> Optional[str]:
    """
    Retorna a abreviação do fuso horário.
    
    Args:
        timezone_str (str): Nome do fuso horário
        
    Returns:
        Optional[str]: Abreviação do fuso horário
    """
    try:
        tz_info = pytz.timezone(timezone_str)
        return datetime.now(tz_info).tzname()
    except pytz.exceptions.UnknownTimeZoneError:
        return None


def get_available_timezones() -> List[str]:
    """
    Retorna uma lista de todos os fusos horários disponíveis.
    
    Returns:
        List[str]: Lista de fusos horários
    """
    return pytz.all_timezones


def get_timezone_by_offset(offset_hours: float) -> List[str]:
    """
    Retorna os fusos horários com um determinado offset.
    
    Args:
        offset_hours (float): Offset em horas
        
    Returns:
        List[str]: Lista de fusos horários com o offset especificado
    """
    matching_timezones = []
    for tz_name in pytz.all_timezones:
        tz_info = pytz.timezone(tz_name)
        now = datetime.now(tz_info)
        tz_offset = now.utcoffset().total_seconds() / 3600
        
        if abs(tz_offset - offset_hours) < 0.1:  # Permite pequena margem de erro
            matching_timezones.append(tz_name)
    
    return matching_timezones


def is_dst_active(timezone_str: str) -> Optional[bool]:
    """
    Verifica se o horário de verão está ativo em um fuso horário.
    
    Args:
        timezone_str (str): Nome do fuso horário
        
    Returns:
        Optional[bool]: True se o horário de verão estiver ativo, False caso contrário
    """
    try:
        tz_info = pytz.timezone(timezone_str)
        return datetime.now(tz_info).dst() is not None
    except pytz.exceptions.UnknownTimeZoneError:
        return None


def get_local_timezone() -> str:
    """
    Retorna o fuso horário local do sistema.
    
    Returns:
        str: Nome do fuso horário local
    """
    return tz.tzlocal().key if hasattr(tz.tzlocal(), 'key') else str(tz.tzlocal())


def get_timezone_utc_offset(timezone_str: str) -> Optional[float]:
    """
    Retorna o offset UTC de um fuso horário em horas.
    
    Args:
        timezone_str (str): Nome do fuso horário
        
    Returns:
        Optional[float]: Offset em horas ou None se o fuso horário não existir
    """
    try:
        tz_info = pytz.timezone(timezone_str)
        return datetime.now(tz_info).utcoffset().total_seconds() / 3600
    except pytz.exceptions.UnknownTimeZoneError:
        return None 