from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

class TimerWidget(QWidget):
    """
    Виджет для отображения таймера и кнопок управления.
    """
    # Сигналы для оповещения о действиях пользователя
    start_clicked = Signal()
    reset_clicked = Signal()
    settings_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Создаем layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Таймер
        self.timer_label = QLabel("25:00")
        self.timer_label.setObjectName("timerLabel")
        self.timer_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.timer_label)

        # Контейнер для кнопок
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(20)

        # Кнопка сброса
        self.reset_button = QPushButton()
        self.reset_button.setObjectName("resetButton")
        self.reset_button.setFixedSize(60, 60)
        self.reset_button.setCursor(Qt.PointingHandCursor)
        try:
            self.reset_button.setIcon(QIcon("reset_icon.svg"))
        except:
            # Используем стандартную иконку, если файл не найден
            from PySide6.QtGui import QPixmap
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.green)
            self.reset_button.setIcon(QIcon(pixmap))
        self.reset_button.setIconSize(self.reset_button.size() * 0.6)
        self.reset_button.clicked.connect(self.reset_clicked.emit)
        buttons_layout.addWidget(self.reset_button)

        # Кнопка старта/паузы
        self.start_button = QPushButton("Старт")
        self.start_button.setObjectName("startButton")
        self.start_button.setFixedSize(160, 60)
        self.start_button.setCursor(Qt.PointingHandCursor)
        try:
            self.start_button.setIcon(QIcon("play_icon.png"))
        except:
            # Используем стандартную иконку, если файл не найден
            from PySide6.QtGui import QPixmap
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.yellow)
            self.start_button.setIcon(QIcon(pixmap))
        self.start_button.setIconSize(self.start_button.size() * 0.15)
        self.start_button.clicked.connect(self.start_clicked.emit)
        buttons_layout.addWidget(self.start_button)

        # Кнопка настроек
        self.settings_button = QPushButton()
        self.settings_button.setObjectName("settingsButton")
        self.settings_button.setFixedSize(60, 60)
        self.settings_button.setCursor(Qt.PointingHandCursor)
        try:
            self.settings_button.setIcon(QIcon("settings_icon.svg"))
        except:
            # Используем стандартную иконку, если файл не найден
            from PySide6.QtGui import QPixmap
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.blue)
            self.settings_button.setIcon(QIcon(pixmap))
        self.settings_button.setIconSize(self.settings_button.size() * 0.6)
        self.settings_button.clicked.connect(self.settings_clicked.emit)
        buttons_layout.addWidget(self.settings_button)

        layout.addWidget(buttons_container)

    def update_time(self, time_str):
        """Обновляет отображаемое время."""
        self.timer_label.setText(time_str)

    def set_start_button_text(self, text):
        """Устанавливает текст на кнопке старта."""
        self.start_button.setText(text)

    def set_start_button_icon(self, icon_path=None):
        """Устанавливает иконку на кнопке старта."""
        try:
            if icon_path:
                self.start_button.setIcon(QIcon(icon_path))
            else:
                # Если путь не указан, используем стандартную иконку
                from PySide6.QtGui import QPixmap
                pixmap = QPixmap(16, 16)
                pixmap.fill(Qt.yellow)
                self.start_button.setIcon(QIcon(pixmap))
        except:
            # Используем стандартную иконку, если файл не найден
            from PySide6.QtGui import QPixmap
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.yellow)
            self.start_button.setIcon(QIcon(pixmap))

        self.start_button.setIconSize(self.start_button.size() * 0.15)
