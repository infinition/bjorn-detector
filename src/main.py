import argparse
import ctypes
import logging
import threading
from logging.handlers import RotatingFileHandler
import math
import os
import platform
import socket
import subprocess
import sys
import time
from PyQt6.QtCore import (
    Qt,
    QPropertyAnimation,
    QPoint,
    QTimer,
    QEasingCurve,
    QRect,
    pyqtSignal,
    QUrl,
)
from PyQt6.QtGui import QPainter, QColor, QAction, QPixmap, QIcon
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QMenu, QLabel
from src.config import settings

# Import notification functions
from src.utils.telegram.main import send_telegram_message
from src.utils.discord.main import send_discord_message
from src.utils.smtp.main import send_smtp_email

if platform.system() == "Windows":
    app_id = "bjorn-cyberviking.bjorn.detector"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

BJORN_ICON = "src//static//images//icon.ico"
BJORN_IMAGE = "src//static//images//bjorn.png"
BJORN_BACKGROUND = "src//static//images//background.png"
BJORN_SOUND = "src//static//sounds//sound.wav"

# Configure logger
logger = logging.getLogger("__main__")


def configure_logger(log_level: str = "INFO") -> None:
    """
    Configures the logger with rotating file handler and console handler.

    Args:
        log_level (str): Logging level (INFO, DEBUG, etc.).
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")

    logger.setLevel(numeric_level)

    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        "logs/bjorn-detector.log", maxBytes=5 * 1024 * 1024, backupCount=5
    )
    # Console handler
    console_handler = logging.StreamHandler()

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="One-Click SSH access to your bjorn device in a radar style."
    )
    parser.add_argument(
        "--identity-file",
        "--i",
        type=str,
        help="Identity file used to connect device if set on install. Defaults to None.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        choices=range(10, 300),
        metavar="[10-300]",
        help="Timeout in seconds. Defaults to 50 seconds. Must be between 10 to 300.",
    )
    parser.add_argument(
        "--no-gui",
        action="store_false",
        dest="gui",
        help="Starts without a graphics user interface.",
    )
    parser.add_argument(
        "--log-level",
        choices=["INFO", "DEBUG"],
        default="INFO",
        help="Logging level. Defaults to INFO.",
    )
    return parser.parse_args()


class OrbitIcon(QLabel):
    """
    Draw red circle on UI
    """

    def __init__(self, parent=None, main_window=None, id_file=None):
        """Init Method"""
        super().__init__(parent)
        self.main_window = main_window
        self.setFixedSize(30, 30)
        self.angle = 0
        self.is_alive = False
        self.is_animating = False
        self.id_file = id_file
        self.sound = QSoundEffect()
        self.sound.setSource(QUrl.fromLocalFile(BJORN_SOUND))

        self.bjorn_pixmap = QPixmap(BJORN_IMAGE)
        self.bjorn_pixmap = self.bjorn_pixmap.scaled(
            100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )

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

    def set_status(self, is_alive: bool):
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
        i_complement = ""
        try:
            bjorn_ip = socket.gethostbyname("bjorn.home")
            logger.debug(f"bjorn.home IP Address: {bjorn_ip}")

            logger.debug(f"Platform: {platform.system()}")

            if self.id_file is not None:
                i_complement = f"-i {self.id_file}"

            if platform.system() == "Windows":
                subprocess.Popen(
                    [
                        "cmd.exe",
                        "/c",
                        "start",
                        "cmd",
                        "/k",
                        f"echo bjorn.home IP Address : {bjorn_ip} && ssh {i_complement} bjorn@bjorn.home",
                    ]
                )
            else:
                subprocess.Popen(
                    [
                        "x-terminal-emulator",
                        "-e",
                        "bash",
                        "-c",
                        f"echo bjorn.home IP Address : {bjorn_ip}; ssh {i_complement} bjorn@bjorn.home",
                    ]
                )

        except Exception as e:
            logger.error(f"Can't perform operation, Caused by: {e}")
            self.set_status(False)


class MainWindow(QMainWindow):
    activity_occurred = pyqtSignal()

    def __init__(self, id_file=None):
        """Init Method"""
        super().__init__()
        self.offset = None
        self.dragging = None
        self.check_timer = None
        self.background = None
        self.orbit_icon = None
        self.circle_widget = None
        self.orbit_timer = None
        self.id_file = id_file
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowIcon(QIcon(BJORN_ICON))
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.circle_widget = QWidget()
        self.circle_widget.setFixedSize(200, 200)
        layout.addWidget(self.circle_widget)

        self.background = QPixmap(BJORN_BACKGROUND)
        self.background = self.background.scaled(
            200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )

        self.orbit_icon = OrbitIcon(self.circle_widget, main_window=self, id_file=self.id_file)

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
        close_action = QAction("Close", self)
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
            center = QPoint(self.circle_widget.width() // 2, self.circle_widget.height() // 2)

            self.orbit_icon.angle += 0.05
            x = center.x() + radius * math.cos(self.orbit_icon.angle)
            y = center.y() + radius * math.sin(self.orbit_icon.angle)
            self.orbit_icon.move(int(x - 15), int(y - 15))

    def check_raspberry(self):
        try:
            socket.gethostbyname("bjorn.home")
            if not self.orbit_icon.is_alive:
                self.orbit_icon.set_status(True)
            self.activity_occurred.emit()
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


def notify_found(bjorn_ip: str):
    """
    Sends notifications via Telegram, Discord, and SMTP when a bjorn is found.

    Args:
        bjorn_ip (str): IP address of the bjorn device.
    """
    message = f"🔍 *Bjorn Device Detected!* 🖥️\nIP Address: {bjorn_ip}"
    subject = "Bjorn Device Detected"

    if settings.telegram:
        # Send Telegram notification
        send_telegram_message(message)
    elif settings.discord:
        # Send Discord notification
        send_discord_message(message)
    elif settings.smtp:
        # Send SMTP email
        send_smtp_email(subject, message.replace("🔍 ", "").replace("🖥️\n", "\n"))
    else:
        logger.debug("No notification configuration.")


class MainThread(threading.Thread):
    """
    Thread to perform checks without launching the GUI.
    """

    def __init__(self, timeout: int):
        """
        Initialize the MainThread.

        Args:
            timeout (int): Timeout in seconds.
        """
        super().__init__()
        self.timeout = timeout
        self.last_success_time = time.time()
        self.timeout_occurred = False
        self._stop_event = threading.Event()

    def run(self):
        """Run the thread to perform the check."""
        try:
            while not self._stop_event.is_set():
                try:
                    bjorn_ip = socket.gethostbyname("bjorn.home")
                    logger.info(f"Bjorn device is reachable. Bjorn device IP: {bjorn_ip}")
                    self.last_success_time = time.time()
                    notify_found(bjorn_ip)
                except socket.gaierror:
                    logger.warning("Bjorn device is not reachable.")

                if time.time() - self.last_success_time > self.timeout:
                    logger.warning(f"Timeout reached. No response after {self.timeout} seconds.")
                    self.timeout_occurred = True
                    break

                time.sleep(30)

        except Exception as e:
            logger.error(f"An error occurred in MainThread: {e}")

        if self.timeout_occurred:
            sys.exit(1)
        else:
            sys.exit(0)

    def stop(self):
        """Set the stop event to terminate the thread."""
        self._stop_event.set()


def main():
    """
    Main function to run the bjorn detector script.
    """
    start_time = time.time()
    timeout_occurred = [False]

    args = parse_arguments()
    configure_logger(args.log_level)

    timeout = args.timeout if args.timeout else settings.timeout

    required_files = [BJORN_ICON, BJORN_IMAGE, BJORN_BACKGROUND, BJORN_SOUND]
    for file in required_files:
        if not os.path.exists(file):
            logger.error(f"File: {file} doesn't exist")
            return

    app = QApplication(sys.argv)

    def handle_timeout():
        logger.warning(f"Timeout reached. No response after {timeout} seconds.")
        timeout_occurred[0] = True
        app.quit() if args.gui else exit(1)

    if args.gui:
        try:
            app.setApplicationName("BjornDetector")
            app.setApplicationDisplayName("Bjorn Detector")
            app.setOrganizationName("BjornCyberviking")
            app.setWindowIcon(QIcon(BJORN_ICON))
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(handle_timeout)
            timer.start(timeout * 1000)
            window = MainWindow(id_file=args.identity_file)
            window.activity_occurred.connect(timer.stop)
            window.show()
            app.exec()
        except Exception as e_gui:
            logger.error(f"Can't perform operation, Caused by: {e_gui}")
        finally:
            end_time = time.time()
            time_elapsed = end_time - start_time
            logger.debug(f"End. Session time: {time_elapsed:.4f} seconds")
    else:
        logger.debug("Starting in non-GUI mode.")
        main_thread = MainThread(timeout=timeout)
        main_thread.start()
        try:
            while main_thread.is_alive():
                main_thread.join(timeout=1)
        except KeyboardInterrupt:
            logger.info("SIGTERM Signal Received...")
            main_thread.stop()
            main_thread.join()
            sys.exit(0)
        except Exception as e_no_gui:
            logger.error(f"Cannot perform operation in non-GUI mode, caused by: {e_no_gui}")
            sys.exit(1)
        finally:
            end_time = time.time()
            time_elapsed = end_time - start_time
            logger.debug(f"End. Session time: {time_elapsed:.4f} seconds")


if __name__ == "__main__":
    main()
