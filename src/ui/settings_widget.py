from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve

class SettingsWidget(QWidget):
    """
    Виджет для настроек таймера.
    """
    # Сигнал для оповещения об изменении значения слайдера
    value_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsPanel")
        self.setFixedHeight(0)

        # Создаем layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Метка для заголовка
        self.settings_label = QLabel("Длительность таймера (минуты):")
        self.settings_label.setObjectName("settingsLabel")
        layout.addWidget(self.settings_label)

        # Слайдер для настройки времени
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setObjectName("timeSlider")
        self.time_slider.setMinimum(1)
        self.time_slider.setMaximum(60)
        self.time_slider.setValue(25)
        self.time_slider.setTickPosition(QSlider.TicksBelow)
        self.time_slider.setTickInterval(5)
        self.time_slider.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.time_slider)

        # Метка для отображения текущего значения
        self.time_value_label = QLabel("25 минут")
        self.time_value_label.setObjectName("timeValueLabel")
        self.time_value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_value_label)

        # Флаг видимости настроек
        self.settings_visible = False

    def _on_value_changed(self, value):
        """Обработчик изменения значения слайдера."""
        self.time_value_label.setText(f"{value} минут")
        self.value_changed.emit(value)

    def toggle_visibility(self):
        """Переключает видимость панели настроек с анимацией."""
        if self.settings_visible:
            # Скрываем панель настроек
            self.settings_animation = QPropertyAnimation(self, b"maximumHeight")
            self.settings_animation.setDuration(300)
            self.settings_animation.setStartValue(200)
            self.settings_animation.setEndValue(0)
            self.settings_animation.setEasingCurve(QEasingCurve.InOutQuad)
            self.settings_animation.start()

            self.settings_visible = False
        else:
            # Показываем панель настроек
            self.settings_animation = QPropertyAnimation(self, b"maximumHeight")
            self.settings_animation.setDuration(300)
            self.settings_animation.setStartValue(0)
            self.settings_animation.setEndValue(200)
            self.settings_animation.setEasingCurve(QEasingCurve.InOutQuad)
            self.settings_animation.start()

            self.settings_visible = True

    def set_value(self, value):
        """Устанавливает значение слайдера."""
        self.time_slider.setValue(value)
        self.time_value_label.setText(f"{value} минут")
