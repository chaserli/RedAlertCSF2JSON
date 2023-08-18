import PySimpleGUI as sg
from json2csf import json2csf
from csf2json import csf2json

def run_func(func, infile: str, outfile: str, ext: str):
    if not infile.lower().endswith(ext):
        sg.popup('Error', f'Input file must be a {ext} file')
        return False
    else:
        try:
            func(infile, outfile)
            return True
        except Exception as e:
            sg.popup('Error', str(e))
            return False

if __name__ == "__main__":
    layout = [
        [sg.Input(key='-IN-', enable_events=True), sg.FileBrowse()],
        [sg.Input(key='-OUT-', enable_events=True), sg.SaveAs()],
        [sg.Radio('CSF to JSON', 'RADIO1', default=True, key='-R1-', enable_events=True),
        sg.Radio('JSON to CSF', 'RADIO1', key='-R2-', enable_events=True)],
        [sg.Button('Run'), sg.Button('Exit')],
        [sg.Text(size=(40,1), key='-OUTPUT-')]
    ]

    window = sg.Window('File Converter', layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Exit':
            break
        elif event in ('-IN-', '-OUT-', '-R1-', '-R2-'):
            window['-OUTPUT-'].update('')
            if event in ('-R1-', '-R2-'):
                window['-IN-'].update('')
                window['-OUT-'].update('')
        elif event == 'Run':
            infile = values['-IN-']
            outfile = values['-OUT-']
            if values['-R1-']:
                success = run_func(csf2json, infile, outfile, '.csf')
                if success:
                    window['-OUTPUT-'].update('CSF to JSON Conversion completed')
            else:
                success = run_func(json2csf, infile, outfile, '.json')
                if success:
                    window['-OUTPUT-'].update('JSON to CSF Conversion completed')

    window.close()
