from PyQt5.QtWidgets import QFrame, QLabel, QHBoxLayout, QApplication, QGraphicsBlurEffect
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap
import sys
import os
import random

from styles import resources
from styles.styles import Styles

class SensorWidget(QFrame):
    def __init__(self, parent=None, icon="temp.png", unit="°C"):
        super().__init__(parent)
        self.setWindowTitle("Two Label Dialog")
        self.setObjectName("sensor_widget")

        self.styles = Styles()

        self.setWindowFlags(Qt.FramelessWindowHint)
        if parent is not None:
            self.setGeometry(self.parent().width() / 2 - 160, self.parent().height() /2 - 160, 320, 320)
        else:
            self.setFixedSize(320, 320)

        label1 = QLabel()
        label1.setPixmap(QPixmap(f":/images/icons/{icon}"))
        label2 = QLabel(f"{random.randint(22, 35)} {unit}")
        label2.setAlignment(Qt.AlignCenter|Qt.AlignCenter)

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)
        layout.addWidget(label1)
        layout.addWidget(label2)

        self.setLayout(layout)

        self.setStyleSheet(self.styles.sensor())
        blur_effect = QGraphicsBlurEffect()
        blur_effect.setBlurRadius(10)
        self.show()
        self.parent().workspace_view.setGraphicsEffect(blur_effect)

        QTimer().singleShot(3000, self.close)
    
    def closeEvent(self, a0):
        self.parent().workspace_view.setGraphicsEffect(None)
        return super().closeEvent(a0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = SensorWidget()
    # dialog.show()
    # QTimer.singleShot(2000, dialog.close)  # Close after 2 seconds
    sys.exit(app.exec_())