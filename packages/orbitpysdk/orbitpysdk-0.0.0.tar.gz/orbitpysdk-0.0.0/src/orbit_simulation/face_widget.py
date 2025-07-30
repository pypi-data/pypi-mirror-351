import os
import sys
import cv2
import time
from importlib.resources import files
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QFrame, QStackedWidget
from PyQt5.QtCore import QThread, pyqtSignal, QUrl, QTimer, Qt, QPropertyAnimation, QPoint
from PyQt5.QtGui import QImage, QPixmap

from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence

from orbit_utils.sound_player import SoundPlayer

RESOURCE = os.path.join(os.path.join(sys.prefix, 'share', 'orbitpysdk'), 'resource')
print(RESOURCE)
VIDEOS = os.path.join(RESOURCE, 'videos')
ADS = os.path.join(VIDEOS, 'ads')
FACES = os.path.join(RESOURCE, 'images', 'faces')
LIPS = os.path.join(RESOURCE, 'images', 'lips')
AUDIO_FOLDER = os.path.join(RESOURCE,'audios')

FACE_IDS = {
    0: "blinking.mp4",
    1: "breathe.mp4",
    2: "compassion.mp4",
    3: "curious.mp4",
    4: "error.mp4",
    5: "heart_eyes.mp4",
    6: "hello.mp4",
    7: "loading.mp4",
    8: "playful.mp4",
    9: "shy.mp4",
    10: "star_eyes.mp4",
    11: "surprised.mp4",
    12: "thank_you.mp4",

    13: "merhaba"
}

class AdsView(QWidget):
    def __init__(self, face_thread:QThread):
        super().__init__()
        self.setObjectName("ad_view")
        # self.setStyleSheet("QWidget#ad_view{background-color: black;}")
        self.face_thread = face_thread
        self.window_width = 220
        self.window_height = 320
        self.scale = 3.5
        self.icon_width = int(640 / self.scale)
        self.icon_height = int(905 / self.scale)
        self.x_pos = int(self.window_width - self.icon_width - 12)
        self.y_pos = int(self.window_height - self.icon_height - 12)
        self.center_widget = QWidget(self)
        self.center_widget.setMinimumHeight(self.window_height)
        self.center_widget.setMinimumWidth(self.window_width)

        self.robot_icon = QLabel(self.center_widget)
        self.robot_icon.setGeometry(self.x_pos, self.y_pos, self.icon_width, self.icon_height)
        self.robot_icon.setPixmap(self.scale_pixel("orbit_v5.png", self.icon_width, self.icon_height))
        self.center_widget.setObjectName("center_object")
        # self.center_widget.setStyleSheet("QWidget#center_object{background-color: black;}")
        self.robot_icon.setStyleSheet("background-color: rgba(0, 255, 255, 0);")
        self.robot_icon.hide()
        
        # self.robot_icon.setStyleSheet("background-color: blue;")

        self.face_frame = QFrame(self.center_widget)
        self.main_face = MainFace(self.face_frame, self.face_thread)
        self.main_face.setParent(self.center_widget)

        self.web_label = QLabel(self.center_widget)
        self.web_label.move(20,20)
        # self.web_label.setMinimumHeight(50)
        self.web_label.setMinimumWidth(300)
        self.web_label.setStyleSheet("color: white;")

        layout = QVBoxLayout()
        layout.addWidget(self.center_widget)
        # layout.addWidget(self.web_label)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        end_pos_x = int(self.x_pos + (self.icon_width - 98) /2)
        end_pos_y = int(self.y_pos + (self.icon_height / 6.5))
        self.main_face.resize_face(98, 48)
        self.main_face.setGeometry(end_pos_x, end_pos_y, 98, 48)
        self.robot_icon.show()
    
    def scale_pixel(self, file_name, w, h):
        pixel = QPixmap(os.path.join(FACES, file_name))
        return pixel.scaled(w, h, Qt.KeepAspectRatio)

class MainFace(QWidget):
    command_executed = pyqtSignal(bool)
    def __init__(self, face_frame:QFrame, face_thread:QThread):
        super().__init__()

        self.max_width = int(1280/1)
        self.max_height = int(720/1)
        self.face_scale = 1.0
        self.face_publisher = PlayFaceThread()
        self.feelings_indx = 0
        self.motions_id = 0

        #create ui
        self.face_frame = face_frame
        self.face_frame.setMinimumSize(self.max_width, self.max_height)
        self.face_frame.setMaximumSize(self.max_width, self.max_height)
        self.video_label = QLabel(self.face_frame)
        self.lip_label = QLabel(self.face_frame)
        # self.setGeometry(0,0,1280, 720)
        # self.setStyleSheet('background-color: transparent;')

        layout = QVBoxLayout()
        layout.addWidget(self.face_frame)
        layout.setContentsMargins(0, 0, 0,0)
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.cap = cv2.VideoCapture(os.path.join(VIDEOS, "blinking.mp4"))

        self.lip_images = {
            "1": cv2.imread(os.path.join(LIPS, "1_face_.png"), cv2.IMREAD_UNCHANGED),  # Kapalı ağız
            "1_2": cv2.imread(os.path.join(LIPS, "1_face.png"), cv2.IMREAD_UNCHANGED),
            "2": cv2.imread(os.path.join(LIPS, "2_face.png"), cv2.IMREAD_UNCHANGED),
            "4": cv2.imread(os.path.join(LIPS, "3_face.png"), cv2.IMREAD_UNCHANGED),  # Yarı açık ağız
            "3": cv2.imread(os.path.join(LIPS, "4_face.png"), cv2.IMREAD_UNCHANGED),
            "5": cv2.imread(os.path.join(LIPS, "5_face.png"), cv2.IMREAD_UNCHANGED)  # Tam açık ağız
        }

        # self.play_face_thread = face_thread
        # self.play_face_thread.face_id.connect(self.change_face_callbackk)
        # self.play_face_thread.decibel_msg.connect(self.update_lip)

        self.previous_time = 0.0
    
    def start_talking(self, base64_audio):
        self.sound_player = SoundPlayer(base64_audio)
        self.sound_player.decibel.connect(self.update_lip)
        self.sound_player.finished.connect(self.command_executed.emit)
        self.sound_player.start()
    
    def resize_face(self, w, h):
        self.face_frame.setMinimumSize(w, h)
        self.face_frame.setMaximumSize(w, h)
        self.max_width = w
        self.max_height = h
        self.update_frame()
        self.update_lip(0)
    
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            new_width = int(self.max_width * self.face_scale)
            new_height = int(self.max_height * self.face_scale)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (new_width, new_height), interpolation = cv2.INTER_LINEAR)
            # x1 = int((new_width - self.max_width) * 1.8)
            x1 = (int(new_width / 8))
            x2 = new_width - x1
            crop = frame[0:new_height, x1:x2]
            h, w, ch = crop.shape
            bytes_per_line = ch * w
            q_image = QImage(crop.tobytes(), w, h, bytes_per_line, QImage.Format_RGB888)
            self.video_label.setGeometry(int(x1), 0, w, h)
            self.video_label.setPixmap(QPixmap.fromImage(q_image))
        
        else:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

            self.cap = cv2.VideoCapture(os.path.join(VIDEOS, "blinking.mp4"))
            self.lip_label.show()

            if self.motions_id == 1:
                print("merhaba")
                self.face_publisher.mp3_player("merhaba")
            self.motions_id = 0

    def update_lip(self, decibel):
        if decibel <= 15:
            lip_time = time.time() - self.previous_time
            if lip_time < 0.25:
                image = self.lip_images["2"]
            else:
                image = self.lip_images["1"]
        elif decibel <= 60:
            image = self.lip_images["2"]
        elif decibel <= 80:
            image = self.lip_images["3"]
        elif decibel <= 100:
            image = self.lip_images["4"]
        elif decibel <= 120:
            image = self.lip_images["5"]
        else:
            image = self.lip_images["1_2"]
        # self.previous_time = time.time()80

        # frame = cv2.imread(os.path.join(LIPS, image), cv2.IMREAD_UNCHANGED)
        frame = image
        new_width = int(self.max_width * self.face_scale)
        new_height = int(self.max_height * self.face_scale)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (new_width, new_height), interpolation = cv2.INTER_LINEAR)
        # x1 = int((new_width - self.max_width) * 1.8)
        x1 = (int(new_width / 8))
        x2 = new_width - x1
        crop = frame[int(new_height/1.5):new_height, x1:x2]
        h, w, ch = crop.shape
        bytes_per_line = ch * w
        q_image = QImage(crop.tobytes(), w, h, bytes_per_line, QImage.Format_RGB888)
        self.lip_label.setGeometry(int(x1), int(new_height/1.3), w, h)
        self.lip_label.setPixmap(QPixmap.fromImage(q_image))
    
    def change_face_callbackk(self, face_id):
        print("face_id")
        self.cap = cv2.VideoCapture(os.path.join(VIDEOS, FACE_IDS[face_id]))
        self.feelings_indx= face_id
        self.lip_label.hide()

class FaceWidget(QWidget):
    command_executed = pyqtSignal(bool)
    def __init__(self, commands):
        super().__init__()

        self.commands = commands
        self.face_thread = PlayFaceThread()

        self.setObjectName("main_window")
        # self.setStyleSheet(""" QWidget#main_window{background-color: black;}""")

        self.stacked_widget = QStackedWidget(self)

        self.face_center = QFrame()

        # self.main_face = MainFace(self.face_center, self.face_thread)
        self.ads_view = AdsView(self.face_thread)

        self.ads_view.main_face.command_executed.connect(self.command_executed.emit)

        # self.stacked_widget.addWidget(self.main_face)
        # self.stacked_widget.addWidget(self.ads_view)

        layout = QVBoxLayout()
        layout.addWidget(self.ads_view)
        layout.setContentsMargins(0, 0, 0,0)
        self.setLayout(layout)

        # self.timer = QTimer()
        # self.timer.singleShot(5000, self.change_page)
        # self.stacked_widget.setCurrentWidget(self.ads_view)

        
        self.face_thread.start()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.shortcut = QShortcut(QKeySequence('Q'), self)
        self.shortcut.activated.connect(self.close)
    
    def start_talking(self, base64_audio):
        self.ads_view.main_face.start_talking(base64_audio)

class PlayFaceThread(QThread):
    face_id = pyqtSignal(int)
    decibel_msg = pyqtSignal(int)
    websocket_status = pyqtSignal(list)  # Add new signal for WebSocket status
    def __init__(self, base64_audio=None):
        super().__init__()
        self.base64_audio = base64_audio
        
    
    def decibel_sub(self, msg):
        self.decibel_msg.emit(int(msg.data))
    
    def run(self):
        ...

def main(args=None):
    app = QApplication(sys.argv)
    main_face = FaceWidget()
    main_face.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()