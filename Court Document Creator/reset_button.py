import flet as ft

def add_reset_button(page, entries, descriptive_text, pleading_text, optional_entries_fields, attendance_fields):
    def reset_fields(e):
        # Сбрасываем значения основных полей
        for entry in entries.values():
            entry.value = ""
            entry.update()

        # Сбрасываем текстовые поля
        descriptive_text.value = ""
        pleading_text.value = ""
        descriptive_text.update()
        pleading_text.update()

        # Сбрасываем опциональные поля
        for container in optional_entries_fields.values():
            if isinstance(container.content, ft.TextField):
                container.content.value = ""
                container.content.update()

        # Сбрасываем радиокнопки для явки сторон
        for field in attendance_fields:
            field.value = "Да"  # Устанавливаем значение по умолчанию
            field.update()

        # Обновляем страницу после всех изменений
        page.update()

    # Кнопка перезагрузки
    reset_button = ft.IconButton(
        icon=ft.icons.REFRESH,
        icon_size=40,
        icon_color=ft.colors.BLACK,
        tooltip="Перезагрузить",
        on_click=reset_fields,
    )

    return reset_button
