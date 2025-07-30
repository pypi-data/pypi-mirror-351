"""
Testes para o módulo de integração com calendários.
"""
from datetime import datetime, timedelta
from unittest.mock import Mock, mock_open, patch

import pytest

from smart_time_py.calendar_integration import (CalendarIntegration,
                                                GoogleCalendarIntegration)


@pytest.fixture
def mock_credentials():
    """Fixture para simular credenciais do Google."""
    return {
        'token': 'mock_token',
        'refresh_token': 'mock_refresh_token',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'client_id': 'mock_client_id',
        'client_secret': 'mock_client_secret',
        'scopes': ['https://www.googleapis.com/auth/calendar']
    }


@pytest.fixture
def mock_event():
    """Fixture para simular um evento do calendário."""
    return {
        'summary': 'Test Event',
        'location': 'Test Location',
        'description': 'Test Description',
        'start': {
            'dateTime': '2024-03-20T10:00:00Z',
            'timeZone': 'UTC'
        },
        'end': {
            'dateTime': '2024-03-20T11:00:00Z',
            'timeZone': 'UTC'
        }
    }


class TestCalendarIntegration:
    """Testes para a classe base CalendarIntegration."""

    def test_abstract_methods(self):
        """Testa se os métodos abstratos lançam NotImplementedError."""
        calendar = CalendarIntegration()
        
        with pytest.raises(NotImplementedError):
            calendar.authenticate('credentials.json')
        
        with pytest.raises(NotImplementedError):
            calendar.get_events(datetime.now(), datetime.now())
        
        with pytest.raises(NotImplementedError):
            calendar.create_event({})
        
        with pytest.raises(NotImplementedError):
            calendar.update_event('event_id', {})
        
        with pytest.raises(NotImplementedError):
            calendar.delete_event('event_id')


class TestGoogleCalendarIntegration:
    """Testes para a classe GoogleCalendarIntegration."""

    def test_authenticate_new_credentials(self):
        """Testa autenticação com novas credenciais."""
        mock_credentials = Mock()
        mock_credentials.valid = False
        mock_credentials.expired = False
        mock_credentials.refresh_token = None
        mock_credentials.to_json.return_value = '{}'

        mock_flow_instance = Mock()
        mock_flow_instance.run_local_server.return_value = mock_credentials

        # mock_service = Mock()  # Removido porque não é mais usado

        with patch(
            'google.oauth2.credentials.Credentials.from_authorized_user_file',
            return_value=mock_credentials
        ), patch(
            'google_auth_oauthlib.flow.InstalledAppFlow.'
            'from_client_secrets_file',
            return_value=mock_flow_instance
        ), patch(
            'smart_time_py.calendar_integration.build',
            return_value=Mock(),
            autospec=True
        ) as mock_build, patch(
            'builtins.open', mock_open(read_data='{}')
        ) as m_open:
            calendar = GoogleCalendarIntegration()
            result = calendar.authenticate('credentials.json')
            assert result is True
            mock_flow_instance.run_local_server.assert_called_once()
            mock_build.assert_called_once()
            m_open.assert_called()

    @patch('google.oauth2.credentials.Credentials.from_authorized_user_file')
    @patch('googleapiclient.discovery.build')
    def test_authenticate_existing_credentials(
        self, mock_build, mock_from_auth
    ):
        """Testa autenticação com credenciais existentes."""
        # Configurar mocks
        mock_credentials = Mock()
        mock_credentials.valid = True
        mock_from_auth.return_value = mock_credentials

        mock_service = Mock()
        mock_build.return_value = mock_service
        
        # Criar instância e testar
        calendar = GoogleCalendarIntegration()
        result = calendar.authenticate('credentials.json')
        
        assert result is True

    @patch('googleapiclient.discovery.build')
    def test_get_events(self, mock_build):
        """Testa obtenção de eventos."""
        # Configurar mocks
        mock_service = Mock()
        mock_build.return_value = mock_service
        mock_events = {'items': [{'id': '1', 'summary': 'Test Event'}]}
        mock_service.events().list().execute.return_value = mock_events
        
        # Criar instância e testar
        calendar = GoogleCalendarIntegration()
        calendar.service = mock_service
        
        start_date = datetime.now()
        end_date = start_date + timedelta(days=1)
        events = calendar.get_events(start_date, end_date)
        
        assert len(events) == 1
        assert events[0]['id'] == '1'
        assert events[0]['summary'] == 'Test Event'

    @patch('googleapiclient.discovery.build')
    def test_create_event(self, mock_build, mock_event):
        """Testa criação de evento."""
        # Configurar mocks
        mock_service = Mock()
        mock_build.return_value = mock_service
        mock_service.events().insert().execute.return_value = mock_event
        
        # Criar instância e testar
        calendar = GoogleCalendarIntegration()
        calendar.service = mock_service
        
        event_data = {
            'summary': 'Test Event',
            'start': datetime.now(),
            'end': datetime.now() + timedelta(hours=1),
            'timezone': 'UTC'
        }
        
        result = calendar.create_event(event_data)
        
        assert result == mock_event
        mock_service.events().insert().execute.assert_called_once()

    @patch('googleapiclient.discovery.build')
    def test_update_event(self, mock_build, mock_event):
        """Testa atualização de evento."""
        # Configurar mocks
        mock_service = Mock()
        mock_build.return_value = mock_service
        mock_service.events().update().execute.return_value = mock_event
        
        # Criar instância e testar
        calendar = GoogleCalendarIntegration()
        calendar.service = mock_service
        
        event_data = {
            'summary': 'Updated Event',
            'start': datetime.now(),
            'end': datetime.now() + timedelta(hours=1),
            'timezone': 'UTC'
        }
        
        result = calendar.update_event('event_id', event_data)
        
        assert result == mock_event
        mock_service.events().update().execute.assert_called_once()

    @patch('googleapiclient.discovery.build')
    def test_delete_event(self, mock_build):
        """Testa remoção de evento."""
        # Configurar mocks
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        # Criar instância e testar
        calendar = GoogleCalendarIntegration()
        calendar.service = mock_service
        
        result = calendar.delete_event('event_id')
        
        assert result is True
        mock_service.events().delete().execute.assert_called_once()

    def test_export_to_ical(self, mock_event, tmp_path):
        """Testa exportação para formato iCal."""
        # Criar instância e testar
        calendar = GoogleCalendarIntegration()
        
        events = [mock_event]
        output_path = tmp_path / 'test.ics'
        
        result = calendar.export_to_ical(events, str(output_path))
        
        assert result is True
        assert output_path.exists()
        
        # Verificar conteúdo do arquivo
        with open(output_path, 'rb') as f:
            content = f.read()
            assert b'BEGIN:VCALENDAR' in content
            assert b'BEGIN:VEVENT' in content
            assert b'Test Event' in content
            assert b'Test Location' in content
            assert b'Test Description' in content 