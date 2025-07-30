import os
import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame, QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy,QWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor

from orbit_simulation.workspace_scene import WorkSpaceView
from orbit_simulation.face_widget import FaceWidget
from orbit_simulation.code_simulation import CodeSimulation
from orbit_simulation.navigator_widgets import NavigatorWidget
from orbit_simulation.temperature import SensorWidget
from styles.styles import Styles


class MainWindow(QFrame):
    def __init__(self, commands):
        super().__init__()
        self.commands = commands
        self.current_command = 0
        self.setObjectName("MainWindow")
        self.setWindowTitle("Orbit Simulation")
        self.setGeometry(100, 100, 1280, 600)

        self.styles = Styles()
        self.init_ui()

        self.setStyleSheet(self.styles.main_window())

        self.sensor_widget = None

        self.start_simulation()

    def init_ui(self):
        layout = QVBoxLayout()
        central_frame = QFrame()
        central_frame.setObjectName("central_frame")
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(20)
        hlayout = QHBoxLayout()
        logolayout = QHBoxLayout()
        logolayout.setAlignment(Qt.AlignCenter)
        logolayout.setContentsMargins(0, 0, 0, 0)
        logolayout.setSpacing(14)

        right_widget = QWidget()
        right_widget.setObjectName("RightWidget")
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setAlignment(Qt.AlignBottom)

        self.navigator_widget = NavigatorWidget()

        self.workspace_view = WorkSpaceView(self.commands)
        self.workspace_view.command_executed.connect(self.command_executed_callback)
        self.workspace_view.twist_changed.connect(self.change_twist)

        self.code_simulation = CodeSimulation()
        self.code_simulation.code_panel(self.commands)

        self.face_widget = FaceWidget(self.commands)
        self.face_widget.command_executed.connect(self.start_simulation)

        self.orbit_label = QLabel("ORBIT")
        self.orbit_label.setAlignment(Qt.AlignBottom|Qt.AlignLeading|Qt.AlignLeft)
        self.orbit_label.setStyleSheet(self.styles.orbit_label())
        self.simulation_label = QLabel("Simulation")
        self.simulation_label.setAlignment(Qt.AlignBottom|Qt.AlignLeading|Qt.AlignLeft)
        # self.simulation_label.setFixedHeight(70)
        self.simulation_label.setStyleSheet(self.styles.simulation_label())

        # self.close_btn = QPushButton("X", self)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(4)
        shadow.setYOffset(4)
        shadow.setColor(QColor("#151537"))

        self.restart = QPushButton("Restart", self)
        self.restart.setGraphicsEffect(shadow)
        self.restart.setFixedSize(160, 60)
        self.restart.setStyleSheet(self.styles.restart_style())
        self.restart.clicked.connect(self.restart_simulation)

        logolayout.addWidget(self.orbit_label, 0, Qt.AlignLeft|Qt.AlignCenter)
        logolayout.addWidget(self.simulation_label, 0, Qt.AlignLeft|Qt.AlignCenter)
        # logolayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        # logolayout.addWidget(self.close_btn, 0, Qt.AlignRight|Qt.AlignCenter)
        # layout.addWidget(self.orbit_label, 0, Qt.AlignCenter)
        # layout.addWidget(self.simulation_label, 0, Qt.AlignBottom|Qt.AlignCenter)

        right_layout.addWidget(self.code_simulation, 0, Qt.AlignTop|Qt.AlignLeft)
        right_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        right_layout.addWidget(self.face_widget, 0, Qt.AlignBottom|Qt.AlignLeft)
        right_widget.setLayout(right_layout)
        right_widget.setFixedHeight(self.workspace_view.height())
        layout.addLayout(logolayout)
        hlayout.addWidget(self.navigator_widget)
        hlayout.addWidget(self.workspace_view, 0, Qt.AlignTop)
        hlayout.addWidget(right_widget)
        central_frame.setLayout(hlayout)
        layout.addWidget(central_frame)
        layout.addWidget(self.restart, 0, Qt.AlignBottom|Qt.AlignCenter)

        central_frame.setStyleSheet(self.styles.central_frame())

        self.setLayout(layout)
    
    def command_executed_callback(self, command_feedback):
        if command_feedback:
            QTimer().singleShot(500, self.start_simulation)
            # self.start_simulation()
        else:
            self.workspace_view.set_initial_position()
            self.current_command = 0
            print("Command execution failed or restart button pressed.")
    
    def change_twist(self, twist:list):
        self.navigator_widget.update_velocity(twist[0])
        self.navigator_widget.update_rotation(twist[1])
    
    def restart_simulation(self):
        if self.sensor_widget is None:
            self.workspace_view.set_initial_position()
            self.current_command = 0
            self.start_simulation()

    def start_simulation(self):
        if self.sensor_widget is not None:
            self.sensor_widget.close
            self.sensor_widget = None
        if self.current_command >= len(self.commands):
            print("All commands executed.")
            self.code_simulation.highlight_code(-1)
            return
        
        command = self.commands[self.current_command]

        self.code_simulation.highlight_code(self.current_command)

        if command["command"] == 1:
            self.workspace_view.start_movement(command["move"])
        elif command["command"] == 2:
            if command["turn"] == 1:
                self.workspace_view.start_rotation(90)
            elif command["turn"] == 2:
                self.workspace_view.start_rotation(-90)
        elif command["command"] == 3:
            self.face_widget.start_talking(command["sound_data"])
        
        elif command["command"] == 4:
            self.sensor_widget = SensorWidget(self, "temp.png", "°C")
            QTimer().singleShot(3500, self.start_simulation)
        
        elif command["command"] == 5:
            self.sensor_widget = SensorWidget(self, "distance.png", "cm")
            QTimer().singleShot(3500, self.start_simulation)
        self.current_command += 1
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow({})
    window.show()
    sys.exit(app.exec_())