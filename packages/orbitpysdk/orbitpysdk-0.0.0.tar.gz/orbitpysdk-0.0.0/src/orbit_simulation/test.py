from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QScrollArea, QLabel, QPushButton, QScrollBar
import sys

class AutoScrollDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto-Scroll Example")

        self.layout = QVBoxLayout(self)

        # Create the scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        # Content widget inside scroll area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.scroll_area.setWidget(self.content_widget)

        self.layout.addWidget(self.scroll_area)

        # Button to add content
        self.add_button = QPushButton("Add Label")
        self.add_button.clicked.connect(self.add_label)
        self.layout.addWidget(self.add_button)

        self.label_count = 0

    def add_label(self):
        self.label_count += 1
        label = QLabel(f"Label #{self.label_count}")
        self.content_layout.addWidget(label)

        # Force scroll to bottom
        scroll_bar = self.scroll_area.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AutoScrollDemo()
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec_())
