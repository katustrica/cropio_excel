import PySimpleGUI as sg

from main import create_excels

sg.theme('Tan')
task_id_table = [
    [sg.Listbox(values=[], select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, size=(40, 15), key='-LISTBOX-')],
]
layout = [
            [sg.Frame('Cписок заданий', task_id_table, font='Helvetica 12', title_color='blue')],
            [sg.InputText('', size=(44, 1), key='-TASK_ID-')],
            [sg.Button('Добавить', size=(39, 1), key='-ADD-')],
            [sg.Button('Сделать таблицу', size=(39, 1), key='-START-')],
]

window = sg.Window('Задания', layout)

task_ids: list[int] = []

while True:             # Event Loop
    event, values = window.read()

    if event in (None, 'Exit'):
        break

    if event == '-ADD-':
        try:
            task_ids.append(int(values['-TASK_ID-']))
            window['-LISTBOX-'].update(task_ids)
            window['-TASK_ID-'].update('')
        except Exception:
            sg.PopupError('неправильный номер задания')
    if event == '-START-':
        create_excels(task_ids)
        sg.PopupOK('Готово')

window.close()