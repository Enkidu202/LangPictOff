import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QFrame,
    QPushButton,
    QFileDialog,
)

from PyQt5.QtCore import Qt
from Capturer import Capture


class ScreenRegionSelector(QMainWindow):
    
    def __init__(self,):
        super().__init__(None)
        self.m_width = 400
        self.m_height = 500

        self.setWindowTitle("Screen Capturer")
        self.setMinimumSize(self.m_width, self.m_height)

        frame = QFrame()
        frame.setContentsMargins(0, 0, 0, 0)
        lay = QVBoxLayout(frame)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setContentsMargins(5, 5, 5, 5)

        self.label = QLabel()
        self.btn_capture = QPushButton("Capture")
        self.btn_capture.clicked.connect(self.capture)
        
        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self.save)
        self.btn_save.setVisible(False)

        self.btn_push = QPushButton("Push")
        self.btn_push.clicked.connect(self.push)
        self.btn_push.setVisible(False)

        lay.addWidget(self.label)
        lay.addWidget(self.btn_capture)
        lay.addWidget(self.btn_save)
        lay.addWidget(self.btn_push)

        self.setCentralWidget(frame)
        
        self.file_path = None  # To store the file path after saving

    def capture(self):
        self.capturer = Capture(self)
        self.capturer.show()
        self.btn_save.setVisible(True)
        self.btn_push.setVisible(True)

    def save(self, push=False):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Image files (*.png *.jpg *.bmp)")
        if file_name:
            self.capturer.imgmap.save(file_name)
            if push:
                self.file_path = file_name
                self.close()
                return file_name 

    def push(self):
        self.save(push=True)

    def get_file_path(self):
        return self.file_path

def main():
    app = QApplication(sys.argv)    
    app.setStyleSheet("""
    QFrame {
        background-color: #3f3f3f;
    }
                      
    QPushButton {
        border-radius: 5px;
        background-color: rgb(60, 90, 255);
        padding: 10px;
        color: white;
        font-weight: bold;
        font-family: Arial;
        font-size: 12px;
    }
                      
    QPushButton::hover {
        background-color: rgb(60, 20, 255)
    }
    """)
    selector = ScreenRegionSelector()
    selector.show()
    app.exec_() 
    file_path = selector.get_file_path()
    return file_path 
