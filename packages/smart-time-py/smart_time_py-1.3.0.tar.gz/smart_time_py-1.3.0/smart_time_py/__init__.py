"""
Smart Time Py - Uma biblioteca avançada para manipulação de datas e tempos em Python.
"""

from smart_time_py.analysis import (TimeGroup, analyze_seasonality,
                                    calculate_temporal_stats,
                                    detect_temporal_patterns, group_dates)
from smart_time_py.calendar_integration import (CalendarIntegration,
                                                GoogleCalendarIntegration)
from smart_time_py.converter import (add_time, calculate_difference,
                                     convert_with_timezone, datetime_to_string,
                                     string_to_datetime, subtract_time,
                                     validate_date_string)
from smart_time_py.formatters import (format_iso, format_natural,
                                      format_relative)
from smart_time_py.holidays import (add_holiday, get_holidays,
                                    get_working_days, is_holiday,
                                    remove_holiday)
from smart_time_py.periods import DateRange, TimePeriod
from smart_time_py.timezone import (convert_timezone, get_available_timezones,
                                    get_timezone_info, is_dst_active)

__version__ = "1.2.0"
__author__ = "Roberto Lima"
__email__ = "robertolima.izphera@gmail.com"
