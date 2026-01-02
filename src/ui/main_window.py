import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSystemTrayIcon, QMenu, QTabBar
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QAction, QFont, QPalette, QColor, QIcon
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from winotify import Notification

from ..core.timer import PomodoroTimer
from ..styles.style import BASE_STYLE, WORK_MODE_BUTTONS, BREAK_MODE_BUTTONS
from .timer_widget import TimerWidget
from .settings_widget import SettingsWidget
from .player_widget import PlayerWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Настройки по умолчанию
        self.WORK_TIME = 25 * 60  # 25 минут
        self.BREAK_TIME = 5 * 60  # 5 минут

        # Инициализация таймера
        self.timer = PomodoroTimer(self.WORK_TIME, self.BREAK_TIME)

        # Подключение сигналов таймера
        self.timer.time_updated.connect(self._on_time_updated)
        self.timer.mode_changed.connect(self._on_mode_changed)
        self.timer.timer_finished.connect(self._on_timer_finished)

        # Состояние UI
        self.settings_visible = False
        self.player_visible = False
        self.old_pos = None

        # Инициализация UI
        self.init_ui()
        self.init_tray_icon()

        # Применяем стили
        self.setStyleSheet(BASE_STYLE + WORK_MODE_BUTTONS)
        self.set_background_color("#FF6B6B")

        # Обновляем начальное состояние
        self._on_time_updated(self.timer.time_left)

    def init_ui(self):
        """Инициализация пользовательского интерфейса."""
        self.setWindowTitle("Pomodoro Timer")
        self.setFixedSize(540, 460)

        # Убираем рамку окна
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Создаем основной контейнер
        central = QWidget(self)
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        # Основной layout
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Верхняя панель с вкладками
        tabs_container = QWidget()
        tabs_container.setObjectName("tabsContainer")
        tabs_layout = QVBoxLayout(tabs_container)
        tabs_layout.setContentsMargins(30, 30, 30, 0)

        # Создаем вкладки
        self.tab_bar = QTabBar()
        self.tab_bar.setObjectName("tabBar")
        self.tab_bar.addTab("Работа")
        self.tab_bar.addTab("Отдых")
        self.tab_bar.setCurrentIndex(0)
        self.tab_bar.setExpanding(False)
        self.tab_bar.setDrawBase(False)
        self.tab_bar.setCursor(Qt.PointingHandCursor)
        self.tab_bar.currentChanged.connect(self._on_tab_changed)

        tabs_layout.addWidget(self.tab_bar)
        main_layout.addWidget(tabs_container)

        # Контейнер для содержимого
        content_container = QWidget()
        content_container.setObjectName("contentContainer")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(30, 30, 30, 30)

        # Виджет таймера
        self.timer_widget = TimerWidget()
        self.timer_widget.start_clicked.connect(self._toggle_timer)
        self.timer_widget.reset_clicked.connect(self._reset_timer)
        self.timer_widget.settings_clicked.connect(self._toggle_settings)
        self.timer_widget.radio_clicked.connect(self._toggle_player)
        content_layout.addWidget(self.timer_widget)

        main_layout.addWidget(content_container)

        # Панель настроек
        self.settings_widget = SettingsWidget()
        self.settings_widget.value_changed.connect(self._on_settings_value_changed)
        main_layout.addWidget(self.settings_widget)
        
        # Панель плеера
        self.player_widget = PlayerWidget()
        main_layout.addWidget(self.player_widget)

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

    def init_tray_icon(self):
        """Инициализация иконки в системном трее."""
        self.tray_icon = QSystemTrayIcon(self)

        # Устанавливаем иконку
        try:
            icon = QIcon("title.png")
            if icon.isNull():
                raise ValueError("Icon file not found or invalid")
            self.tray_icon.setIcon(icon)
            # Также устанавливаем иконку для окна
            self.setWindowIcon(icon)
        except:
            from PySide6.QtGui import QPixmap
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.red)
            self.tray_icon.setIcon(QIcon(pixmap))

        # Создаем контекстное меню
        tray_menu = QMenu()

        show_action = QAction("Показать/Скрыть", self)
        show_action.triggered.connect(self.toggle_window_visibility)
        tray_menu.addAction(show_action)

        quit_action = QAction("Выход", self)
        quit_action.triggered.connect(self.force_quit)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # Обработка двойного клика по иконке
        self.tray_icon.activated.connect(self._on_tray_icon_activated)

    def add_glassmorphism_effect(self, widget, blur_radius=15, opacity=0.5):
        """Добавляет эффект glassmorphism к виджету."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur_radius)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        widget.setGraphicsEffect(shadow)

        widget.setStyleSheet(widget.styleSheet() + f"background-color: rgba(255, 255, 255, {opacity});")

    def add_neon_glow_effect(self, widget, color="#6366F1", blur_radius=25):
        """Добавляет эффект неонового свечения к виджету."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur_radius)

        qcolor = QColor()
        qcolor.setNamedColor(color)
        shadow.setColor(qcolor)

        shadow.setOffset(0, 0)
        widget.setGraphicsEffect(shadow)

    def set_background_color(self, color):
        """Устанавливает цвет фона окна."""
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

    def animate_background_color(self, color):
        """Анимирует изменение цвета фона."""
        start = self.palette()
        end = self.palette()
        end.setColor(QPalette.Window, QColor(color))

        color_animation = QPropertyAnimation(self, b"palette")
        color_animation.setDuration(800)
        color_animation.setEasingCurve(QEasingCurve.InOutQuad)
        color_animation.setStartValue(start)
        color_animation.setEndValue(end)
        color_animation.start()

    def show_notification(self, title, message):
        """Показывает системное уведомление."""
        toast = Notification(
            app_id="Pomodoro Timer",
            title=title,
            msg=message,
            duration="short"
        )
        toast.show()

    def toggle_window_visibility(self):
        """Переключает видимость окна."""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()

    def _on_tray_icon_activated(self, reason):
        """Обработка активации иконки в системном трее."""
        if reason == QSystemTrayIcon.DoubleClick:
            self.toggle_window_visibility()

    def minimize_to_tray(self):
        """Сворачивает окно в системный трей."""
        self.hide()

    def restore_from_tray(self):
        """Восстанавливает окно из системного трея."""
        self.show()
        self.raise_()
        self.activateWindow()

    def _toggle_timer(self):
        """Переключает состояние таймера."""
        if self.timer.is_running:
            self.timer.pause()
            self.timer_widget.set_start_button_text("Старт")
            try:
                self.timer_widget.set_start_button_icon("play_icon.png")
            except:
                # Используем стандартную иконку, если файл не найден
                self.timer_widget.set_start_button_icon(None)
        else:
            self.timer.start()
            self.timer_widget.set_start_button_text("Пауза")
            try:
                self.timer_widget.set_start_button_icon("pause_icon.png")
            except:
                # Используем стандартную иконку, если файл не найден
                self.timer_widget.set_start_button_icon(None)

            if self.timer.is_work_mode:
                self.show_notification("Таймер запущен", "Время работать 💪")
            else:
                self.show_notification("Отдых", "Начался отдых ☕")

            QTimer.singleShot(300, self.minimize_to_tray)

    def _reset_timer(self):
        """Сбрасывает таймер."""
        self.timer.reset()
        self.timer_widget.set_start_button_text("Старт")
        try:
            self.timer_widget.set_start_button_icon("play_icon.png")
        except:
            # Используем стандартную иконку, если файл не найден
            self.timer_widget.set_start_button_icon(None)

        # Устанавливаем правильную вкладку
        if self.timer.is_work_mode:
            self.tab_bar.setCurrentIndex(0)
        else:
            self.tab_bar.setCurrentIndex(1)

    def _toggle_settings(self):
        """Переключает видимость панели настроек."""
        self.settings_widget.toggle_visibility()
        self.settings_visible = not self.settings_visible
        
    def _toggle_player(self):
        """Переключает видимость панели плеера."""
        self.player_widget.toggle_visibility()
        self.player_visible = not self.player_visible

    def _on_settings_value_changed(self, value):
        """Обработчик изменения значения в настройках."""
        if self.timer.is_work_mode:
            self.timer.set_work_time(value)
        else:
            self.timer.set_break_time(value)

    def _on_time_updated(self, seconds):
        """Обработчик обновления времени."""
        self.timer_widget.update_time(self.timer.format_time(seconds))

    def _on_mode_changed(self, is_work_mode):
        """Обработчик изменения режима."""
        if is_work_mode:
            self.tab_bar.setCurrentIndex(0)
            self.setStyleSheet(BASE_STYLE + WORK_MODE_BUTTONS)
            self.add_neon_glow_effect(self.centralWidget(), "#FF6B6B", 25)
        else:
            self.tab_bar.setCurrentIndex(1)
            self.setStyleSheet(BASE_STYLE + BREAK_MODE_BUTTONS)
            self.add_neon_glow_effect(self.centralWidget(), "#4ECDC4", 25)

    def _on_timer_finished(self):
        """Обработчик завершения таймера."""
        self.restore_from_tray()
        self.timer_widget.set_start_button_text("Старт")
        try:
            self.timer_widget.set_start_button_icon("play_icon.png")
        except:
            # Используем стандартную иконку, если файл не найден
            self.timer_widget.set_start_button_icon(None)

    def _on_tab_changed(self, index):
        """Обработчик переключения вкладок."""
        if index == 0 and not self.timer.is_work_mode:
            self.timer.switch_mode()
        elif index == 1 and self.timer.is_work_mode:
            self.timer.switch_mode()

    def closeEvent(self, event):
        """Обработка события закрытия окна."""
        event.ignore()
        self.hide()

    def force_quit(self):
        """Принудительное завершение приложения."""
        QApplication.quit()

    def mousePressEvent(self, event):
        """Обработка нажатия кнопки мыши."""
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        """Обработка отпускания кнопки мыши."""
        if event.button() == Qt.LeftButton:
            self.old_pos = None

    def mouseReleaseEvent(self, event):
        """Обработка отпускания кнопки мыши."""
        if event.button() == Qt.LeftButton:
            self.old_pos = None

    def mouseMoveEvent(self, event):
        """Обработка перемещения мыши для перетаскивания окна."""
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()
