# Стили приложения Pomodoro Timer

BASE_STYLE = """
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
        color: rgba(255, 255, 255, 0.9);
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
        background-color: rgba(255, 255, 255, 0.35);
        border-radius: 16px;
        margin: 10px 30px 20px 30px;
        border: 1px solid rgba(255, 255, 255, 0.4);
    }
    #timerLabel {
        font-family: "SF Pro Display", "Segoe UI", Arial, sans-serif;
        font-size: 72px;
        font-weight: 500;
        color: white;
        margin: 10px 0 30px 0;
        letter-spacing: -2px;
    }
    #settingsPanel {
        background-color: rgba(255, 255, 255, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.4);
        margin: 10px 0;
    }
    #settingsLabel {
        font-family: "SF Pro Display", "Segoe UI", Arial, sans-serif;
        font-size: 14px;
        font-weight: 600;
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
        font-weight: 600;
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
        color: rgba(255, 255, 255, 0.9);
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
        color: rgba(255, 255, 255, 0.9);
        background-color: transparent;
        border: none;
        border-radius: 15px;
        margin-right: 5px;
    }
    #minimizeButton:hover {
        color: white;
        background-color: rgba(255, 255, 255, 0.2);
    }
    #minimizeButton:pressed {
        background-color: rgba(255, 255, 255, 0.3);
    }
"""

WORK_MODE_BUTTONS = """
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
        background-color: rgba(78, 205, 196, 0.8);
        border: 1px solid rgba(78, 205, 196, 0.5);
        border-radius: 30px;
        color: white;
    }
    #resetButton:hover {
        background-color: rgba(78, 205, 196, 0.9);
        border: 1px solid rgba(78, 205, 196, 0.7);
    }
    #resetButton:pressed {
        background-color: rgba(78, 205, 196, 0.7);
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
"""

BREAK_MODE_BUTTONS = """
    #startButton {
        font-family: "SF Pro Display", "Segoe UI", Arial, sans-serif;
        font-size: 16px;
        font-weight: 600;
        color: white;
        background-color: rgba(78, 205, 196, 0.8);
        border: 1px solid rgba(78, 205, 196, 0.5);
        border-radius: 30px;
        padding: 0;
    }
    #startButton:hover {
        background-color: rgba(78, 205, 196, 0.9);
        border: 1px solid rgba(78, 205, 196, 0.7);
    }
    #startButton:pressed {
        background-color: rgba(78, 205, 196, 0.7);
    }
    #resetButton {
        background-color: rgba(255, 107, 107, 0.8);
        border: 1px solid rgba(255, 107, 107, 0.5);
        border-radius: 30px;
        color: white;
    }
    #resetButton:hover {
        background-color: rgba(255, 107, 107, 0.9);
        border: 1px solid rgba(255, 107, 107, 0.7);
    }
    #resetButton:pressed {
        background-color: rgba(255, 107, 107, 0.7);
    }
    #settingsButton {
        font-family: "SF Pro Display", "Segoe UI", Arial, sans-serif;
        font-size: 18px;
        font-weight: 600;
        color: white;
        background-color: rgba(255, 107, 107, 0.8);
        border: 1px solid rgba(255, 107, 107, 0.5);
        border-radius: 30px;
    }
    #settingsButton:hover {
        background-color: rgba(255, 107, 107, 0.9);
        border: 1px solid rgba(255, 107, 107, 0.7);
    }
    #settingsButton:pressed {
        background-color: rgba(255, 107, 107, 0.7);
    }
"""
