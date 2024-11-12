from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QMenu, QLabel
from PyQt6.QtCore import Qt, QPropertyAnimation, QPoint, QTimer, QEasingCurve, QRect
from PyQt6.QtGui import QPainter, QColor, QAction, QPixmap, QIcon
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl
import sys
import subprocess
import platform
import math
import socket
import os

class OrbitIcon(QLabel):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setFixedSize(30, 30)
        self.angle = 0
        self.is_alive = False
        self.is_animating = False
        
        self.sound = QSoundEffect()
        self.sound.setSource(QUrl.fromLocalFile("sound.wav"))
        
        self.bjorn_pixmap = QPixmap("bjorn.png")
        self.bjorn_pixmap = self.bjorn_pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
        self.red_pixmap = QPixmap(30, 30)
        self.red_pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(self.red_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(255, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, 30, 30)
        painter.end()
        
        self.setPixmap(self.red_pixmap)
        
        self.move_animation = QPropertyAnimation(self, b"pos")
        self.move_animation.setDuration(1000)
        self.move_animation.setEasingCurve(QEasingCurve.Type.OutQuint)
        self.move_animation.finished.connect(self.on_center_animation_finished)
        
        self.zoom_animation = QPropertyAnimation(self, b"geometry")
        self.zoom_animation.setDuration(200)
        self.zoom_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        self.setMouseTracking(True)
        
    def on_center_animation_finished(self):
        self.is_animating = False
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_alive and not self.is_animating:
            self.sound.play()
            self.launch_ssh()
        elif event.button() == Qt.MouseButton.RightButton:
            if self.main_window:
                self.main_window.contextMenuEvent(event)
        else:
            if self.main_window:
                self.main_window.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.main_window:
            self.main_window.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.main_window:
            self.main_window.mouseReleaseEvent(event)

    def move_to_center(self):
        background_rect = self.parent().rect()
        center_x = background_rect.center().x() - self.width() // 2
        center_y = background_rect.center().y() - self.height() // 2
        self.move(QPoint(center_x, center_y))

    def set_status(self, is_alive):
        if is_alive != self.is_alive:
            self.is_alive = is_alive
            if is_alive:
                self.setFixedSize(100, 100)
                self.setPixmap(self.bjorn_pixmap)
                self.move_to_center()
            else:
                self.setFixedSize(30, 30)
                self.setPixmap(self.red_pixmap)
                self.is_animating = False
                
    def launch_ssh(self):
        try:
            bjorn_ip = socket.gethostbyname("bjorn.home")
            print(f"Adresse IP de bjorn.home : {bjorn_ip}")

            if platform.system() == "Windows":
                subprocess.Popen(["cmd.exe", "/c", "start", "cmd", "/k", f"echo Adresse IP de bjorn.home : {bjorn_ip} && ssh bjorn@bjorn.home"])
            else:
                subprocess.Popen(["x-terminal-emulator", "-e", "bash", "-c", f"echo Adresse IP de bjorn.home : {bjorn_ip}; ssh bjorn@bjorn.home"])
        
        except Exception as e:
            print(f"Erreur : {e}")
            self.set_status(False)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowIcon(QIcon("icon.png"))
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        self.circle_widget = QWidget()
        self.circle_widget.setFixedSize(200, 200)
        layout.addWidget(self.circle_widget)
        
        self.background = QPixmap("background.png")
        self.background = self.background.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
        self.orbit_icon = OrbitIcon(self.circle_widget, main_window=self)
        
        self.orbit_timer = QTimer(self)
        self.orbit_timer.timeout.connect(self.update_orbit)
        self.orbit_timer.start(50)
        
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.check_raspberry)
        self.check_timer.start(2000)
        
        self.dragging = False
        self.offset = None
        
        self.setFixedSize(220, 220)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        close_action = QAction("Fermer", self)
        close_action.triggered.connect(self.close)
        menu.addAction(close_action)
        menu.exec(event.globalPosition().toPoint())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.circle_widget.geometry()
        center_x = rect.center().x() - self.background.width() // 2
        center_y = rect.center().y() - self.background.height() // 2
        center_x -= 10
        centered_rect = QRect(center_x, center_y, self.background.width(), self.background.height())
        
        painter.drawPixmap(centered_rect, self.background)

    def update_orbit(self):
        if not self.orbit_icon.is_alive and not self.orbit_icon.is_animating:
            radius = 70
            center = QPoint(
                self.circle_widget.width() // 2,
                self.circle_widget.height() // 2
            )
            
            self.orbit_icon.angle += 0.05
            x = center.x() + radius * math.cos(self.orbit_icon.angle)
            y = center.y() + radius * math.sin(self.orbit_icon.angle)
            self.orbit_icon.move(int(x - 15), int(y - 15))
        
    def check_raspberry(self):
        try:
            socket.gethostbyname("bjorn.home")
            if not self.orbit_icon.is_alive:
                self.orbit_icon.set_status(True)
            self.orbit_icon.show()
        except socket.gaierror:
            if self.orbit_icon.is_alive:
                self.orbit_icon.set_status(False)
            self.orbit_icon.show()
            
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.position().toPoint()
        elif event.button() == Qt.MouseButton.RightButton:
            self.contextMenuEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging and self.offset:
            new_pos = event.globalPosition().toPoint() - self.offset
            self.move(new_pos)
            
    def mouseReleaseEvent(self, event):
        self.dragging = False

def main():
    required_files = ["bjorn.png", "background.png", "sound.wav"]
    for file in required_files:
        if not os.path.exists(file):
            print(f"Erreur: {file} non trouvé")
            return
            
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
