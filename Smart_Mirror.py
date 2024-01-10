import sys
import os
import requests
import datetime
import pytz
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import QTimer, QDateTime, Qt
from PyQt5.QtGui import QPixmap, QFont

# Constants for API and UI
WEATHER_API_KEY = "d25fa059af0e7d54c12e4b19483d3d58"
WEATHER_URL = f"http://api.openweathermap.org/data/2.5/weather?q=Boca%20Raton,FL,US&units=imperial&appid={WEATHER_API_KEY}"
FORECAST_URL = f"http://api.openweathermap.org/data/2.5/forecast?q=Boca%20Raton,FL,US&units=imperial&appid={WEATHER_API_KEY}"
FONT_PRIMARY = "Arial"
FONT_SIZE_LARGE = 48
FONT_SIZE_MEDIUM = 30
FONT_SIZE_SMALL = 20
BACKGROUND_COLOR = "#282a36"
FONT_COLOR = "#f8f8f2"
ACCENT_COLOR = "#8be9fd"
GREETER_TEXT = "Good day! Here's your update."

# Function to update time and greeting
def update_time_and_greeting(label_time, greeting_label):
    current_time = QDateTime.currentDateTime()
    label_time.setText(current_time.toString("hh:mm:ss a"))

    # Update greeting based on the time of the day
    hour = current_time.time().hour()
    if 6 <= hour < 12:
        greeting = "Good morning!"
    elif 12 <= hour < 18:
        greeting = "Good afternoon!"
    elif 18 <= hour < 22:
        greeting = "Good evening!"
    else:
        greeting = "Good night!"

    greeting_label.setText(greeting)

# Function to update current weather
def update_weather(weather_label, temp_label, humidity_label, wind_label):
    try:
        response = requests.get(WEATHER_URL)
        weather_data = response.json()
        temp = round(weather_data['main']['temp'])
        humidity = weather_data['main']['humidity']
        wind_speed = weather_data['wind']['speed']
        description = weather_data['weather'][0]['main']
        weather_label.setText(f"{description}")
        temp_label.setText(f"Temp: {temp}°F")
        humidity_label.setText(f"Humidity: {humidity}%")
        wind_label.setText(f"Wind: {wind_speed} mph")
    except Exception as e:
        weather_label.setText("Weather update failed")
        temp_label.setText("--")
        humidity_label.setText("--")
        wind_label.setText("--")

# Function to update forecast
def update_forecast(forecast_layout):
    try:
        response = requests.get(FORECAST_URL)
        forecast_data = response.json()
        timezone = pytz.timezone('America/New_York')

        for i in reversed(range(forecast_layout.count())):
            widget_to_remove = forecast_layout.itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.deleteLater()

        current_date = datetime.datetime.now(timezone).date()
        displayed_dates = set()

        for forecast in forecast_data['list']:
            forecast_datetime = datetime.datetime.fromtimestamp(forecast['dt'], timezone)
            forecast_date = forecast_datetime.date()

            if forecast_date > current_date and forecast_date not in displayed_dates:
                date_text = forecast_datetime.strftime("%a")
                temp = round(forecast['main']['temp'])
                icon_code = forecast['weather'][0]['icon']
                icon_path = f"weather_icons/{icon_code}.png"

                if not os.path.isfile(icon_path):
                    continue

                pixmap = QPixmap(icon_path)
                if pixmap.isNull():
                    continue

                day_layout = QHBoxLayout()
                icon_label = QLabel()
                icon_label.setPixmap(pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                day_layout.addWidget(icon_label)

                forecast_label = QLabel(f"{date_text} {temp}°F")
                forecast_label.setStyleSheet(f"font-size: {FONT_SIZE_SMALL}px; color: {FONT_COLOR};")
                day_layout.addWidget(forecast_label)
                forecast_layout.addLayout(day_layout, len(displayed_dates), 0)

                displayed_dates.add(forecast_date)
                if len(displayed_dates) == 5:
                    break

    except Exception as e:
        print("Forecast update failed:", e)

# Main application window setup
def create_main_window():
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setWindowTitle('Smart Mirror')
    win.setGeometry(100, 100, 800, 480)

    # Styling for the sleek, modern theme
    win.setStyleSheet(f"""
        background-color: {BACKGROUND_COLOR};
        color: {FONT_COLOR};
        font-family: {FONT_PRIMARY};
        QLabel {{
            border-radius: 5px;
            padding: 8px;
        }}
    """)

    central_widget = QWidget(win)
    win.setCentralWidget(central_widget)
    main_layout = QVBoxLayout(central_widget)

    # Greeting Display
    greeting_label = QLabel(GREETER_TEXT)
    greeting_label.setFont(QFont(FONT_PRIMARY, FONT_SIZE_MEDIUM))
    greeting_label.setAlignment(Qt.AlignCenter)
    main_layout.addWidget(greeting_label)

    # Time Display
    time_label = QLabel("Time")
    time_label.setFont(QFont(FONT_PRIMARY, FONT_SIZE_LARGE))
    time_label.setAlignment(Qt.AlignCenter)
    main_layout.addWidget(time_label)

    # Weather and Forecast Section
    weather_section = QWidget()
    weather_section_layout = QVBoxLayout(weather_section)
    weather_section_layout.setSpacing(10)
    weather_section_layout.setAlignment(Qt.AlignBottom | Qt.AlignLeft)

    # Compact Current Weather Layout
    weather_info_layout = QHBoxLayout()
    weather_label = QLabel("Weather")
    weather_label.setFont(QFont(FONT_PRIMARY, FONT_SIZE_MEDIUM))
    weather_label.setAlignment(Qt.AlignCenter)
    temp_label = QLabel("Temp")
    temp_label.setFont(QFont(FONT_PRIMARY, FONT_SIZE_MEDIUM))
    temp_label.setAlignment(Qt.AlignCenter)
    humidity_label = QLabel("Humidity")
    humidity_label.setFont(QFont(FONT_PRIMARY, FONT_SIZE_MEDIUM))
    humidity_label.setAlignment(Qt.AlignCenter)
    wind_label = QLabel("Wind")
    wind_label.setFont(QFont(FONT_PRIMARY, FONT_SIZE_MEDIUM))
    wind_label.setAlignment(Qt.AlignCenter)

    weather_info_layout.addWidget(weather_label)
    weather_info_layout.addWidget(temp_label)
    weather_info_layout.addWidget(humidity_label)
    weather_info_layout.addWidget(wind_label)
    weather_section_layout.addLayout(weather_info_layout)

    # Sleek Forecast Grid
    forecast_layout = QGridLayout()
    forecast_layout.setSpacing(10)
    weather_section_layout.addLayout(forecast_layout)
    main_layout.addWidget(weather_section, alignment=Qt.AlignLeft | Qt.AlignBottom)

    # Initial updates and timers
    update_time_and_greeting(time_label, greeting_label)
    update_weather(weather_label, temp_label, humidity_label, wind_label)
    update_forecast(forecast_layout)
    timer = QTimer(win)
    timer.timeout.connect(lambda: update_time_and_greeting(time_label, greeting_label))
    timer.start(1000)  # Update every second for the clock
    forecast_timer = QTimer(win)
    forecast_timer.timeout.connect(lambda: update_forecast(forecast_layout))
    forecast_timer.start(3600000)  # Update weather every hour

    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    create_main_window()
