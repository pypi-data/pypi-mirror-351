from . import resources

class Styles:
    def __init__(self):
        self.main_color = "white"
        self.logo_color = "#87f3ff"
        self.simulation_color = "#ff9900"
    
    def workspace_background(self):
        return f"""
            QGraphicsView {{
                background-color: transparent;
                border-radius: 2px;
            }}
        """
    def main_window(self):
        return f"""
            QFrame#MainWindow {{
                border-image: url(:/images/icons/main_background.jpg) 0 0 0 0 stretch stretch;
            }}
        """
    
    def orbit_label(self):
        return f"""
            QLabel {{
                color: {self.logo_color};
                font: 81 48pt "Aeronixsa";
            }}
        """
    
    def simulation_label(self):
        return f"""
            QLabel {{
                color: {self.simulation_color};
                font: 81 26pt "Pacifico";
            }}
        """
    
    def central_frame(self):
        return f"""
            QFrame#central_frame {{
                background-color: rgba(26, 27, 38, 0.18);
                border-radius: 2px;
                padding: 10px;
            }}
        """
    
    def navigator_label(self):
        return f"""
            QWidget {{
                background-color: transparent;
            }}
            QLabel {{
                color: {self.logo_color};
                font: 81 14pt "Aeronixsa";
            }}
        """
    
    def restart_style(self):
        return f"""
            QPushButton {{
                background-color: {self.simulation_color};
                color: #ffffff;
                border: 0px;
                border-radius: 8px;
                font: 81 18pt "Sary Soft";
            }}
        """
    
    def code_panel(self):
        return f"""
            QLabel {{
                color: {self.simulation_color};
                font: 81 14pt "Courier New";
            }}
        """
    
    def scroll_area(self):
        return f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 10px;
                margin: 5px 0;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: #a0a0a0;
                min-height: 30px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #808080;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: none;  /* Or set to 'transparent' */
            }}
        """
    
    def sensor(self):
        return f"""
            QFrame#sensor_widget {{
                background-color: rgba(22, 22, 30, 0.6);
            }}
            QLabel {{
                color: white;
                font: 81 24pt "Courier New";
            }}
        """