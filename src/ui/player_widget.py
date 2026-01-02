
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve

class PlayerWidget(QWidget):
    """
    Виджет для плеера.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("playerPanel")
        self.setFixedHeight(0)

        # Создаем layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Метка для заголовка
        self.player_label = QLabel("Плеер")
        self.player_label.setObjectName("playerLabel")
        self.player_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.player_label)

        # Флаг видимости плеера
        self.player_visible = False

    def toggle_visibility(self):
        """Переключает видимость панели плеера с анимацией."""
        if self.player_visible:
            # Скрываем панель плеера
            self.player_animation = QPropertyAnimation(self, b"maximumHeight")
            self.player_animation.setDuration(300)
            self.player_animation.setStartValue(200)
            self.player_animation.setEndValue(0)
            self.player_animation.setEasingCurve(QEasingCurve.InOutQuad)
            self.player_animation.start()

            self.player_visible = False
        else:
            # Показываем панель плеера
            self.player_animation = QPropertyAnimation(self, b"maximumHeight")
            self.player_animation.setDuration(300)
            self.player_animation.setStartValue(0)
            self.player_animation.setEndValue(200)
            self.player_animation.setEasingCurve(QEasingCurve.InOutQuad)
            self.player_animation.start()

            self.player_visible = True
