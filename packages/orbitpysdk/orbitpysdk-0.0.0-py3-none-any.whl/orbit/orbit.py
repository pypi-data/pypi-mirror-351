
import os
import sys
import base64
from pydub import AudioSegment


TEMP = os.path.join(os.getcwd())

class Orbit:
    def __init__(self):
        self.command = []
        self.command_template = {
            "command" : 0,
            "move" : 0,
            "turn" : 0,
            "sound_data" : ""
            
        }
        
    
    def forward(self,steps):
        copy_command = self.command_template.copy()
        copy_command["command"] = 1
        copy_command["move"] = steps
        
        self.command.append(copy_command)
    
    def turn_right(self):
        copy_command = self.command_template.copy()
        copy_command["command"] = 2
        copy_command["turn"] = 1
        
        self.command.append(copy_command)

    def turn_left(self):
        copy_command = self.command_template.copy()
        copy_command["command"] = 2
        copy_command["turn"] = 2
        
        self.command.append(copy_command)

    
    def playsound(self,path_to_audio):
        copy_command = self.command_template.copy()
        copy_command["command"] = 3
        if not path_to_audio.endswith("mp3"):
            new_path = os.path.join(TEMP, "temp.mp3")
            sound = AudioSegment.from_file(path_to_audio)
            sound.export(new_path,format="mp3",bitrate="128k")
            with open(new_path, 'rb') as binary_file:
                binary_file_data =binary_file.read()
                base64_encoded_data = base64.b64encode(binary_file_data)
                base64_output = base64_encoded_data.decode('utf-8')
                
            copy_command["sound_data"] = base64_output

            os.remove(new_path)
            
        elif path_to_audio.endswith("mp3"):
            with open(path_to_audio, 'rb') as binary_file:
                binary_file_data =binary_file.read()
                base64_encoded_data = base64.b64encode(binary_file_data)
                base64_output = base64_encoded_data.decode('utf-8')
                
            copy_command["sound_data"] = base64_output
            
        self.command.append(copy_command)
    
    def temperature(self):
        copy_command = self.command_template.copy()
        copy_command["command"] = 4
        self.command.append(copy_command)
    
    def distance(self):
        copy_command = self.command_template.copy()
        copy_command["command"] = 5
        self.command.append(copy_command)
    
    def start_simulation(self):
        from PyQt5.QtWidgets import QApplication
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from orbit_simulation.main_window import MainWindow
        app = QApplication(sys.argv)
        window = MainWindow(self.command)
        window.show()
        sys.exit(app.exec_())
