import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSystemTrayIcon, QMenu, QStyle, QTabBar, QSlider
)
from PySide6.QtCore import QTimer, Qt, QPropertyAnimation, QEasingCurve, QRect, QSize
from PySide6.QtGui import QAction, QFont, QPalette, QColor, QIcon, QPainter, QLinearGradient
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QFrame
from winotify import Notification


class PomodoroTimer(QMainWindow):
    def __init__(self):
        super().__init__()

        # ===== НАСТРОЙКИ =====
        self.WORK_TIME = 25 * 60  # 25 минут по умолчанию
        self.BREAK_TIME = 5 * 60

        # ===== СОСТОЯНИЕ =====
        self.is_work_mode = True
        self.is_running = False
        self.time_left = self.WORK_TIME
        self.settings_visible = False

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
        self.setFixedSize(540, 460)

        # Убираем рамку окна для более современного вида
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Создаем основной контейнер с закругленными углами
        central = QWidget(self)
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        # Основной layout с отступами
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Верхняя панель с вкладками
        tabs_container = QWidget()
        tabs_container.setObjectName("tabsContainer")
        tabs_layout = QVBoxLayout(tabs_container)
        tabs_layout.setContentsMargins(30, 30, 30, 0)

        # Создаем вкладки в стиле macOS
        self.tab_bar = QTabBar()
        self.tab_bar.setObjectName("tabBar")
        self.tab_bar.addTab("Работа")
        self.tab_bar.addTab("Отдых")
        self.tab_bar.setCurrentIndex(0)  # По умолчанию активна вкладка "Работа"
        self.tab_bar.setExpanding(False)
        self.tab_bar.setDrawBase(False)  # Убираем базовую линию
        self.tab_bar.setCursor(Qt.PointingHandCursor)

        # Обработка переключения вкладок
        self.tab_bar.currentChanged.connect(self.on_tab_changed)

        tabs_layout.addWidget(self.tab_bar)
        main_layout.addWidget(tabs_container)

        # Контейнер для содержимого с эффектом glassmorphism
        content_container = QWidget()
        content_container.setObjectName("contentContainer")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(30, 30, 30, 30)

        # Таймер с более крупным шрифтом
        self.timer_label = QLabel(self.format_time(self.time_left))
        self.timer_label.setObjectName("timerLabel")
        self.timer_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.timer_label)

        # Контейнер для кнопок
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(20)

        # Кнопка сброса (только иконка)
        self.reset_button = QPushButton()
        self.reset_button.setObjectName("resetButton")
        self.reset_button.setFixedSize(60, 60)
        self.reset_button.setCursor(Qt.PointingHandCursor)
        try:
            self.reset_button.setIcon(QIcon("reset_icon.png"))
        except:
            # Используем стандартную иконку, если файл не найден
            self.reset_button.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.reset_button.setIconSize(QSize(24, 24))
        self.reset_button.clicked.connect(self.reset_timer)
        buttons_layout.addWidget(self.reset_button)

        # Кнопка старта/паузы с улучшенным дизайном
        self.start_button = QPushButton("Старт")
        self.start_button.setObjectName("startButton")
        self.start_button.setFixedSize(160, 60)
        self.start_button.setCursor(Qt.PointingHandCursor)
        try:
            self.start_button.setIcon(QIcon("play_icon.png"))
        except:
            # Используем стандартную иконку, если файл не найден
            self.start_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.start_button.setIconSize(QSize(24, 24))
        self.start_button.clicked.connect(self.toggle_timer)
        buttons_layout.addWidget(self.start_button)

        # Кнопка настроек времени (иконка с цифрой 6)
        self.settings_button = QPushButton("6")
        self.settings_button.setObjectName("settingsButton")
        self.settings_button.setFixedSize(60, 60)
        self.settings_button.setCursor(Qt.PointingHandCursor)
        self.settings_button.clicked.connect(self.toggle_settings)
        buttons_layout.addWidget(self.settings_button)

        content_layout.addWidget(buttons_container)

        # Панель настроек времени (изначально скрыта)
        self.settings_panel = QWidget()
        self.settings_panel.setObjectName("settingsPanel")
        self.settings_panel.setFixedHeight(0)
        settings_layout = QVBoxLayout(self.settings_panel)
        settings_layout.setContentsMargins(20, 20, 20, 20)

        settings_label = QLabel("Длительность таймера (минуты):")
        settings_label.setObjectName("settingsLabel")
        settings_layout.addWidget(settings_label)

        # Слайдер для настройки времени
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setObjectName("timeSlider")
        self.time_slider.setMinimum(1)
        self.time_slider.setMaximum(60)
        self.time_slider.setValue(25)
        self.time_slider.setTickPosition(QSlider.TicksBelow)
        self.time_slider.setTickInterval(5)
        self.time_slider.valueChanged.connect(self.update_timer_duration)
        settings_layout.addWidget(self.time_slider)

        # Отображение текущего значения слайдера
        self.time_value_label = QLabel("25 минут")
        self.time_value_label.setObjectName("timeValueLabel")
        self.time_value_label.setAlignment(Qt.AlignCenter)
        settings_layout.addWidget(self.time_value_label)

        content_layout.addWidget(self.settings_panel)

        main_layout.addWidget(content_container)

        # Верхняя панель с кнопками управления окном
        top_panel = QWidget()
        top_panel.setObjectName("topPanel")
        top_panel.setFixedHeight(40)
        top_layout = QHBoxLayout(top_panel)
        top_layout.setContentsMargins(0, 0, 10, 0)

        # Кнопка сворачивания
        self.minimize_button = QPushButton("−")
        self.minimize_button.setObjectName("minimizeButton")
        self.minimize_button.setFixedSize(30, 30)
        self.minimize_button.clicked.connect(self.showMinimized)

        # Кнопка закрытия
        self.close_button = QPushButton("×")
        self.close_button.setObjectName("closeButton")
        self.close_button.setFixedSize(30, 30)
        self.close_button.clicked.connect(self.hide)
        top_layout.addStretch()
        top_layout.addWidget(self.minimize_button)
        top_layout.addWidget(self.close_button)

        main_layout.addWidget(top_panel)

        # Применяем стили
        self.setStyleSheet("""
            QMainWindow {
                background: transparent;
            }
            #centralWidget {
                background-color: rgba(160, 152, 159, 0.5);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
            #tabsContainer {
                background-color: transparent;
            }
            #tabBar {
                background: transparent;
                margin-left: 20px;
            }
            #tabBar::tab {
                background-color: rgba(255, 255, 255, 0.25);
                color: rgba(255, 255, 255, 0.7);
                padding: 12px 24px;
                margin-right: 8px;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                font-family: "SF Pro Display", "Segoe UI", Arial, sans-serif;
                font-size: 14px;
                font-weight: 500;
                min-width: 80px;
            }
            #tabBar::tab:selected {
                background-color: rgba(255, 255, 255, 0.4);
                color: white;
                border-bottom: 2px solid rgba(255, 255, 255, 0.5);
            }
            #tabBar::tab:hover:!selected {
                background-color: rgba(255, 255, 255, 0.35);
            }
            #contentContainer {
                background-color: rgba(255, 255, 255, 0.25);
                border-radius: 16px;
                margin: 10px 30px 20px 30px;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
            #timerLabel {
                font-family: "SF Pro Display", "Segoe UI", Arial, sans-serif;
                font-size: 72px;
                font-weight: 300;
                color: white;
                margin: 30px 0;
                letter-spacing: -2px;
            }
            #startButton {
                font-family: "SF Pro Display", "Segoe UI", Arial, sans-serif;
                font-size: 16px;
                font-weight: 600;
                color: white;
                background-color: rgba(255, 107, 107, 0.8);
                border: 1px solid rgba(255, 107, 107, 0.5);
                border-radius: 30px;
                padding: 0;
            }
            #startButton:hover {
                background-color: rgba(255, 107, 107, 0.9);
                border: 1px solid rgba(255, 107, 107, 0.7);
            }
            #startButton:pressed {
                background-color: rgba(255, 107, 107, 0.7);
            }
            #resetButton {
                background-color: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 30px;
                color: white;
            }
            #resetButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
            #resetButton:pressed {
                background-color: rgba(255, 255, 255, 0.1);
            }
            #settingsButton {
                font-family: "SF Pro Display", "Segoe UI", Arial, sans-serif;
                font-size: 18px;
                font-weight: 600;
                color: white;
                background-color: rgba(78, 205, 196, 0.8);
                border: 1px solid rgba(78, 205, 196, 0.5);
                border-radius: 30px;
            }
            #settingsButton:hover {
                background-color: rgba(78, 205, 196, 0.9);
                border: 1px solid rgba(78, 205, 196, 0.7);
            }
            #settingsButton:pressed {
                background-color: rgba(78, 205, 196, 0.7);
            }
            #settingsPanel {
                background-color: rgba(255, 255, 255, 0.25);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.3);
                margin: 10px 0;
            }
            #settingsLabel {
                font-family: "SF Pro Display", "Segoe UI", Arial, sans-serif;
                font-size: 14px;
                font-weight: 500;
                color: white;
                margin-bottom: 10px;
            }
            #timeSlider {
                height: 6px;
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 3px;
            }
            #timeSlider::groove:horizontal {
                height: 6px;
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 3px;
            }
            #timeSlider::handle:horizontal {
                background-color: white;
                width: 18px;
                height: 18px;
                border-radius: 9px;
                margin: -6px 0;
            }
            #timeValueLabel {
                font-family: "SF Pro Display", "Segoe UI", Arial, sans-serif;
                font-size: 14px;
                font-weight: 500;
                color: white;
                margin-top: 10px;
            }
            #topPanel {
                background-color: transparent;
            }
            #closeButton {
                font-family: "SF Pro Display", "Segoe UI", Arial, sans-serif;
                font-size: 18px;
                font-weight: 600;
                color: rgba(255, 255, 255, 0.7);
                background-color: transparent;
                border: none;
                border-radius: 15px;
            }
            #closeButton:hover {
                color: white;
                background-color: rgba(255, 107, 107, 0.3);
            }
            #closeButton:pressed {
                background-color: rgba(255, 107, 107, 0.5);
            }
            #minimizeButton {
                font-family: "SF Pro Display", "Segoe UI", Arial, sans-serif;
                font-size: 18px;
                font-weight: 600;
                color: rgba(255, 255, 255, 0.7);
                background-color: transparent;
                border: none;
                border-radius: 15px;
                margin-right: 5px;
            }
            #minimizeButton:hover {
                color: white;
                background-color: rgba(78, 205, 196, 0.3);
            }
            #minimizeButton:pressed {
                background-color: rgba(78, 205, 196, 0.5);
            }
        """)

        self.set_background_color("#FF6B6B")

    def add_glassmorphism_effect(self, widget, blur_radius=15, opacity=0.5):
        """Добавляет эффект glassmorphism к виджету

        Args:
            widget: Виджет, к которому применяется эффект
            blur_radius: Радиус размытия эффекта
            opacity: Прозрачность фона
        """
        # Создаем эффект тени для glassmorphism
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur_radius)  # Радиус размытия
        shadow.setColor(QColor(0, 0, 0, 30))  # Цвет тени с прозрачностью
        shadow.setOffset(0, 4)  # Смещение тени
        widget.setGraphicsEffect(shadow)

        # Устанавливаем прозрачный фон
        widget.setStyleSheet(widget.styleSheet() + f"background-color: rgba(255, 255, 255, {opacity});")

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
            self.start_button.setText("Старт")
            try:
                self.start_button.setIcon(QIcon("play_icon.png"))
            except:
                self.start_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.is_running = False
        else:
            self.timer.start(1000)
            self.start_button.setText("Пауза")
            try:
                self.start_button.setIcon(QIcon("pause_icon.png"))
            except:
                self.start_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.is_running = True

            if self.is_work_mode:
                self.show_notification("Таймер запущен", "Время работать 💪")
            else:
                self.show_notification("Отдых", "Начался отдых ☕")

            QTimer.singleShot(300, self.minimize_to_tray)

    def reset_timer(self):
        """Сбрасывает таймер в начальное состояние"""
        self.timer.stop()
        self.is_running = False
        self.start_button.setText("Старт")
        try:
            self.start_button.setIcon(QIcon("play_icon.png"))
        except:
            self.start_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

        # Сбрасываем в зависимости от текущего режима
        if self.is_work_mode:
            self.time_left = self.WORK_TIME
            self.tab_bar.setCurrentIndex(0)  # Устанавливаем вкладку "Работа"
        else:
            self.time_left = self.BREAK_TIME
            self.tab_bar.setCurrentIndex(1)  # Устанавливаем вкладку "Отдых"

        self.timer_label.setText(self.format_time(self.time_left))

    def update_timer(self):
        self.time_left -= 1
        self.timer_label.setText(self.format_time(self.time_left))

        if self.time_left <= 0:
            self.switch_mode()

    def switch_mode(self):
        self.timer.stop()
        self.is_running = False
        self.start_button.setText("Старт")
        try:
            self.start_button.setIcon(QIcon("play_icon.png"))
        except:
            self.start_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

        # Восстанавливаем окно из системного трея
        self.restore_from_tray()

        if self.is_work_mode:
            self.is_work_mode = False
            self.time_left = self.BREAK_TIME
            self.tab_bar.setCurrentIndex(1)  # Устанавливаем вкладку "Отдых"

            # Обновляем стиль для режима отдыха
            self.update_style_for_mode(False)

            self.show_notification("Перерыв", "Пора отдохнуть 🧘‍♂️")
        else:
            self.is_work_mode = True
            self.time_left = self.WORK_TIME
            self.tab_bar.setCurrentIndex(0)  # Устанавливаем вкладку "Работа"

            # Обновляем стиль для режима работы
            self.update_style_for_mode(True)

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

    def on_tab_changed(self, index):
        """Обработка переключения вкладок"""
        if index == 0:  # Вкладка "Работа"
            if not self.is_work_mode:
                self.is_work_mode = True
                self.time_left = self.WORK_TIME
                self.timer_label.setText(self.format_time(self.time_left))
                self.update_style_for_mode(True)
        else:  # Вкладка "Отдых"
            if self.is_work_mode:
                self.is_work_mode = False
                self.time_left = self.BREAK_TIME
                self.timer_label.setText(self.format_time(self.time_left))
                self.update_style_for_mode(False)

    def update_style_for_mode(self, is_work_mode):
        """Обновляет стили интерфейса в зависимости от режима"""
        current_style = self.styleSheet()

        if is_work_mode:
            # Стиль для режима работы
            updated_style = current_style.replace("rgba(255, 107, 107, 0.8)", "rgba(255, 107, 107, 0.8)")
            updated_style = updated_style.replace("rgba(78, 205, 196, 0.8)", "rgba(78, 205, 196, 0.8)")

            # Добавляем эффект свечения для режима работы
            self.add_neon_glow_effect(self.centralWidget(), "#FF6B6B", 25)
        else:
            # Стиль для режима отдыха
            updated_style = current_style.replace("rgba(255, 107, 107, 0.8)", "rgba(78, 205, 196, 0.8)")
            updated_style = updated_style.replace("rgba(78, 205, 196, 0.8)", "rgba(255, 107, 107, 0.8)")

            # Добавляем эффект свечения для режима отдыха
            self.add_neon_glow_effect(self.centralWidget(), "#4ECDC4", 25)

        self.setStyleSheet(updated_style)

    def toggle_settings(self):
        """Переключает видимость панели настроек"""
        if self.settings_visible:
            # Скрываем панель настроек
            self.settings_animation = QPropertyAnimation(self.settings_panel, b"maximumHeight")
            self.settings_animation.setDuration(300)
            self.settings_animation.setStartValue(self.settings_panel.height())
            self.settings_animation.setEndValue(0)
            self.settings_animation.setEasingCurve(QEasingCurve.InOutQuad)
            self.settings_animation.start()

            self.settings_visible = False
        else:
            # Показываем панель настроек
            self.settings_panel.setMaximumHeight(200)
            self.settings_animation = QPropertyAnimation(self.settings_panel, b"maximumHeight")
            self.settings_animation.setDuration(300)
            self.settings_animation.setStartValue(0)
            self.settings_animation.setEndValue(200)
            self.settings_animation.setEasingCurve(QEasingCurve.InOutQuad)
            self.settings_animation.start()

            self.settings_visible = True

    def update_timer_duration(self, value):
        """Обновляет длительность таймера в зависимости от значения слайдера"""
        self.WORK_TIME = value * 60
        self.time_value_label.setText(f"{value} минут")

        # Если таймер не запущен и мы в режиме работы, обновляем отображаемое время
        if not self.is_running and self.is_work_mode:
            self.time_left = self.WORK_TIME
            self.timer_label.setText(self.format_time(self.time_left))


# ================= ЗАПУСК =================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = PomodoroTimer()
    window.show()

    sys.exit(app.exec())
