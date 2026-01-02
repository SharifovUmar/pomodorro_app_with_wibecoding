from PySide6.QtCore import QTimer, Signal, QObject

class PomodoroTimer(QObject):
    """
    Класс, реализующий логику таймера помодоро.
    """
    # Сигналы для оповещения об изменениях состояния
    time_updated = Signal(int)  # Обновление оставшегося времени
    mode_changed = Signal(bool)  # Изменение режима (True - работа, False - отдых)
    timer_finished = Signal()  # Завершение таймера

    def __init__(self, work_time=25 * 60, break_time=5 * 60):
        super().__init__()
        self.WORK_TIME = work_time  # Время работы в секундах
        self.BREAK_TIME = break_time  # Время отдыха в секундах

        self.is_work_mode = True  # Текущий режим
        self.is_running = False  # Состояние таймера
        self.time_left = self.WORK_TIME  # Оставшееся время

        # Таймер для обратного отсчета
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_timer)

    def start(self):
        """Запускает таймер."""
        if not self.is_running:
            self.timer.start(1000)  # Обновление каждую секунду
            self.is_running = True

    def pause(self):
        """Приостанавливает таймер."""
        if self.is_running:
            self.timer.stop()
            self.is_running = False

    def reset(self):
        """Сбрасывает таймер в начальное состояние."""
        self.timer.stop()
        self.is_running = False

        if self.is_work_mode:
            self.time_left = self.WORK_TIME
        else:
            self.time_left = self.BREAK_TIME

        self.time_updated.emit(self.time_left)

    def switch_mode(self):
        """Переключает режим работы/отдых."""
        self.timer.stop()
        self.is_running = False

        # Переключаем режим
        self.is_work_mode = not self.is_work_mode

        # Устанавливаем время для нового режима
        if self.is_work_mode:
            self.time_left = self.WORK_TIME
        else:
            self.time_left = self.BREAK_TIME

        # Оповещаем об изменении режима
        self.mode_changed.emit(self.is_work_mode)
        self.time_updated.emit(self.time_left)

    def set_work_time(self, minutes):
        """Устанавливает время работы в минутах."""
        self.WORK_TIME = minutes * 60
        if self.is_work_mode:
            self.time_left = self.WORK_TIME
            self.time_updated.emit(self.time_left)

    def set_break_time(self, minutes):
        """Устанавливает время отдыха в минутах."""
        self.BREAK_TIME = minutes * 60
        if not self.is_work_mode:
            self.time_left = self.BREAK_TIME
            self.time_updated.emit(self.time_left)

    def _update_timer(self):
        """Внутренний метод для обновления таймера."""
        self.time_left -= 1
        self.time_updated.emit(self.time_left)

        if self.time_left <= 0:
            self.timer_finished.emit()
            self.switch_mode()

    def format_time(self, seconds):
        """Форматирует секунды в строку MM:SS."""
        m, s = divmod(seconds, 60)
        return f"{m:02d}:{s:02d}"
