"""
Módulo de formatação de datas e tempos
"""
from datetime import datetime, date, timedelta
from typing import Optional, Union
import locale
from babel.dates import format_date, format_datetime, format_time


def format_relative(
    date_obj: Union[date, datetime],
    reference_date: Optional[Union[date, datetime]] = None,
    locale_str: str = "pt_BR"
) -> str:
    """
    Formata uma data de forma relativa (ex: "há 2 horas", "ontem").
    
    Args:
        date_obj (Union[date, datetime]): Data a ser formatada
        reference_date (Optional[Union[date, datetime]]): Data de referência (padrão: agora)
        locale_str (str): Localidade para formatação
        
    Returns:
        str: Data formatada de forma relativa
    """
    if reference_date is None:
        reference_date = datetime.now()
    
    if isinstance(date_obj, date) and not isinstance(date_obj, datetime):
        date_obj = datetime.combine(date_obj, datetime.min.time())
    
    if isinstance(reference_date, date) and not isinstance(reference_date, datetime):
        reference_date = datetime.combine(reference_date, datetime.min.time())
    
    delta = reference_date - date_obj
    
    if delta.days == 0:
        if delta.seconds < 60:
            return "agora mesmo"
        elif delta.seconds < 3600:
            minutes = delta.seconds // 60
            return f"há {minutes} {'minuto' if minutes == 1 else 'minutos'}"
        else:
            hours = delta.seconds // 3600
            return f"há {hours} {'hora' if hours == 1 else 'horas'}"
    elif delta.days == 1:
        return "ontem"
    elif delta.days == -1:
        return "amanhã"
    elif delta.days < 7:
        return f"há {delta.days} {'dia' if delta.days == 1 else 'dias'}"
    elif delta.days < 30:
        weeks = delta.days // 7
        return f"há {weeks} {'semana' if weeks == 1 else 'semanas'}"
    elif delta.days < 365:
        months = delta.days // 30
        return f"há {months} {'mês' if months == 1 else 'meses'}"
    else:
        years = delta.days // 365
        return f"há {years} {'ano' if years == 1 else 'anos'}"


def format_custom(
    date_obj: Union[date, datetime],
    format_str: str,
    locale_str: str = "pt_BR"
) -> str:
    """
    Formata uma data usando um formato personalizado.
    
    Args:
        date_obj (Union[date, datetime]): Data a ser formatada
        format_str (str): String de formato
        locale_str (str): Localidade para formatação
        
    Returns:
        str: Data formatada
    """
    try:
        locale.setlocale(locale.LC_TIME, locale_str)
    except locale.Error:
        pass  # Mantém a localidade padrão se a especificada não estiver disponível
    
    if isinstance(date_obj, date) and not isinstance(date_obj, datetime):
        date_obj = datetime.combine(date_obj, datetime.min.time())
    
    return date_obj.strftime(format_str)


def format_natural(
    date_obj: Union[date, datetime],
    include_time: bool = True,
    locale_str: str = "pt_BR"
) -> str:
    """
    Formata uma data de forma natural (ex: "25 de fevereiro de 2024").
    
    Args:
        date_obj (Union[date, datetime]): Data a ser formatada
        include_time (bool): Se deve incluir a hora
        locale_str (str): Localidade para formatação
        
    Returns:
        str: Data formatada de forma natural
    """
    if isinstance(date_obj, date) and not isinstance(date_obj, datetime):
        date_obj = datetime.combine(date_obj, datetime.min.time())
    
    if include_time:
        return format_datetime(date_obj, format="long", locale=locale_str)
    else:
        return format_date(date_obj, format="long", locale=locale_str)


def format_iso(
    date_obj: Union[date, datetime],
    include_time: bool = True
) -> str:
    """
    Formata uma data no formato ISO 8601.
    
    Args:
        date_obj (Union[date, datetime]): Data a ser formatada
        include_time (bool): Se deve incluir a hora
        
    Returns:
        str: Data formatada no padrão ISO 8601
    """
    if isinstance(date_obj, date) and not isinstance(date_obj, datetime):
        date_obj = datetime.combine(date_obj, datetime.min.time())
    
    if include_time:
        return date_obj.isoformat()
    else:
        return date_obj.date().isoformat()


def format_short(
    date_obj: Union[date, datetime],
    include_time: bool = True,
    locale_str: str = "pt_BR"
) -> str:
    """
    Formata uma data de forma curta (ex: "25/02/2024").
    
    Args:
        date_obj (Union[date, datetime]): Data a ser formatada
        include_time (bool): Se deve incluir a hora
        locale_str (str): Localidade para formatação
        
    Returns:
        str: Data formatada de forma curta
    """
    if isinstance(date_obj, date) and not isinstance(date_obj, datetime):
        date_obj = datetime.combine(date_obj, datetime.min.time())
    
    if include_time:
        return format_datetime(date_obj, format="short", locale=locale_str)
    else:
        return format_date(date_obj, format="short", locale=locale_str) 