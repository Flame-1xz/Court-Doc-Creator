import os
import re
import flet as ft
from flet import *
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

from document_creation import create_document, create_extramural_document, create_special_document
from templates import load_templates, load_template_text, generate_optional_entries
from template_creation import create_template_from_document
from background_manager import initialize_background, change_background, initialize_topbar_background, change_topbar_background, change_topbar_opacity
from reset_button import add_reset_button
from colors_settings import load_settings, save_settings, apply_settings, update_settings


#Цвет топбара
top_bar_color = ft.colors.WHITE
#Цвет border
my_border_color = ft.colors.BLACK
#Цвет текста
my_text_color = ft.colors.WHITE
#Цвет проверки явки сторон
attendance_options_color = ft.colors.BLACK
radio_button_color = ft.colors.BLACK


def root(page: ft.Page):  # Принимаем объект page как аргумент
    page.title = "Создание решения суда"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.icon = r"C:\Python Projects\WordCreator\Court Document Creator\assets\CourtDesignerIconPNG.png"  # Иконка приложения
    page.padding=0

    # Фон для topbar
    topbar_background = initialize_topbar_background()

    # Задний фон
    BackGround = initialize_background()

    # Настройки цветов
    user_color_settings, switch_state = apply_settings()

    # Применение настроек к глобальным переменным
    top_bar_color = user_color_settings["top_bar_color"]
    my_border_color = user_color_settings["my_border_color"]
    my_text_color = user_color_settings["my_text_color"]
    attendance_options_color = user_color_settings["attendance_options_color"]
    radio_button_color = user_color_settings["radio_button_color"]

    #Стиль Шрифта для Label
    label_text_field_style = ft.TextStyle(color=my_text_color,font_family="Flame",size=20)

    # Стиль Шрифта в поле для ввода
    text_field_style = ft.TextStyle(color=my_text_color, font_family="Flame", size=16)

    #Стиль радиокнопок
    radio_style = ft.TextStyle(color=attendance_options_color,font_family="Flame",size=16)

    # Список полей с их метками
    fields = [
        ("decision_number", "Номер дела"),
        ("uid", "УИД дела"),
        ("decision_date", "Дата решения"),
        ("plaintiff", "Истец"),
        ("defendant", "Ответчик"),
        ("third_faces", "Третьи лица"),
        ("applicant", "Заявитель"),
        ("interested_persons", "Заинтересованные лица"),
        ("crux", "Суть дела"),
    ]

    # Шаблон параметров для полей ввода
    common_params = {
        "label_style": label_text_field_style,
        "text_style": label_text_field_style,
        "border_radius": 18,
        "border_color": my_border_color,
        "border_width": 2,
        "focused_border_color": my_border_color,
        "cursor_color": ft.colors.BLACK,
    }

    # Генерация словаря полей ввода
    entries = {}
    entries_containers = {}
    for field_name, label in fields:
        is_visible = field_name not in ["applicant", "interested_persons"]  # По умолчанию скрываем нужные поля

        text_field = ft.TextField(label=label, **common_params, visible=is_visible)

        container = ft.Container(
            content=text_field,
            blur=ft.Blur(10, 12, ft.BlurTileMode.MIRROR),
            border_radius=18,
            padding=5,
            visible=is_visible  # Контейнер тоже изначально скрываем
        )

        entries[field_name] = text_field
        entries_containers[field_name] = container

    #Функция для выбора вида судопроизводства
    def update_fields_visibility(e):
        special_case = case_type_selector.value  # True -> особое производство, False -> обычное

        # Скрытие/показ полей сторон
        for field_name in ["plaintiff", "defendant", "third_faces"]:
            if field_name in entries:
                entries[field_name].visible = not special_case
                entries_containers[field_name].visible = not special_case

        for field_name in ["applicant", "interested_persons"]:
            if field_name in entries:
                entries[field_name].visible = special_case
                entries_containers[field_name].visible = special_case

        # Обновление видимости контейнеров явки сторон
        for container in tabs_content.controls[0].content.tabs[0].content.controls[1].controls:
            if isinstance(container, ft.Container):
                if container.key == "plaintiff_attendance_container" or container.key == "defendant_attendance_container" or container.key == "third_party_attendance_container":
                    container.visible = not special_case
                elif container.key == "applicant_attendance_container" or container.key == "interested_persons_attendance_container":
                    container.visible = special_case

        # Также обновляем видимость самих радиокнопок
        applicant_attendance.visible = special_case
        interested_persons_attendance.visible = special_case

        # Скрытие кнопок создания документов
        create_button.visible = not special_case
        create_extramural_button.visible = not special_case
        create_special_button.visible = special_case

        page.update()

    #Переключатель вида судопроизводства
    case_type_selector = ft.Switch(
        label="Особое производство",
        label_style=label_text_field_style,
        value=False,
        active_color=radio_button_color,
        on_change=update_fields_visibility,
    )

    # Описательная часть
    descriptive_text = ft.TextField(
        label="Описательная часть",
        multiline=True,
        min_lines=4,
        max_lines=10,
        label_style = label_text_field_style, border_radius = 18, border_color = my_border_color, border_width = 2, focused_border_color = my_border_color, cursor_color=ft.colors.BLACK,
        text_style=text_field_style
    )

    # Просительная часть
    pleading_text = ft.TextField(
        label="Просительная часть",
        multiline=True,
        min_lines=4,
        max_lines=10,
        label_style=label_text_field_style, border_radius=18, border_color=my_border_color,border_width=2, focused_border_color=my_border_color, cursor_color=ft.colors.BLACK,
        text_style=text_field_style
    )

    # Явка сторон
    attendance_options = ["Да", "Нет"]
    plaintiff_attendance = ft.RadioGroup(
        value="Да",
        content=ft.Row(
            controls=[ft.Radio(value=o, label=o,label_style=radio_style,active_color=radio_button_color) for o in attendance_options],
            spacing=10,
        ),
    )

    defendant_attendance = ft.RadioGroup(
        value="Да",
        content=ft.Row(
            controls=[ft.Radio(value=o, label=o,label_style=radio_style,active_color=radio_button_color) for o in attendance_options],
            spacing=10,
        ),
    )

    third_party_attendance = ft.RadioGroup(
        value="Да",
        content=ft.Row(
            controls=[ft.Radio(value=o, label=o,label_style=radio_style,active_color=radio_button_color) for o in attendance_options],
            spacing=10,
        ),
    )

    applicant_attendance = ft.RadioGroup(
        value="Да",
        content=ft.Row(
            controls=[ft.Radio(value=o, label=o, label_style=radio_style, active_color=radio_button_color) for o in attendance_options],
            spacing=10,
        ),
    )

    interested_persons_attendance = ft.RadioGroup(
        value="Да",
        content=ft.Row(
            controls=[ft.Radio(value=o, label=o, label_style=radio_style, active_color=radio_button_color) for o in attendance_options],
            spacing=10,
        ),
    )

    # Словарь для хранения ссылок на созданные опциональные поля
    optional_entries_fields = {}

    # Функция для выбора шаблона и динамического создания опциональных полей
    def on_template_select(e):
        selected_template = template_selector.value.strip()  # Убираем лишние пробелы
        selected_template = selected_template.replace('(', '').replace(')', '')

        try:
            template_text = load_template_text(selected_template)

            used_optional_entries = generate_optional_entries(template_text, entries)

            # Очистить контейнер для отображения новых полей
            optional_entries_tab.controls.clear()

            # Добавить динамически найденные опциональные поля и сохранить ссылки на них
            for label, field in used_optional_entries.items():
                # Создаем TextField с нужным стилем
                text_field = ft.TextField(
                    label=label,
                    label_style=label_text_field_style,
                    border_radius=18,
                    border_color=my_border_color,
                    border_width=2,
                    focused_border_color=my_border_color,
                    cursor_color=ft.colors.BLACK,
                    text_style=text_field_style,
                )

                # Оборачиваем TextField в Container
                container = ft.Container(
                    content=text_field,
                    blur=Blur(10, 12, BlurTileMode.MIRROR),
                    border_radius=18,
                    padding=5
                )

                # Добавляем контейнер с TextField в таблицу
                optional_entries_tab.controls.append(container)
                optional_entries_fields[label] = container  # Сохраняем ссылку на контейнер

            page.update()  # Обновляем интерфейс после добавления новых полей

        except FileNotFoundError as ex:
            page.snack_bar = ft.SnackBar(ft.Text(str(ex)))
            page.snack_bar.open = True
            page.update()

    # Загрузка шаблонов
    templates = load_templates()
    template_selector = ft.Dropdown(
        label="Выберите шаблон",
        label_style=label_text_field_style,
        text_style=label_text_field_style,
        border_radius=18,
        color=ft.colors.BLACK,
        border_color=my_border_color,
        border_width=2,
        focused_border_color=my_border_color,
        options=[ft.dropdown.Option(t) for t in templates] if templates else [],
        on_change=on_template_select,
        padding=5
    )

    # Обработчик для создания документа
    def on_create_document(e):
        if not template_selector.value:
            page.snack_bar = ft.SnackBar(ft.Text("Пожалуйста, выберите шаблон!"))
        else:
            try:
                template_text = load_template_text(template_selector.value.strip())

                used_optional_entries = generate_optional_entries(template_text, entries)
                page.update()

                optional_values = {}
                for label, container in optional_entries_fields.items():
                    # Проверяем, содержит ли контейнер TextField
                    if isinstance(container.content, ft.TextField):
                        # Извлекаем значение из TextField внутри контейнера
                        optional_values[label] = container.content.value or ""
                    else:
                        optional_values[label] = ""  # Если нет TextField, используем пустое значение


                # Передаем данные в функцию создания документа
                create_document(
                    entries,
                    descriptive_text,
                    pleading_text,
                    optional_values,
                    plaintiff_attendance.value,
                    defendant_attendance.value,
                    third_party_attendance.value,
                    template_selector.value,
                    page,
                )

                page.snack_bar = ft.SnackBar(ft.Text("Документ создан успешно!"))
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Произошла ошибка: {ex}"))

        page.snack_bar.open = True
        page.update()

    # Функция для создания заочного решения суда
    def on_create_extramural_document(e):
        if not template_selector.value:
            page.snack_bar = ft.SnackBar(ft.Text("Пожалуйста, выберите шаблон!"))
        else:
            try:
                template_text = load_template_text(template_selector.value.strip())

                used_optional_entries = generate_optional_entries(template_text, entries)
                page.update()

                optional_values = {}
                for label, container in optional_entries_fields.items():
                    # Проверяем, содержит ли контейнер TextField
                    if isinstance(container.content, ft.TextField):
                        # Извлекаем значение из TextField внутри контейнера
                        optional_values[label] = container.content.value or ""
                    else:
                        optional_values[label] = ""  # Если нет TextField, используем пустое значение

                # Передаем данные в функцию создания документа
                create_extramural_document(
                    entries,
                    descriptive_text,
                    pleading_text,
                    optional_values,
                    plaintiff_attendance.value,
                    defendant_attendance.value,
                    third_party_attendance.value,
                    template_selector.value,
                    page,
                )

                page.snack_bar = ft.SnackBar(ft.Text("Документ создан успешно!"))
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Произошла ошибка: {ex}"))

        page.snack_bar.open = True
        page.update()

    #Кнопка создания решения суда
    create_button = ft.ElevatedButton(
        text="Создать решение суда",
        on_click=on_create_document,
        icon=ft.icons.CREATE,  # Иконка для кнопки
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),  # Скругленные углы
            color=ft.colors.BLACK, # Цвет фона
            text_style=ft.TextStyle(
                font_family="Flame",  # Устанавливаем шрифт
                color=ft.colors.WHITE  # Цвет текста
            )
        ),
    )

    # Функция для создания решения суда в особом производстве
    def on_create_special_document(e):
        if not template_selector.value:
            page.snack_bar = ft.SnackBar(ft.Text("Пожалуйста, выберите шаблон!"))
        else:
            try:
                template_text = load_template_text(template_selector.value.strip())

                used_optional_entries = generate_optional_entries(template_text, entries)
                page.update()

                optional_values = {}
                for label, container in optional_entries_fields.items():
                    # Проверяем, содержит ли контейнер TextField
                    if isinstance(container.content, ft.TextField):
                        # Извлекаем значение из TextField внутри контейнера
                        optional_values[label] = container.content.value or ""
                    else:
                        optional_values[label] = ""  # Если нет TextField, используем пустое значение


                # Передаем данные в функцию создания документа
                create_special_document(
                    entries,
                    descriptive_text,
                    pleading_text,
                    optional_values,
                    applicant_attendance.value,
                    interested_persons_attendance.value,
                    template_selector.value,
                    page,
                )

                page.snack_bar = ft.SnackBar(ft.Text("Документ создан успешно!"))
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Произошла ошибка: {ex}"))

        page.snack_bar.open = True
        page.update()

    #Кнопка создания решения в особом производстве
    create_special_button = ft.ElevatedButton(
        text="Создать решение суда в особом производстве",
        on_click=on_create_special_document,
        icon=ft.Icons.CREATE_OUTLINED,  # Иконка для кнопки
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            color=ft.colors.BLACK,
            text_style=ft.TextStyle(
                font_family="Flame",
                color=ft.colors.WHITE)
        )
    )

    # Кнопка создания заочного решения суда
    create_extramural_button = ft.ElevatedButton(
        text="Создать заочное решение суда",
        on_click=on_create_extramural_document,
        icon=ft.Icons.BORDER_COLOR,  # Иконка для кнопки
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),  # Скругленные углы
            color=ft.colors.BLACK,  # Цвет фона
            text_style=ft.TextStyle(
                font_family="Flame",  # Устанавливаем шрифт
                color=ft.colors.WHITE  # Цвет текста
            )
        ),
    )


    # Вкладка для создания шаблона
    def on_analyze_document(e):
        if not document_text.value:
            page.snack_bar = ft.SnackBar(ft.Text("Пожалуйста, выберите текст документа!"))
        else:
            processed_text = create_template_from_document(document_text.value)
            page.snack_bar = ft.SnackBar(ft.Text("Документ успешно преобразован в шаблон!"))

            # Сохранение шаблона в формате .docx в папку Templates of motivational parts
            save_directory = "Templates of motivational parts"
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)

            file_name = f"{entries['decision_number'].value}_шаблон.docx"
            file_path = os.path.join(save_directory, file_name)

            # Создание нового документа Word
            doc = Document()
            # Добавляем абзац с обработанным текстом
            paragraph = doc.add_paragraph(processed_text)

            # Настройка шрифта
            run = paragraph.runs[0]  # Получаем первый (единственный) run
            run.font.name = 'Times New Roman'
            run.font.size = Pt(14)  # Размер шрифта 14

            # Выравнивание по ширине
            paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

            # Установка междустрочного интервала 1.0 и удаление интервала после абзаца
            paragraph.paragraph_format.line_spacing = 1.0  # Междустрочный интервал
            paragraph.paragraph_format.space_after = 0  # Удаление интервала после абзаца

            # Установка отступа первой строки 1.25 см
            paragraph.paragraph_format.first_line_indent = Pt(1.25 * 28.35)  # Переводим см в пункты (1 см = 28.35 pt)

            # Сохраняем документ
            doc.save(file_path)

            # Уведомление о сохранении шаблона
            page.snack_bar = ft.SnackBar(ft.Text(f"Шаблон сохранен как {file_name}."))
            page.snack_bar.open = True
            page.update()

    document_text = ft.TextField(
        label="Введите текст документа",
        multiline=True,
        min_lines=10,
        expand=True,
    )

    analyze_button = ft.ElevatedButton(
        text="Преобразовать в шаблон",
        on_click=on_analyze_document,
        bgcolor=ft.colors.GREEN,
        color=ft.colors.WHITE,
    )

    # Вкладка для опциональных сведений
    optional_entries_tab = ft.Column(controls=[], scroll=ft.ScrollMode.ALWAYS,height=600)

    #Функция для изменения цвета
    def update_color(variable_name, new_color,switch_value=None):
        global top_bar_color, my_border_color, my_text_color, attendance_options_color, radio_button_color

        if variable_name == "top_bar_color":
            top_bar_color = new_color
            update_settings("top_bar_color", new_color)
            if switch_value is not None:
                update_settings("top_bar_switch_state", switch_value)
            # Находим вкладки внутри tabs_content и обновляем их цвет
            for control in tabs_content.controls:
                if isinstance(control.content, ft.Tabs):
                    control.content.label_color = top_bar_color
                    control.content.label_text_style = ft.TextStyle(color=top_bar_color, font_family="Flame")
                    control.content.indicator_color = top_bar_color
                    control.content.update()

        elif variable_name == "my_border_color":
            my_border_color = new_color
            update_settings("my_border_color", new_color)
            # Обновление рамок
            for entry in entries.values():
                entry.border_color = my_border_color
                entry.focused_border_color = my_border_color
                entry.update()

            for text_field in [descriptive_text, pleading_text]:
                text_field.border_color = my_border_color
                text_field.focused_border_color = my_border_color
                text_field.update()

            # Если в on_template_select создаются дополнительные поля, то их рамки тоже можно обновить
            for container in optional_entries_fields.values():
                if isinstance(container.content, ft.TextField):
                    container.content.border_color = my_border_color
                    container.content.focused_border_color = my_border_color
                    container.content.update()

        elif variable_name == "my_text_color":
            my_text_color = new_color
            update_settings("my_text_color", new_color)
            # Обновление текста
            for entry in entries.values():
                entry.text_style.color = my_text_color
                entry.label_style.color = my_text_color
                entry.update()

            for text_field in [descriptive_text, pleading_text]:
                text_field.text_style.color = my_text_color
                text_field.label_style.color = my_text_color
                text_field.update()

        elif variable_name == "attendance_options_color":
            attendance_options_color = new_color
            update_settings("attendance_options_color", new_color)
            # Обновление текста явки сторон
            for attendance in [plaintiff_attendance, defendant_attendance, third_party_attendance, applicant_attendance, interested_persons_attendance]:
                for radio in attendance.content.controls:
                    radio.label_style.color = attendance_options_color
                    radio.update()

        elif variable_name == "radio_button_color":
            radio_button_color = new_color
            update_settings("radio_button_color", new_color)
            # Обновление цвета кнопок
            for attendance in [plaintiff_attendance, defendant_attendance, third_party_attendance, applicant_attendance, interested_persons_attendance]:
                for radio in attendance.content.controls:
                    radio.active_color = radio_button_color
                    radio.update()

        # Обновление всей страницы
        page.update()

    # Создаем слайдер для изменения прозрачности
    opacity_slider = ft.Slider(
        min=0.0,
        max=1.0,
        divisions=10,  # Десятые доли
        value=load_settings().get("topbar_opacity", 0.3),  # Загружаем сохраненное значение
        label="{value}",
        on_change=lambda e: change_topbar_opacity(topbar_background, page, e.control.value),
    )

    # Функция для открытия меню настроек
    def open_settings_menu(e):
        # Создаем объект FilePicker
        file_picker = ft.FilePicker(on_result=lambda e: change_background(BackGround, page, e))

        # Добавляем FilePicker в overlay
        page.overlay.append(file_picker)
        page.update()  # Обновляем страницу
        file_picker_topbar = ft.FilePicker(on_result=lambda e: change_topbar_background(topbar_background, page, e))
        page.overlay.append(file_picker_topbar)
        # Создаем окно настроек
        settings_dialog = ft.AlertDialog(
            title=ft.Text("Настройки", font_family='Flame'),  # Заголовок
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text("Цвет топбара", font_family='Flame'),
                            ft.Switch(
                                value=(top_bar_color == ft.colors.WHITE),
                                on_change=lambda e: update_color(
                                    "top_bar_color", ft.colors.WHITE if e.control.value else ft.colors.BLACK, switch_value=e.control.value
                                ),
                            ),
                        ]
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("Цвет рамок", font_family='Flame'),
                            ft.Switch(
                                value=(my_border_color == ft.colors.WHITE),
                                on_change=lambda e: update_color(
                                    "my_border_color", ft.colors.WHITE if e.control.value else ft.colors.BLACK
                                ),
                            ),
                        ]
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("Цвет текста", font_family='Flame'),
                            ft.Switch(
                                value=(my_text_color == ft.colors.WHITE),
                                on_change=lambda e: update_color(
                                    "my_text_color", ft.colors.WHITE if e.control.value else ft.colors.BLACK
                                ),
                            ),
                        ]
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("Цвет проверки явки сторон", font_family='Flame'),
                            ft.Switch(
                                value=(attendance_options_color == ft.colors.WHITE),
                                on_change=lambda e: update_color(
                                    "attendance_options_color", ft.colors.WHITE if e.control.value else ft.colors.BLACK
                                ),
                            ),
                        ]
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("Цвет радио-кнопок", font_family='Flame'),
                            ft.Switch(
                                value=(radio_button_color == ft.colors.WHITE),
                                on_change=lambda e: update_color(
                                    "radio_button_color", ft.colors.WHITE if e.control.value else ft.colors.BLACK
                                ),
                            ),
                        ]
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("Сменить фон", font_family='Flame'),
                            ft.ElevatedButton(
                                text="Выбрать изображение",
                                on_click=lambda _: file_picker.pick_files(allowed_extensions=["png", "jpg", "jpeg", "gif"]),
                                icon=ft.icons.IMAGE,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                    color=ft.colors.BLACK,
                                    text_style=ft.TextStyle(color=ft.colors.WHITE),
                                ),
                            ),
                        ]
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("Фон верхней панели", font_family='Flame'),
                            ft.ElevatedButton(
                                text="Выбрать изображение",
                                on_click=lambda _: file_picker_topbar.pick_files(
                                    allowed_extensions=["png", "jpg", "jpeg", "gif"]
                                ),
                                icon=ft.icons.IMAGE,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                    color=ft.colors.BLACK,
                                    text_style=ft.TextStyle(color=ft.colors.WHITE),
                                ),
                            ),
                        ]
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("Прозрачность фона верхней панели", font_family='Flame'),
                            opacity_slider,
                        ]
                    )
                ]
            ),
            actions=[
                ft.TextButton(
                    "Закрыть",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        color=ft.colors.BLACK,
                        text_style=ft.TextStyle(
                            font_family="Flame",
                            color=ft.colors.WHITE,
                        ),
                    ),
                    on_click=lambda _: close_settings_menu(),
                )
            ],
        )

        def close_settings_menu():
            settings_dialog.open = False
            page.update()

        # Открываем меню настроек
        page.dialog = settings_dialog
        settings_dialog.open = True
        page.update()
        tabs_content.update()

    reset_button = add_reset_button(page, entries, descriptive_text, pleading_text, optional_entries_fields,
                                 [plaintiff_attendance, defendant_attendance, third_party_attendance])
    #Задний фон для верхнего меню
    topbar = ft.Stack(
        width=2000,
        controls=[
            # Контейнер с фоновым изображением
            topbar_background,
            # Контейнер с содержимым
            ft.Container(
                border_radius=ft.border_radius.vertical(bottom=30),
                height=250,
                margin=ft.Margin(top=0, left=0, right=0, bottom=0),  # Отступы для этого контейнера
                content=ft.Row(
                    controls=[
                        ft.Image(
                            src=r"C:\Python Projects\WordCreator\Court Document Creator\assets\CourtDesignerIconPNG.png",
                            width=200, height=200),
                        ft.Text("Создание решения суда", size=36, weight=ft.FontWeight.BOLD, color="black",
                                style=ft.TextStyle(color=ft.colors.BLACK, font_family="Flame"))
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ),
            # Контейнер для кнопки настроек
            ft.Container(
                width=2000,
                height=50,
                content=ft.IconButton(
                    icon=ft.Icons.SETTINGS_OUTLINED,  # Иконка шестеренки
                    icon_size=40,
                    icon_color=top_bar_color,
                    focus_color=ft.colors.WHITE,
                    on_click=lambda e: open_settings_menu(page),  # Функция для открытия меню настроек
                ),
                alignment=ft.Alignment(1.0, -1.0),  # Выравнивание контейнера в правый верхний угол
                margin=ft.Margin(top=20, right=20, left=0, bottom=0),  # Отступы от краев экрана (если нужно)
            ),
            # Контейнер для кнопки перезагрузки
            ft.Container(
                width=50,
                height=50,
                content=reset_button,
                alignment=ft.Alignment(-1.0, -1.0),  # Выравнивание контейнера в левый верхний угол
                margin=ft.Margin(top=20, right=0, left=20, bottom=0),  # Отступы от краев экрана (если нужно)
            )
        ]
    )

    # Вкладки
    tabs_content = ft.Column(
        controls=[
            ft.Container(margin=ft.Margin(top=175, left=0, right=0, bottom=0),  # Отступ сверху для опускания вкладок вниз
                content=ft.Tabs(
                    animation_duration=600,
                    padding=15,  # Уменьшено значение padding для уменьшения высоты вкладок
                    height=1500,
                    label_color=top_bar_color,
                    label_text_style=ft.TextStyle(color=top_bar_color, font_family="Flame"),
                    divider_color=ft.colors.TRANSPARENT,
                    indicator_color=top_bar_color,
                    tabs=[
                        ft.Tab(
                            text="Основные сведения",
                            icon=Icons.DOCUMENT_SCANNER_OUTLINED,
                            content=ft.Row(  # Горизонтальное расположение блоков
                                alignment=ft.MainAxisAlignment.START,  # Располагаем блоки по горизонтали
                                vertical_alignment=ft.CrossAxisAlignment.START,
                                controls=[
                                    # Блок слева - entries
                                    ft.Column(
                                        expand=True,  # Растягиваем колонку по ширине
                                        scroll=ft.ScrollMode.ALWAYS,
                                        alignment=ft.MainAxisAlignment.START,
                                        controls=[
                                            ft.Column(
                                                expand=True,
                                                scroll=ft.ScrollMode.ALWAYS,
                                                alignment=ft.MainAxisAlignment.START,
                                                controls=[entries_containers[field_name] for field_name in entries]
                                                # Используем контейнеры вместо TextField
                                            )

                                        ],
                                    ),
                                    # Блок по центру - Явка сторон
                                    ft.Column(
                                        scroll=ft.ScrollMode.ALWAYS,
                                        alignment=ft.MainAxisAlignment.START,
                                        controls=[
                                            ft.Container(
                                                visible=True,  # По умолчанию показываем
                                                content=ft.Column(controls=[
                                                    ft.Text("Явка истца:", color=attendance_options_color,
                                                            font_family="Flame", size=16),
                                                    plaintiff_attendance
                                                ]),
                                                key="plaintiff_attendance_container"
                                            ),
                                            ft.Container(
                                                visible=True,
                                                content=ft.Column(controls=[
                                                    ft.Text("Явка ответчика:", color=attendance_options_color,
                                                            font_family="Flame", size=16),
                                                    defendant_attendance
                                                ]),
                                                key="defendant_attendance_container"
                                            ),
                                            ft.Container(
                                                visible=True,
                                                content=ft.Column(controls=[
                                                    ft.Text("Явка третьих лиц:", color=attendance_options_color,
                                                            font_family="Flame", size=16),
                                                    third_party_attendance
                                                ]),
                                                key="third_party_attendance_container"
                                            ),
                                            ft.Container(
                                                visible=False,
                                                # Скрыто по умолчанию, так как особое производство выключено
                                                content=ft.Column(controls=[
                                                    ft.Text("Явка заявителя:", color=attendance_options_color,
                                                            font_family="Flame", size=16),
                                                    applicant_attendance
                                                ]),
                                                key="applicant_attendance_container"
                                            ),
                                            ft.Container(
                                                visible=False,
                                                content=ft.Column(controls=[
                                                    ft.Text("Явка заинтересованных лиц:",
                                                            color=attendance_options_color, font_family="Flame",
                                                            size=16),
                                                    interested_persons_attendance
                                                ]),
                                                key="interested_persons_attendance_container"
                                            ),
                                        ],
                                    ),
                                    # Блок справа - descriptive_text и pleading_text
                                    ft.Column(
                                        expand=True,  # Растягиваем колонку по ширине
                                        scroll=ft.ScrollMode.ALWAYS,
                                        alignment=ft.MainAxisAlignment.START,
                                        controls=[
                                            ft.Container(
                                                content=descriptive_text,
                                                blur=Blur(10, 12, BlurTileMode.MIRROR),
                                                border_radius=18,
                                                expand=True,
                                                padding=5
                                            ),
                                            ft.Container(
                                                content=pleading_text,
                                                blur=Blur(10, 12, BlurTileMode.MIRROR),
                                                border_radius=18,
                                                expand=True,
                                                padding=5
                                            ),
                                            case_type_selector,
                                        ],
                                    ),
                                ],
                            ),
                        ),
                        ft.Tab(
                            text="Выбор шаблона",
                            icon=Icons.PSYCHOLOGY_ALT_OUTLINED,
                            content=ft.Column(
                                controls=[template_selector],
                            ),
                        ),
                        ft.Tab(
                            text="Дополнительные сведения",
                            icon=Icons.EDIT_DOCUMENT,
                            content=ft.Column(
                                controls=[
                                    optional_entries_tab,
                                    ft.Container(
                                        content=create_button,
                                        alignment=ft.Alignment(0.0, -1.0)
                                    ),
                                    ft.Container(
                                        content=create_special_button,
                                        alignment=ft.Alignment(0.0, -1.0)
                                    ),
                                    ft.Container(
                                        content=create_extramural_button,
                                        alignment=ft.Alignment(0.0, -1.0)
                                    ),
                                ],
                            ),
                        ),
                        ft.Tab(
                            text="Создание шаблона (В РАЗРАБОТКЕ)",
                            content=ft.Column(
                                controls=[document_text, analyze_button],
                            ),
                        ),
                    ],
                    selected_index=0,  # Первая вкладка по умолчанию
                ),
            ),
        ],
    )

    #Главная страница
    page.add(
        ft.Stack(
            controls=[
                BackGround,  # Фон (самый нижний слой)
                topbar,  # Топбар (прикреплен поверх фона)
                tabs_content  # Вкладки (поверх фон и топбар)
            ],
            alignment=ft.Alignment(-1.0, -1.0),  # Выравнивание всех элементов в Stack по верхнему левому углу
        )
    )


