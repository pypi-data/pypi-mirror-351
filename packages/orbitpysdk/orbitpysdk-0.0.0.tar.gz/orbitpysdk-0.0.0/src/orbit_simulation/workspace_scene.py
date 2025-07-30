import sys
import os
import math
  # Copies text to the clipboard


from PyQt5.QtWidgets import (
    QApplication, QGraphicsScene, QGraphicsView,
    QGraphicsPixmapItem,
    QVBoxLayout, QWidget, QMessageBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

from styles import resources
from styles.styles import Styles
class WorkSpaceView(QGraphicsView):
    command_executed = pyqtSignal(bool)
    twist_changed = pyqtSignal(list)
    def __init__(self, commands):
        super().__init__()

        self.styles = Styles()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.setFixedSize(760, 580)
        self.setStyleSheet(self.styles.workspace_background())

        # Load and add QPixmap
        background_pixmap = QPixmap(":/images/icons/background.jpg").scaled(750, 600, Qt.KeepAspectRatio)
        self.background_item = QGraphicsPixmapItem(background_pixmap)
        self.scene.addItem(self.background_item)

        # Load and add SVG
        robot_pixmap = QPixmap(":/images/icons/orbit.png").scaled(90, 90, Qt.KeepAspectRatio)
        self.robot_item = QGraphicsPixmapItem(robot_pixmap)  # <-- replace with your SVG file path
        self.robot_item.setTransformOriginPoint(self.robot_item.boundingRect().center())
        self.scene.addItem(self.robot_item)

        # Initial rotation angle
        # self.rotation_angle = 0

        self.step_x = int(self.background_item.boundingRect().width() / 5)
        self.step_y = int(self.background_item.boundingRect().height() / 4)
        # self.x = int(self.step_x / 2 - self.robot_item.boundingRect().width() / 2)
        # self.y = int(self.background_item.boundingRect().height() - self.step_y / 2 - self.robot_item.boundingRect().height() / 2)

        self.initial_x = 0
        self.initial_y = 0
        self.target_distance = 0
        self.initial_angle = 0
        self.target_rotation = 0

        self.current_velocity = 0.0

        self.commands = commands

        self.move_timer = QTimer()
        self.move_timer.timeout.connect(self.move_robot)

        self.rotate_timer = QTimer()
        self.rotate_timer.timeout.connect(self.rotate_svg)

        self.set_initial_position()


        # self.robot_item.setPos(self.x, self.y)
        # self.start_commands() 

    def set_initial_position(self):
        self.move_timer.stop()
        self.rotate_timer.stop()
        self.x = int(self.step_x / 2 - self.robot_item.boundingRect().width() / 2)
        self.y = int(self.background_item.boundingRect().height() - self.step_y / 2 - self.robot_item.boundingRect().height() / 2)
        self.robot_item.setPos(self.x, self.y)
        self.rotation_angle = 0
        self.current_velocity = 0.0
        self.twist_changed.emit([self.current_velocity, self.rotation_angle])
        self.robot_item.setRotation(self.rotation_angle)

    def rotate_svg(self):
        self.rotation_angle += (self.target_rotation - self.initial_angle) / 45
        self.robot_item.setRotation(self.rotation_angle % 360)
        self.twist_changed.emit([self.current_velocity, self.rotation_angle])
        if abs(self.target_rotation - self.rotation_angle) < 1:
            self.rotate_timer.stop()
            self.command_executed.emit(True)
    
    def start_movement(self, target_distance):
        self.initial_x = self.x
        self.initial_y = self.y
        heading = math.radians(self.rotation_angle - 90)
        step_x = self.step_x * math.cos(heading)
        step_y = self.step_y * math.sin(heading)
        step_d = math.sqrt(step_x ** 2 + step_y ** 2)
        self.target_distance = target_distance * step_d
        self.move_timer.start(20)
    
    def start_rotation(self, target_rotation):
        self.target_rotation = self.rotation_angle + target_rotation
        self.initial_angle = self.rotation_angle
        self.rotate_timer.start(20)
    
    def move_robot(self):
        heading = math.radians(self.rotation_angle - 90)
        distance = math.sqrt((self.robot_item.x() - self.initial_x) ** 2 + (self.robot_item.y() - self.initial_y) ** 2)

        if self.outofbounds():
            self.move_timer.stop()
            QMessageBox.warning(self, "Warning", "Robot is out of bounds!")
            self.command_executed.emit(False)
            return
        if self.target_distance - distance < 1:
            self.current_velocity = 0.0
            self.move_timer.stop()
            self.command_executed.emit(True)
            self.twist_changed.emit([self.current_velocity, self.rotation_angle])
            return
        self.current_velocity = math.sin(distance * math.pi / (abs(self.target_distance))) * 0.35
        self.twist_changed.emit([self.current_velocity, self.rotation_angle])
        step_x = self.step_x * math.cos(heading)
        step_y = self.step_y * math.sin(heading)
        self.robot_item.setPos(self.x, self.y)
        self.x += step_x / 50
        self.y += step_y / 50
    
    def outofbounds(self):
        if self.robot_item.x() < 0 or self.robot_item.x() > self.background_item.boundingRect().width() - self.robot_item.boundingRect().width() / 2:
            return True
        if self.robot_item.y() < 0 or self.robot_item.y() > self.background_item.boundingRect().height() - self.robot_item.boundingRect().height() / 2:
            return True
        return False

class MainWindow(QWidget):
    def __init__(self, commands):
        super().__init__()
        self.commands = commands
        self.setWindowTitle("PyQt5 QPixmap & Rotatable SVG")
        self.view = WorkSpaceView(self.commands)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow({})
    window.resize(800, 800)
    window.show()
    sys.exit(app.exec_())
