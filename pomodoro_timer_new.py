import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSystemTrayIcon, QMenu, QStyle
)
from PySide6.QtCore import QTimer, Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QAction, QFont, QPalette, QColor, QIcon
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from winotify import Notification


class PomodoroTimer(QMainWindow):
    def __init__(self):
        super().__init__()

        # ===== НАСТРОЙКИ =====
        self.WORK_TIME = 1 * 10
        self.BREAK_TIME = 5 * 60

        # ===== СОСТОЯНИЕ =====
        self.is_work_mode = True
        self.is_running = False
        self.time_left = self.WORK_TIME

        # ===== UI =====
        self.init_ui()

        # ===== ТАЙМЕР =====
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        # ===== АНИМАЦИЯ ФОНА =====
        self.color_animation = QPropertyAnimation(self, b"palette")
        self.color_animation.setDuration(800)
        self.color_animation.setEasingCurve(QEasingCurve.InOutQuad)

        # ===== СИСТЕМНЫЙ ТРЕЙ =====
        self.init_tray_icon()

        # ===== ПЕРЕМЕЩЕНИЕ ОКНА =====
        self.old_pos = None

        # ===== ОБРАБОТКА ЗАКРЫТИЯ ОКНА =====
        # Переопределяем обработчик закрытия окна
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)

    # ================= UI =================

    def init_ui(self):
        self.setWindowTitle("Pomodoro Timer")
        self.setFixedSize(500, 400)

        # Убираем рамку окна для более современного вида
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Создаем основной контейнер с закругленными углами
        central = QWidget(self)
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        # Добавляем эффект неонового свечения с начальным цветом
        self.add_neon_glow_effect(central, "#FF6B6B", 25)

        # Основной layout с отступами
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Верхняя панель с кнопкой закрытия
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 10)

        # Кнопка сворачивания
        self.minimize_button = QPushButton("−")
        self.minimize_button.setObjectName("minimizeButton")
        self.minimize_button.clicked.connect(self.showMinimized)

        # Кнопка закрытия
        self.close_button = QPushButton("×")
        self.close_button.setObjectName("closeButton")
        self.close_button.clicked.connect(self.hide)
        top_layout.addStretch()
        top_layout.addWidget(self.minimize_button)
        top_layout.addWidget(self.close_button)

        main_layout.addLayout(top_layout)

        # Заголовок с названием режима
        self.mode_label = QLabel("Время работы")
        self.mode_label.setObjectName("modeLabel")
        self.mode_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.mode_label)

        # Таймер с более крупным шрифтом
        self.timer_label = QLabel(self.format_time(self.time_left))
        self.timer_label.setObjectName("timerLabel")
        self.timer_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.timer_label)

        # Контейнер для кнопок
        buttons_layout = QHBoxLayout()

        # Кнопка старта/паузы с улучшенным дизайном
        self.start_button = QPushButton(" Старт")
        self.start_button.setObjectName("startButton")
        try:
            self.start_button.setIcon(QIcon("play_icon.png"))
        except:
            # Используем стандартную иконку, если файл не найден
            self.start_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.start_button.clicked.connect(self.toggle_timer)
        buttons_layout.addWidget(self.start_button)

        # Добавляем эффект свечения к кнопке старта
        self.add_neon_glow_effect(self.start_button, "#FF6B6B", 15)

        # Кнопка сброса
        self.reset_button = QPushButton(" Сброс")
        self.reset_button.setObjectName("resetButton")
        try:
            self.reset_button.setIcon(QIcon("reset_icon.png"))
        except:
            # Используем стандартную иконку, если файл не найден
            self.reset_button.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.reset_button.clicked.connect(self.reset_timer)
        buttons_layout.addWidget(self.reset_button)

        # Добавляем эффект свечения к кнопке сброса
        self.add_neon_glow_effect(self.reset_button, "#4ECDC4", 15)

        main_layout.addLayout(buttons_layout)

        # Применяем стили
        self.setStyleSheet("""
            #centralWidget {
                background-color: rgba(30, 30, 30, 0.95);
                border-radius: 20px;
                border: 2px solid #FF6B6B;
                /* Эффект неонового свечения для Qt */
                outline: 0;
            }
            #modeLabel {
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 24px;
                font-weight: 500;
                color: #FFFFFF;
                margin-bottom: 10px;
            }
            #timerLabel {
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 72px;
                font-weight: 700;
                color: #FFFFFF;
                margin: 20px 0;
            }
            #startButton {
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 18px;
                font-weight: 600;
                color: white;
                background-color: #FF6B6B;
                border: 2px solid #FF6B6B;
                border-radius: 10px;
                padding: 14px 32px;
                margin: 5px;
                text-align: left;
            }
            #startButton:hover {
                background-color: #E55555;
            }
            #startButton:pressed {
                background-color: #D14444;
            }
            #resetButton {
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 16px;
                font-weight: 600;
                color: white;
                background-color: #4ECDC4;
                border: 2px solid #4ECDC4;
                border-radius: 10px;
                padding: 12px 24px;
                margin: 5px;
                text-align: left;
            }
            #resetButton:hover {
                background-color: #3DBDB4;
            }
            #resetButton:pressed {
                background-color: #2CACB4;
            }
            #closeButton {
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 24px;
                font-weight: 600;
                color: #AAAAAA;
                background-color: transparent;
                border: none;
                border-radius: 15px;
                width: 30px;
                height: 30px;
                padding: 0;
                margin: 0;
            }
            #closeButton:hover {
                color: white;
                background-color: rgba(255, 107, 107, 0.7);
            }
            #closeButton:pressed {
                background-color: rgba(255, 107, 107, 0.9);
            }
            #minimizeButton {
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 24px;
                font-weight: 600;
                color: #AAAAAA;
                background-color: transparent;
                border: none;
                border-radius: 15px;
                width: 30px;
                height: 30px;
                padding: 0;
                margin: 0;
                margin-right: 5px;
            }
            #minimizeButton:hover {
                color: white;
                background-color: rgba(78, 205, 196, 0.7);
            }
            #minimizeButton:pressed {
                background-color: rgba(78, 205, 196, 0.9);
            }
        """)

        self.set_background_color("#FF6B6B")

    def add_neon_glow_effect(self, widget, color="#6366F1", blur_radius=25):
        """Добавляет эффект неонового свечения к виджету

        Args:
            widget: Виджет, к которому применяется эффект
            color: Цвет свечения в формате HEX
            blur_radius: Радиус размытия эффекта
        """
        # Создаем эффект тени для имитации свечения
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur_radius)  # Радиус размытия

        # Преобразуем HEX-цвет в QColor
        qcolor = QColor()
        qcolor.setNamedColor(color)
        shadow.setColor(qcolor)  # Цвет свечения

        shadow.setOffset(0, 0)  # Смещение тени (0,0 для свечения вокруг виджета)

        # Применяем эффект к виджету
        widget.setGraphicsEffect(shadow)

    def init_tray_icon(self):
        """Инициализация иконки в системном трее"""
        # Создаем иконку в системном трее
        self.tray_icon = QSystemTrayIcon(self)

        # Устанавливаем иконку
        try:
            icon = QIcon("icon.png")
            if icon.isNull():
                raise ValueError("Icon file not found or invalid")
            self.tray_icon.setIcon(icon)
        except:
            # Используем стандартную иконку
            self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))

        # Создаем контекстное меню для иконки
        tray_menu = QMenu()

        # Добавляем действие для показа/скрытия окна
        show_action = QAction("Показать/Скрыть", self)
        show_action.triggered.connect(self.toggle_window_visibility)
        tray_menu.addAction(show_action)

        # Добавляем действие для выхода
        quit_action = QAction("Выход", self)
        quit_action.triggered.connect(self.force_quit)
        tray_menu.addAction(quit_action)

        # Устанавливаем контекстное меню
        self.tray_icon.setContextMenu(tray_menu)

        # Показываем иконку в системном трее
        self.tray_icon.show()

        # Убедимся, что иконка действительно видима
        if not self.tray_icon.isVisible():
            # Если иконка не видима, попробуем снова
            self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
            self.tray_icon.show()

        # Обработка двойного клика по иконке
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

    def toggle_window_visibility(self):
        """Переключает видимость окна"""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()

    def on_tray_icon_activated(self, reason):
        """Обработка активации иконки в системном трее"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.toggle_window_visibility()

    def minimize_to_tray(self):
        """Сворачивает окно в системный трей"""
        self.hide()

    def restore_from_tray(self):
        """Восстанавливает окно из системного трея"""
        self.show()
        self.raise_()
        self.activateWindow()

    # ================= ЛОГИКА =================

    def toggle_timer(self):
        if self.is_running:
            self.timer.stop()
            self.start_button.setText(" Старт")
            try:
                self.start_button.setIcon(QIcon("play_icon.png"))
            except:
                self.start_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.is_running = False
        else:
            self.timer.start(1000)
            self.start_button.setText(" Пауза")
            try:
                self.start_button.setIcon(QIcon("pause_icon.png"))
            except:
                self.start_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.is_running = True

            # Сворачиваем окно в системный трей
            # if self.is_work_mode:
            #     self.show_notification("Таймер запущен", "Время работать 💪")

            if self.is_work_mode:
                self.show_notification("Таймер запущен", "Время работать 💪")
            else:
                self.show_notification("Отдых", "Начался отдых ☕")

            QTimer.singleShot(300, self.minimize_to_tray)

    def reset_timer(self):
        """Сбрасывает таймер в начальное состояние"""
        self.timer.stop()
        self.is_running = False
        self.start_button.setText(" Старт")
        try:
            self.start_button.setIcon(QIcon("play_icon.png"))
        except:
            self.start_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

        # Сбрасываем в зависимости от текущего режима
        if self.is_work_mode:
            self.time_left = self.WORK_TIME
            self.mode_label.setText("Время работы")
        else:
            self.time_left = self.BREAK_TIME
            self.mode_label.setText("Время отдыха")

        self.timer_label.setText(self.format_time(self.time_left))

    def update_timer(self):
        self.time_left -= 1
        self.timer_label.setText(self.format_time(self.time_left))

        if self.time_left <= 0:
            self.switch_mode()

    def switch_mode(self):
        self.timer.stop()
        self.is_running = False
        self.start_button.setText(" Старт")
        try:
            self.start_button.setIcon(QIcon("play_icon.png"))
        except:
            self.start_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

        # Восстанавливаем окно из системного трея
        self.restore_from_tray()

        if self.is_work_mode:
            self.is_work_mode = False
            self.time_left = self.BREAK_TIME
            self.mode_label.setText("Время отдыха")
            self.animate_background_color("#4ECDC4")

            # Обновляем цвет рамки
            current_style = self.styleSheet()
            updated_style = current_style.replace("#FF6B6B", "#4ECDC4")
            self.setStyleSheet(updated_style)

            # Обновляем эффект свечения основного виджета
            self.add_neon_glow_effect(self.centralWidget(), "#4ECDC4", 25)

            self.show_notification("Перерыв", "Пора отдохнуть 🧘‍♂️")
        else:
            self.is_work_mode = True
            self.time_left = self.WORK_TIME
            self.mode_label.setText("Время работы")
            self.animate_background_color("#FF6B6B")

            # Обновляем цвет рамки
            current_style = self.styleSheet()
            updated_style = current_style.replace("#4ECDC4", "#FF6B6B")
            self.setStyleSheet(updated_style)

            # Обновляем эффект свечения основного виджета
            self.add_neon_glow_effect(self.centralWidget(), "#FF6B6B", 25)

            self.show_notification("Работа", "Пора работать 💼")

        self.timer_label.setText(self.format_time(self.time_left))

    # ================= ОБРАБОТКА ЗАКРЫТИЯ ОКНА =================

    def closeEvent(self, event):
        """Обработка события закрытия окна"""
        event.ignore()  # Игнорируем событие закрытия
        self.hide()  # Скрываем окно вместо закрытия

    def force_quit(self):
        """Принудительное завершение приложения"""
        QApplication.quit()

    # ================= ПЕРЕМЕЩЕНИЕ ОКНА =================

    def mousePressEvent(self, event):
        """Обработка нажатия кнопки мыши"""
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        """Обработка отпускания кнопки мыши"""
        if event.button() == Qt.LeftButton:
            self.old_pos = None

    def mouseMoveEvent(self, event):
        """Обработка перемещения мыши для перетаскивания окна"""
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    # ================= WINDOWS TOAST =================

    def show_notification(self, title, message):
        toast = Notification(
            app_id="Pomodoro Timer",
            title=title,
            msg=message,
            duration="short"
        )
        toast.show()

    # ================= ВСПОМОГАТЕЛЬНОЕ =================

    def format_time(self, seconds):
        m, s = divmod(seconds, 60)
        return f"{m:02d}:{s:02d}"

    def set_background_color(self, color):
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

    def animate_background_color(self, color):
        start = self.palette()
        end = self.palette()
        end.setColor(QPalette.Window, QColor(color))
        self.color_animation.setStartValue(start)
        self.color_animation.setEndValue(end)
        self.color_animation.start()


# ================= ЗАПУСК =================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = PomodoroTimer()
    window.show()

    sys.exit(app.exec())
