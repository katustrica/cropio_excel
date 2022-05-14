from datetime import timedelta, datetime
import PySimpleGUI as sg

from main import create_excels
from info import date_format

sg.theme("Tan")
task_id_table = [
    [
        sg.Listbox(
            values=[],
            select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE,
            size=(40, 15),
            key="-LISTBOX-",
            enable_events=True,
        )
    ],
]

layout_list = [
    [
        sg.Frame(
            "Cписок заданий", task_id_table, font="Helvetica 12", title_color="blue"
        )
    ],
    [sg.InputText("", size=(44, 1), key="-TASK_ID-")],
    [sg.Button("Добавить", size=(39, 1), key="-ADD-")],
    [sg.Button("Удалить", size=(39, 1), key="-DELETE-")],
    [sg.Button("Сделать таблицу", size=(39, 1), key="-START_LIST-")],
]

layout_period = [
    [sg.Text("Выберите начало промежутка")],
    [sg.Input(key='-DATE_START-', size=(20, 1), readonly=True), sg.CalendarButton('Дата', close_when_date_chosen=False, key='-CALENDAR_START-', format=date_format)],
    [sg.Text("Выберите конец промежутка")],
    [sg.Input(key='-DATE_END-', size=(20, 1), readonly=True), sg.CalendarButton('Дата', close_when_date_chosen=False, key='-CALENDAR_END-', format=date_format)],
    [sg.Button("Сделать таблицу", size=(39, 1), key="-START_PERIOD-",  expand_x=True)],
            ]

layuot_date = [
    [sg.Text("Выберите день")],
    [sg.Input(key='-DATE_ONLY_DAY-', size=(20, 1), readonly=True), sg.CalendarButton('Дата', close_when_date_chosen=False, key='-CALENDAR_ONLY_DAY-', format=date_format)],
    [sg.Button("Сделать таблицу", size=(39, 1), key="-START_DAY-",  expand_x=True)],
]

layuot = [
    [sg.TabGroup([
        [sg.Tab('Список заданий', layout_list), sg.Tab('Период', layout_period), sg.Tab("День", layuot_date)]
        ])
    ]
]

window = sg.Window("Задания", layuot)

task_ids: list[int] = []

while True:  # Event Loop
    event, values = window.read()
    if event in (None, "Exit"):
        break

    if event == "-DELETE-":
        try:
            for task_id in values["-LISTBOX-"]:
                task_ids.remove(task_id)
            window["-LISTBOX-"].update(task_ids)
            window["-TASK_ID-"].update("")
        except Exception:
            sg.PopupError("Ошибка")

    elif event == "-ADD-":
        try:
            task_ids.append(int(values["-TASK_ID-"]))
            window["-LISTBOX-"].update(task_ids)
            window["-TASK_ID-"].update("")
        except Exception:
            sg.PopupError("Неправильный номер задания")
    # Поскольку может быть одновременно минимум два непустых поля,
    # были отдельно добавлены кнопки "Создать таблицу"
    elif event == "-START_LIST-":
        create_excels(task_ids=task_ids)
        sg.PopupOK("Готово")

    elif event == "-START_PERIOD-":
        start_date = datetime.strptime(values["-CALENDAR_START-"], date_format)
        end_date = datetime.strptime(values["-CALENDAR_END-"], date_format)
        if end_date > start_date:
            sg.PopupError("Дата конца промежутка введена неверно. Пожалуйста, укажите дату начала раньше, чем дата конца")
        period_range = []
        while start_date <= end_date:
            period_range.append(start_date)
            start_date += timedelta(days=1)

        create_excels(period=period_range)
        sg.PopupOK("Готово")

    elif event == "-START_DAY-":
        create_excels(period=[datetime.strptime(values["-DATE_ONLY_DAY-"], date_format)])
        sg.PopupOK("Готово")

    elif event == "-CALENDAR_START-":
        window["-DATE_START-"].update(values["-CALENDAR_START-"])

    elif event == "-CALENDAR_END-":
        window["-DATE_END-"].update(values["-CALENDAR_END-"])
    
    elif event == "-CALENDAR_ONLY_DAY-":
        window["-DATE_ONLY_DAY-"].update(values["-CALENDAR_ONLY_DAY-"])
window.close()
