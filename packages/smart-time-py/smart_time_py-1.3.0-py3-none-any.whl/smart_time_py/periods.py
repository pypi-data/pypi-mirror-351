"""
Módulo de períodos e intervalos de tempo
"""
from datetime import datetime, date, timedelta
from typing import Optional, Union, List, Dict
from dataclasses import dataclass
from enum import Enum


class PeriodType(Enum):
    """Tipos de períodos temporais"""
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    CUSTOM = "custom"


@dataclass
class TimePeriod:
    """
    Representa um período de tempo com início e fim.
    """
    start: Union[date, datetime]
    end: Union[date, datetime]
    name: Optional[str] = None
    period_type: PeriodType = PeriodType.CUSTOM
    
    def __post_init__(self):
        """Valida o período após a inicialização."""
        if self.end < self.start:
            raise ValueError("A data final deve ser posterior à data inicial")
    
    @property
    def duration(self) -> timedelta:
        """Retorna a duração do período."""
        return self.end - self.start
    
    @property
    def days(self) -> int:
        """Retorna o número de dias do período."""
        return self.duration.days
    
    def contains(self, date_obj: Union[date, datetime]) -> bool:
        """
        Verifica se uma data está dentro do período.
        
        Args:
            date_obj (Union[date, datetime]): Data a ser verificada
            
        Returns:
            bool: True se a data estiver dentro do período, False caso contrário
        """
        return self.start <= date_obj <= self.end
    
    def overlaps(self, other: 'TimePeriod') -> bool:
        """
        Verifica se este período sobrepõe outro período.
        
        Args:
            other (TimePeriod): Outro período a ser verificado
            
        Returns:
            bool: True se houver sobreposição, False caso contrário
        """
        return (
            self.start <= other.end and
            other.start <= self.end
        )
    
    def intersection(self, other: 'TimePeriod') -> Optional['TimePeriod']:
        """
        Retorna a interseção entre este período e outro.
        
        Args:
            other (TimePeriod): Outro período
            
        Returns:
            Optional[TimePeriod]: Período de interseção ou None se não houver interseção
        """
        if not self.overlaps(other):
            return None
        
        start = max(self.start, other.start)
        end = min(self.end, other.end)
        return TimePeriod(start=start, end=end)
    
    def union(self, other: 'TimePeriod') -> 'TimePeriod':
        """
        Retorna a união entre este período e outro.
        
        Args:
            other (TimePeriod): Outro período
            
        Returns:
            TimePeriod: Período união
        """
        start = min(self.start, other.start)
        end = max(self.end, other.end)
        return TimePeriod(start=start, end=end)
    
    def split(self, interval: timedelta) -> List['TimePeriod']:
        """
        Divide o período em subperíodos de tamanho igual.
        
        Args:
            interval (timedelta): Intervalo de tempo para divisão
            
        Returns:
            List[TimePeriod]: Lista de subperíodos
        """
        periods = []
        current_start = self.start
        
        while current_start < self.end:
            current_end = min(current_start + interval, self.end)
            periods.append(TimePeriod(
                start=current_start,
                end=current_end
            ))
            current_start = current_end
        
        return periods


class DateRange:
    """
    Classe para representar um intervalo de datas com funcionalidades avançadas.
    """
    def __init__(
        self,
        start: Union[date, datetime],
        end: Union[date, datetime],
        include_weekends: bool = True
    ):
        """
        Inicializa o intervalo de datas.
        
        Args:
            start (Union[date, datetime]): Data inicial
            end (Union[date, datetime]): Data final
            include_weekends (bool): Se deve incluir finais de semana
        """
        self.start = start
        self.end = end
        self.include_weekends = include_weekends
    
    def __iter__(self):
        """Iterador sobre as datas do intervalo."""
        current = self.start
        while current <= self.end:
            if self.include_weekends or current.weekday() < 5:
                yield current
            current += timedelta(days=1)
    
    def __len__(self) -> int:
        """Retorna o número de dias no intervalo."""
        return sum(1 for _ in self)
    
    def to_list(self) -> List[Union[date, datetime]]:
        """Converte o intervalo para uma lista de datas."""
        return list(self)
    
    def filter(self, condition) -> List[Union[date, datetime]]:
        """
        Filtra as datas do intervalo baseado em uma condição.
        
        Args:
            condition: Função que recebe uma data e retorna um booleano
            
        Returns:
            List[Union[date, datetime]]: Lista de datas filtradas
        """
        return [date for date in self if condition(date)]
    
    def group_by_week(self) -> Dict[int, List[Union[date, datetime]]]:
        """
        Agrupa as datas por semana.
        
        Returns:
            Dict[int, List[Union[date, datetime]]]: Datas agrupadas por semana
        """
        weeks = {}
        for date in self:
            week = date.isocalendar()[1]
            if week not in weeks:
                weeks[week] = []
            weeks[week].append(date)
        return weeks
    
    def group_by_month(self) -> Dict[int, List[Union[date, datetime]]]:
        """
        Agrupa as datas por mês.
        
        Returns:
            Dict[int, List[Union[date, datetime]]]: Datas agrupadas por mês
        """
        months = {}
        for date in self:
            month = date.month
            if month not in months:
                months[month] = []
            months[month].append(date)
        return months


def get_overlapping_periods(
    periods: List[TimePeriod]
) -> List[TimePeriod]:
    """
    Retorna os períodos de sobreposição entre múltiplos períodos.
    
    Args:
        periods (List[TimePeriod]): Lista de períodos
        
    Returns:
        List[TimePeriod]: Lista de períodos de sobreposição
    """
    if not periods:
        return []
    
    # Ordena os períodos por data de início
    sorted_periods = sorted(periods, key=lambda p: p.start)
    
    overlapping = []
    current_overlap = sorted_periods[0]
    
    for period in sorted_periods[1:]:
        if current_overlap.overlaps(period):
            current_overlap = current_overlap.intersection(period)
        else:
            if current_overlap:
                overlapping.append(current_overlap)
            current_overlap = period
    
    if current_overlap:
        overlapping.append(current_overlap)
    
    return overlapping 