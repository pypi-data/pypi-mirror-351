"""
Módulo de gerenciamento de feriados
"""
from datetime import datetime, date
from typing import Dict, List, Optional, Union
import json
import os
from pathlib import Path


class HolidayManager:
    def __init__(self, country: str = "BR"):
        """
        Inicializa o gerenciador de feriados.
        
        Args:
            country (str): Código do país (padrão: "BR" para Brasil)
        """
        self.country = country
        self.holidays: Dict[str, Dict] = {}
        self._load_holidays()
    
    def _load_holidays(self):
        """Carrega os feriados do arquivo de configuração."""
        config_path = Path(__file__).parent / "data" / "holidays.json"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self.holidays = json.load(f)
    
    def _save_holidays(self):
        """Salva os feriados no arquivo de configuração."""
        config_path = Path(__file__).parent / "data" / "holidays.json"
        os.makedirs(config_path.parent, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(self.holidays, f, ensure_ascii=False, indent=2)
    
    def is_holiday(self, date_obj: Union[date, datetime]) -> bool:
        """
        Verifica se uma data é feriado.
        
        Args:
            date_obj (Union[date, datetime]): Data a ser verificada
            
        Returns:
            bool: True se for feriado, False caso contrário
        """
        if isinstance(date_obj, datetime):
            date_obj = date_obj.date()
        
        date_str = date_obj.strftime("%Y-%m-%d")
        return date_str in self.holidays
    
    def get_holidays(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None
    ) -> List[Dict]:
        """
        Retorna a lista de feriados.
        
        Args:
            year (Optional[int]): Ano específico
            month (Optional[int]): Mês específico
            
        Returns:
            List[Dict]: Lista de feriados
        """
        holidays = []
        for date_str, holiday_info in self.holidays.items():
            holiday_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            if year and holiday_date.year != year:
                continue
            if month and holiday_date.month != month:
                continue
                
            holidays.append({
                "date": date_str,
                "name": holiday_info["name"],
                "type": holiday_info.get("type", "national")
            })
        
        return sorted(holidays, key=lambda x: x["date"])
    
    def add_holiday(
        self,
        date_obj: Union[date, datetime],
        name: str,
        holiday_type: str = "national"
    ) -> bool:
        """
        Adiciona um novo feriado.
        
        Args:
            date_obj (Union[date, datetime]): Data do feriado
            name (str): Nome do feriado
            holiday_type (str): Tipo do feriado (ex: "national", "regional", "local")
            
        Returns:
            bool: True se o feriado foi adicionado, False caso contrário
        """
        if isinstance(date_obj, datetime):
            date_obj = date_obj.date()
        
        date_str = date_obj.strftime("%Y-%m-%d")
        if date_str in self.holidays:
            return False
        
        self.holidays[date_str] = {
            "name": name,
            "type": holiday_type
        }
        self._save_holidays()
        return True
    
    def remove_holiday(self, date_obj: Union[date, datetime]) -> bool:
        """
        Remove um feriado.
        
        Args:
            date_obj (Union[date, datetime]): Data do feriado a ser removido
            
        Returns:
            bool: True se o feriado foi removido, False caso contrário
        """
        if isinstance(date_obj, datetime):
            date_obj = date_obj.date()
        
        date_str = date_obj.strftime("%Y-%m-%d")
        if date_str not in self.holidays:
            return False
        
        del self.holidays[date_str]
        self._save_holidays()
        return True
    
    def get_working_days(
        self,
        start_date: Union[date, datetime],
        end_date: Union[date, datetime]
    ) -> int:
        """
        Calcula o número de dias úteis entre duas datas.
        
        Args:
            start_date (Union[date, datetime]): Data inicial
            end_date (Union[date, datetime]): Data final
            
        Returns:
            int: Número de dias úteis
        """
        if isinstance(start_date, datetime):
            start_date = start_date.date()
        if isinstance(end_date, datetime):
            end_date = end_date.date()
        
        total_days = (end_date - start_date).days + 1
        holidays = 0
        
        current_date = start_date
        while current_date <= end_date:
            if self.is_holiday(current_date):
                holidays += 1
            current_date = date(
                current_date.year,
                current_date.month,
                current_date.day + 1
            )
        
        return total_days - holidays


# Instância global do gerenciador de feriados
holiday_manager = HolidayManager()

# Funções de conveniência
def is_holiday(date_obj: Union[date, datetime]) -> bool:
    """Verifica se uma data é feriado."""
    return holiday_manager.is_holiday(date_obj)

def get_holidays(year: Optional[int] = None, month: Optional[int] = None) -> List[Dict]:
    """Retorna a lista de feriados."""
    return holiday_manager.get_holidays(year, month)

def add_holiday(
    date_obj: Union[date, datetime],
    name: str,
    holiday_type: str = "national"
) -> bool:
    """Adiciona um novo feriado."""
    return holiday_manager.add_holiday(date_obj, name, holiday_type)

def remove_holiday(date_obj: Union[date, datetime]) -> bool:
    """Remove um feriado."""
    return holiday_manager.remove_holiday(date_obj)

def get_working_days(
    start_date: Union[date, datetime],
    end_date: Union[date, datetime]
) -> int:
    """Calcula o número de dias úteis entre duas datas."""
    return holiday_manager.get_working_days(start_date, end_date) 