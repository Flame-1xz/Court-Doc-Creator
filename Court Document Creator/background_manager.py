import json
import flet as ft

# Путь к файлу для хранения настроек
SETTINGS_FILE = "settings.json"

# Функция для загрузки настроек
def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"background_image": ""}  # Значение по умолчанию

# Функция для сохранения настроек
def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

# Функция для изменения фона с использованием Flet FilePicker
def change_background(BackGround, page,e: ft.FilePickerResultEvent):
    if e.files:
        file_path = e.files[0].path
        # Сохраняем путь к изображению
        settings = load_settings()
        settings["background_image"] = file_path
        save_settings(settings)

        # Устанавливаем новый фон
        BackGround.content.src = file_path
        BackGround.update()
        page.update()

# Функция для загрузки сохраненного фона при запуске
def initialize_background():
    settings = load_settings()
    background_image_path = settings.get("background_image", "")
    return ft.Container(
        ft.Image(
            src=background_image_path or r'C:\Python Projects\WordCreator\Court Document Creator\assets\WAE8.gif',  # Укажите путь по умолчанию
            fit=ft.ImageFit.CONTAIN,
        ),
        width=2000,  # Ширина фона
    )
# Функция для загрузки фона topbar при старте
def initialize_topbar_background():
    settings = load_settings()
    topbar_background_path = settings.get("topbar_background_image", "")
    topbar_opacity = settings.get("topbar_opacity", 0.3)  # Загружаем значение opacity, по умолчанию 0.3
    return ft.Container(
        width=2000,
        height=250,
        content=ft.Image(
            src=topbar_background_path or r"C:\Python Projects\WordCreator\Court Document Creator\assets\Рельеф.jpg",
            fit=ft.ImageFit.COVER,
            opacity=topbar_opacity,  # Устанавливаем opacity
        ),
        margin=ft.Margin(top=0, left=0, right=0, bottom=0),
        border_radius=ft.border_radius.vertical(bottom=30),
    )

# Функция для смены фона topbar
def change_topbar_background(topbar_background, page, e: ft.FilePickerResultEvent):
    if e.files:
        file_path = e.files[0].path
        settings = load_settings()
        settings["topbar_background_image"] = file_path  # Сохраняем путь к изображению
        save_settings(settings)

        # Устанавливаем новый фон
        topbar_background.content.src = file_path
        topbar_background.update()
        page.update()

# Функция для изменения прозрачности topbar
def change_topbar_opacity(topbar_background, page, new_opacity):
    settings = load_settings()
    settings["topbar_opacity"] = new_opacity  # Сохраняем значение opacity
    save_settings(settings)

    # Применяем новую прозрачность
    topbar_background.content.opacity = new_opacity
    topbar_background.update()
    page.update()