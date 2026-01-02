
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QComboBox, QSlider
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon
try:
    import vlc
    VLC_AVAILABLE = True
except ImportError:
    VLC_AVAILABLE = False

class PlayerWidget(QWidget):
    """
    Виджет для плеера.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("playerPanel")
        self.setFixedHeight(0)

        # Инициализация VLC
        if VLC_AVAILABLE:
            self.instance = vlc.Instance()
            self.player = self.instance.media_player_new()
            self.is_playing = False
        else:
            self.instance = None
            self.player = None
            self.is_playing = False

        # Создаем layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Метка для заголовка
        self.player_label = QLabel("Радио")
        self.player_label.setObjectName("playerLabel")
        self.player_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.player_label)
        
        # Контейнер для кнопок управления
        controls_container = QWidget()
        controls_layout = QHBoxLayout(controls_container)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(15)
        
        # Выбор радиостанции
        self.station_combo = QComboBox()
        self.station_combo.setObjectName("stationCombo")
        self.station_combo.addItems([
            "SomaFM N5MD",
            "Smooth Jazz",
            "Record FM",
            "Europa Plus"
        ])
        self.station_combo.setMinimumWidth(150)
        controls_layout.addWidget(self.station_combo)
        
        # Кнопка воспроизведения/паузы
        self.play_button = QPushButton()
        self.play_button.setObjectName("playButton")
        self.play_button.setFixedSize(50, 50)
        try:
            self.play_button.setIcon(QIcon("play.svg"))
        except:
            self.play_button.setText("▶")
        self.play_button.setIconSize(self.play_button.size() * 0.6)
        self.play_button.clicked.connect(self.toggle_playback)
        controls_layout.addWidget(self.play_button)
        
        # Кнопка остановки
        self.stop_button = QPushButton()
        self.stop_button.setObjectName("stopButton")
        self.stop_button.setFixedSize(50, 50)
        try:
            self.stop_button.setIcon(QIcon("stop.svg"))
        except:
            self.stop_button.setText("■")
        self.stop_button.setIconSize(self.stop_button.size() * 0.6)
        self.stop_button.clicked.connect(self.stop_playback)
        controls_layout.addWidget(self.stop_button)
        
        # Регулятор громкости
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setObjectName("volumeSlider")
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(70)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.valueChanged.connect(self.set_volume)
        controls_layout.addWidget(self.volume_slider)
        
        layout.addWidget(controls_container)
        
        # Метка для отображения статуса
        self.status_label = QLabel("Выберите станцию и нажмите play")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

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
            
    def get_station_url(self, station_name):
        """Возвращает URL радиостанции по её названию."""
        stations = {
            "SomaFM N5MD": "https://ice6.somafm.com/n5md-128-mp3",
            "Smooth Jazz": "http://jazz-wr04.ice.infomaniak.ch/jazz-wr04-128.mp3",
            "Record FM": "https://radiorecord.hostingradio.ru/rr_main96.aacp",
            "Europa Plus": "http://ep256.hostingradio.ru:8052/europaplus256.mp3"
        }
        return stations.get(station_name, "")
        
    def toggle_playback(self):
        """Переключает состояние воспроизведения."""
        if not VLC_AVAILABLE or not self.player:
            self.status_label.setText("Библиотека VLC не установлена")
            return
            
        if self.is_playing:
            # Пауза
            self.player.pause()
            self.is_playing = False
            try:
                self.play_button.setIcon(QIcon("play.svg"))
            except:
                self.play_button.setText("▶")
            self.status_label.setText("Пауза")
        else:
            # Воспроизведение
            station_name = self.station_combo.currentText()
            url = self.get_station_url(station_name)
            
            if not url:
                self.status_label.setText("Станция не найдена")
                return
                
            media = self.instance.media_new(url)
            # Добавляем заголовок User-Agent для решения проблемы с HTTP 403 Forbidden
            media.add_option("http-user-agent=Mozilla/5.0")
            self.player.set_media(media)
            self.player.play()
            self.is_playing = True
            
            try:
                self.play_button.setIcon(QIcon("pause.svg"))
            except:
                self.play_button.setText("⏸")
            self.status_label.setText(f"Воспроизведение: {station_name}")
            
    def stop_playback(self):
        """Останавливает воспроизведение."""
        if not VLC_AVAILABLE or not self.player:
            return
            
        self.player.stop()
        self.is_playing = False
        try:
            self.play_button.setIcon(QIcon("play.svg"))
        except:
            self.play_button.setText("▶")
        self.status_label.setText("Остановлено")
        
    def set_volume(self, value):
        """Устанавливает громкость."""
        if VLC_AVAILABLE and self.player:
            self.player.audio_set_volume(value)
