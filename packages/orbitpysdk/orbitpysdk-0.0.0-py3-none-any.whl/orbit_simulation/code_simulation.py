import os
import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QLabel, QFrame, QWidget, QScrollArea
from PyQt5.QtCore import Qt

from styles.styles import Styles

# COMMANDS = [{
#     "command" : 1,
#     "move" : 5,
#     "turn" : 0,
#     "sound_data" : ""
    
# },
# {
#     "command" : 3,
#     "move" : 0,
#     "turn" : 1,
#     "sound_data" : ""
# }]

CODE_MAPPING = {
    1: ["forward", "move"],
    2: ["turn", "turn"],
    3: ["playsound", "sound_data"],
    4: ["temperature", ""],
    5: ["distance", ""]
}

class CodeSimulation(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("CodeSimulation")

        self.styles = Styles()

        self.setMinimumWidth(350)
    def code_panel(self, commands):
        self.main_layout = QVBoxLayout()

        self.title_label = QLabel("Code Simulation")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.code_widget = QWidget()
        self.code_layout = QVBoxLayout()
        self.code_scroll_area = QScrollArea()
        for command in commands:
            command_type = command["command"]
            if command_type in CODE_MAPPING:
                code_text = CODE_MAPPING[command_type][0]
                if code_text == "turn":
                    if command["turn"] == 1:
                        code_text = "turn_right"
                    elif command["turn"] == 2:
                        code_text = "turn_left"
                    code_arg = ""
                elif code_text == "playsound":
                    code_arg = "..."
                elif code_text == "forward":
                    code_arg = command[CODE_MAPPING[command_type][1]]
                else:
                    code_arg = ""
                label = QLabel()
                label.setText(
                    f'<span style="color:#c2caf7;">orbit.</span>'
                    f'<span style="color:#80a3fa;">{code_text}(</span>'
                    f'<span style="color:#ea6b40;">{code_arg}</span>'
                    f'<span style="color:#80a3fa;">)</span>'
                )
            self.code_layout.addWidget(label)
        self.code_layout.setAlignment(Qt.AlignTop)
        self.code_widget.setLayout(self.code_layout)
        self.code_scroll_area.setWidget(self.code_widget)
        self.main_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.code_scroll_area)
        self.main_layout.setAlignment(Qt.AlignBottom)
        self.setLayout(self.main_layout)

        self.code_scroll_area.setWidgetResizable(True)
        self.setStyleSheet(self.styles.code_panel())
        self.code_widget.setStyleSheet("background-color: transparent;")
        self.code_scroll_area.setStyleSheet(self.styles.scroll_area())
    
    def highlight_code(self, command_index):
        for i in range(self.code_layout.count()):
            label = self.code_layout.itemAt(i).widget()
            if i == command_index:
                label.setStyleSheet("background-color: #363a54; font-weight: normal;")
                scroll_bar = self.code_scroll_area.verticalScrollBar()
                scroll_value = int(i * scroll_bar.maximum() / self.code_layout.count())
                scroll_bar.setValue(scroll_value)
            else:
                label.setStyleSheet("background-color: transparent; font-weight: normal;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CodeSimulation()
    window.show()
    sys.exit(app.exec_())