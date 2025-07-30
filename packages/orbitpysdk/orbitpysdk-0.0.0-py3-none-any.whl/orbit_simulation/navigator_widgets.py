import sys
import os
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QWidget, QLabel, QSpacerItem, QSizePolicy, QVBoxLayout
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtSvg import QGraphicsSvgItem
from styles import resources
from styles.styles import Styles

class VelocityWidget(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.velocity_item = QGraphicsSvgItem(":/images/icons/velocity.svg")
        self.scene.addItem(self.velocity_item)
        self.niddle_item = QGraphicsSvgItem(":/images/icons/niddle.svg")

        center_corrdinates = self.velocity_item.boundingRect().center()
        niddle_height = self.niddle_item.boundingRect().height()
        niddle_width = self.niddle_item.boundingRect().width()

        niddle_x = center_corrdinates.x() - niddle_width/2
        niddle_y = center_corrdinates.y() - niddle_height + 8
        rotation_point = QPointF(niddle_width / 2, niddle_height - 8 )
        self.niddle_item.setPos(niddle_x, niddle_y)
        self.niddle_item.setTransformOriginPoint(rotation_point)
        self.niddle_item.setRotation(-150)
        self.scene.addItem(self.niddle_item)

        self.setStyleSheet("border: none;")
        self.setMaximumHeight(int(self.velocity_item.boundingRect().height()))
        self.setMinimumWidth(int(self.velocity_item.boundingRect().width()))
    
    def update_velocity(self, velocity:float):
        velocity = abs(velocity)
        if velocity > 0.5:
            velocity = 0.5
        rotation_angle = (velocity * 300 / 0.5) - 150
        self.niddle_item.setRotation(rotation_angle)

class CompassWidget(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.compass_item = QGraphicsSvgItem(":/images/icons/compass.svg")
        self.scene.addItem(self.compass_item)
        self.niddle_item = QGraphicsSvgItem(":/images/icons/comp_rob.svg")

        center_corrdinates = self.compass_item.boundingRect().center()
        niddle_height = self.niddle_item.boundingRect().height()
        niddle_width = self.niddle_item.boundingRect().width()

        niddle_x = center_corrdinates.x() - niddle_width/2
        niddle_y = center_corrdinates.y() - niddle_height + 22
        rotation_point = QPointF(niddle_width / 2, niddle_height - 22 )
        self.niddle_item.setPos(niddle_x, niddle_y)
        self.niddle_item.setTransformOriginPoint(rotation_point)
        self.scene.addItem(self.niddle_item)

        self.setStyleSheet("border: none;")
        self.setMaximumHeight(int(self.compass_item.boundingRect().height()))
        self.setMinimumWidth(int(self.compass_item.boundingRect().width()))
    
    def update_rotation(self, rotation_angle:int):
        self.niddle_item.setRotation(rotation_angle % 360)

class NavigatorWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.styles = Styles()
        self.vlayout = QVBoxLayout()
        self.vlayout.setAlignment(Qt.AlignTop|Qt.AlignCenter)

        self.velocity_label = QLabel()
        self.velocity_label.setAlignment(Qt.AlignCenter|Qt.AlignBottom)
        self.velocity_label.setText("VELOCITY")
        self.velocity_label.setMaximumHeight(48)
        self.compass_label = QLabel()
        self.compass_label.setAlignment(Qt.AlignCenter|Qt.AlignBottom)
        self.compass_label.setText("ROTATION")
        self.compass_label.setMaximumHeight(48)
        self.velocity_view = VelocityWidget()
        self.compass_view = CompassWidget()

        self.vlayout.addWidget(self.compass_label)
        self.vlayout.addWidget(self.compass_view)
        self.vlayout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.vlayout.addWidget(self.velocity_label)
        self.vlayout.addWidget(self.velocity_view)
        self.setLayout(self.vlayout)

        self.setStyleSheet(self.styles.navigator_label())
    
    def update_velocity(self, velocity:float):
        self.velocity_view.update_velocity(velocity)
    
    def update_rotation(self, rotation_angle:int):
        self.compass_view.update_rotation(rotation_angle)
if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = NavigatorWidget()
    window.show()
    sys.exit(app.exec_())