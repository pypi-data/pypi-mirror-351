"""
Módulo para integração com calendários externos.
"""
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union

import pytz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from icalendar import Calendar, Event


class CalendarIntegration:
    """Classe base para integração com calendários externos."""
    
    def __init__(self):
        """Inicializa a integração com calendário."""
        self.credentials = None
        self.service = None

    def authenticate(self, credentials_path: str) -> bool:
        """
        Autentica com o serviço de calendário.
        
        Args:
            credentials_path: Caminho para o arquivo de credenciais.
            
        Returns:
            bool: True se a autenticação foi bem-sucedida, False caso contrário.
        """
        raise NotImplementedError("Método deve ser implementado pelas classes filhas")

    def get_events(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Obtém eventos do calendário no período especificado.
        
        Args:
            start_date: Data de início do período.
            end_date: Data de fim do período.
            
        Returns:
            List[Dict]: Lista de eventos encontrados.
        """
        raise NotImplementedError("Método deve ser implementado pelas classes filhas")

    def create_event(self, event_data: Dict) -> Dict:
        """
        Cria um novo evento no calendário.
        
        Args:
            event_data: Dicionário com os dados do evento.
            
        Returns:
            Dict: Dados do evento criado.
        """
        raise NotImplementedError("Método deve ser implementado pelas classes filhas")

    def update_event(self, event_id: str, event_data: Dict) -> Dict:
        """
        Atualiza um evento existente no calendário.
        
        Args:
            event_id: ID do evento a ser atualizado.
            event_data: Dicionário com os novos dados do evento.
            
        Returns:
            Dict: Dados do evento atualizado.
        """
        raise NotImplementedError("Método deve ser implementado pelas classes filhas")

    def delete_event(self, event_id: str) -> bool:
        """
        Remove um evento do calendário.
        
        Args:
            event_id: ID do evento a ser removido.
            
        Returns:
            bool: True se o evento foi removido com sucesso, False caso contrário.
        """
        raise NotImplementedError("Método deve ser implementado pelas classes filhas")


class GoogleCalendarIntegration(CalendarIntegration):
    """Implementação da integração com Google Calendar."""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self):
        """Inicializa a integração com Google Calendar."""
        super().__init__()
        self.token_path = Path.home() / '.smart_time_py' / 'token.json'
        self.token_path.parent.mkdir(exist_ok=True)

    def authenticate(self, credentials_path: str) -> bool:
        """
        Autentica com o Google Calendar.
        
        Args:
            credentials_path: Caminho para o arquivo de credenciais OAuth2.
            
        Returns:
            bool: True se a autenticação foi bem-sucedida, False caso contrário.
        """
        if os.path.exists(self.token_path):
            self.credentials = Credentials.from_authorized_user_file(
                str(self.token_path), self.SCOPES
            )

        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, self.SCOPES
                )
                self.credentials = flow.run_local_server(port=0)

            with open(self.token_path, 'w') as token:
                token.write(self.credentials.to_json())

        self.service = build('calendar', 'v3', credentials=self.credentials)
        return True

    def get_events(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Obtém eventos do Google Calendar no período especificado.
        
        Args:
            start_date: Data de início do período.
            end_date: Data de fim do período.
            
        Returns:
            List[Dict]: Lista de eventos encontrados.
        """
        if not self.service:
            raise ValueError("Serviço não inicializado. Execute authenticate() primeiro.")

        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=start_date.isoformat() + 'Z',
            timeMax=end_date.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        return events_result.get('items', [])

    def create_event(self, event_data: Dict) -> Dict:
        """
        Cria um novo evento no Google Calendar.
        
        Args:
            event_data: Dicionário com os dados do evento.
            
        Returns:
            Dict: Dados do evento criado.
        """
        if not self.service:
            raise ValueError("Serviço não inicializado. Execute authenticate() primeiro.")

        event = {
            'summary': event_data.get('summary', ''),
            'location': event_data.get('location', ''),
            'description': event_data.get('description', ''),
            'start': {
                'dateTime': event_data['start'].isoformat(),
                'timeZone': event_data.get('timezone', 'UTC'),
            },
            'end': {
                'dateTime': event_data['end'].isoformat(),
                'timeZone': event_data.get('timezone', 'UTC'),
            },
        }

        event = self.service.events().insert(
            calendarId='primary',
            body=event
        ).execute()

        return event

    def update_event(self, event_id: str, event_data: Dict) -> Dict:
        """
        Atualiza um evento existente no Google Calendar.
        
        Args:
            event_id: ID do evento a ser atualizado.
            event_data: Dicionário com os novos dados do evento.
            
        Returns:
            Dict: Dados do evento atualizado.
        """
        if not self.service:
            raise ValueError("Serviço não inicializado. Execute authenticate() primeiro.")

        event = {
            'summary': event_data.get('summary', ''),
            'location': event_data.get('location', ''),
            'description': event_data.get('description', ''),
            'start': {
                'dateTime': event_data['start'].isoformat(),
                'timeZone': event_data.get('timezone', 'UTC'),
            },
            'end': {
                'dateTime': event_data['end'].isoformat(),
                'timeZone': event_data.get('timezone', 'UTC'),
            },
        }

        event = self.service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=event
        ).execute()

        return event

    def delete_event(self, event_id: str) -> bool:
        """
        Remove um evento do Google Calendar.
        
        Args:
            event_id: ID do evento a ser removido.
            
        Returns:
            bool: True se o evento foi removido com sucesso, False caso contrário.
        """
        if not self.service:
            raise ValueError("Serviço não inicializado. Execute authenticate() primeiro.")

        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            return True
        except Exception:
            return False

    def export_to_ical(self, events: List[Dict], output_path: str) -> bool:
        """
        Exporta eventos para formato iCal.
        
        Args:
            events: Lista de eventos para exportar.
            output_path: Caminho do arquivo de saída.
            
        Returns:
            bool: True se a exportação foi bem-sucedida, False caso contrário.
        """
        try:
            cal = Calendar()
            cal.add('prodid', '-//Smart Time Py//Calendar Export//EN')
            cal.add('version', '2.0')

            for event in events:
                ical_event = Event()
                ical_event.add('summary', event.get('summary', ''))
                ical_event.add('location', event.get('location', ''))
                ical_event.add('description', event.get('description', ''))
                
                start = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                end = datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00'))
                
                ical_event.add('dtstart', start)
                ical_event.add('dtend', end)
                
                cal.add_component(ical_event)

            with open(output_path, 'wb') as f:
                f.write(cal.to_ical())
            return True
        except Exception:
            return False 