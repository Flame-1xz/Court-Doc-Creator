import json
import flet as ft

# Путь к файлу для хранения настроек
SETTINGS_FILE = "color_settings.json"

# Функция для загрузки настроек
def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "top_bar_color": ft.colors.WHITE,
            "my_border_color": ft.colors.BLACK,
            "my_text_color": ft.colors.WHITE,
            "attendance_options_color": ft.colors.BLACK,
            "radio_button_color": ft.colors.BLACK,
            "top_bar_switch_state": True
        }  # Значения по умолчанию

# Функция для сохранения настроек
def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

# Функция для применения сохраненных настроек при запуске приложения
def apply_settings():
    settings = load_settings()
    # Устанавливаем состояние переключателя из настроек
    switch_state = settings.get("top_bar_switch_state", True)
    return settings, switch_state  # Возвращаем и настройки, и состояние переключателя

# Функция для обновления настроек
# Она должна быть интегрирована в вашу функцию update_color
def update_settings(variable_name, new_value):
    settings = load_settings()
    if variable_name in settings:
        settings[variable_name] = new_value
        save_settings(settings)
