""" Вспомогательные функции для интерфейса """
from datetime import datetime, timedelta

import PySimpleGUI as sg

from info import date_format


def get_period(values: dict[str, str]) -> list[datetime]:
    """Проверить даты и вернуть интервал из начала и конца"""
    start_date = datetime.strptime(values["-DATE_START-"], date_format)
    end_date = datetime.strptime(values["-DATE_END-"], date_format)
    if end_date < start_date:
        sg.PopupError(
            "Дата конца промежутка введена неверно. Пожалуйста, укажите дату начала раньше, чем дата конца"
        )
    period_range = []
    while start_date <= end_date:
        period_range.append(start_date)
        start_date += timedelta(days=1)
    return period_range
