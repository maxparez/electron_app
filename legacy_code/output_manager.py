import sys
import PySimpleGUI as sg

class OutputManager:
    @property
    def window(self):
        return self._window
    
    def __init__(self):
        self.gui_enabled = False
        self._window = None

    def start(self, window=None):
        self.gui_enabled = True
        if window is None:
            self.create_gui_window()
        else:
            self._window = window    

    def create_gui_window(self):
        layout = [
            [sg.Multiline(size=(60, 10), key='-OUTPUT-', autoscroll=True)],
            [sg.Button('Clear')]
        ]
        self._window = sg.Window('Output Window', layout,finalize=True)

    def do_event(self,win, event):
        if win==self._window:
            if event == "Clear":
                self._window['-OUTPUT-'].update('')



    def print(self, text, color = 'black'):
        if self.gui_enabled:
            if self._window:
                self._window['-OUTPUT-'].update(value=text+"\n", text_color_for_value=color, append=True)
        else:
            print(text)

    def clear_gui_output(self):
        if self.window:
            self.window['-OUTPUT-'].update('')

    def run_gui_loop(self):
        while True:
            event, values = self.window.read()
            if event == sg.WINDOW_CLOSED or event == 'Exit':
                break
            elif event == 'Clear':
                self.clear_gui_output()

        self.window.close()
