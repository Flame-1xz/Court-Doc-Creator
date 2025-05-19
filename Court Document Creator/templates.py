import os
import re
import flet as ft
from docx import Document


#Функция для генерации полей из шаблонов
def generate_optional_entries(template_text, entries):
    """
    Находит в тексте опциональные поля и генерирует словарь с их объектами.
    Исключает поля, уже представленные в entries.
    """
    optional_entries = {}

    # Регулярное выражение для поиска шаблонов {Название поля}
    pattern = r"\{(.*?)\}"

    # Ищем все совпадения в тексте
    matches = re.findall(pattern, template_text)

    # Преобразуем ключи основных сведений для исключения
    excluded_labels = {field.label for field in entries.values()}

    # Вручную добавляем поля для исключения (например, падежи истца и ответчика)
    manually_excluded_fields = {"plaintiff",
                                "plaintiff:gent", "plaintiff:datv", "plaintiff:accs",
                                "plaintiff:ablt", "plaintiff:loct", "defendant",
                                "defendant:gent", "defendant:datv", "defendant:accs",
                                "defendant:ablt", "defendant:ablt", "crux_of_the_matter", "pleading_part",
                                "applicant","applicant:gent", "applicant:datv", "applicant:accs",
                                "applicant:ablt", "applicant:loct",
                                }

    # Объединяем все поля для исключения
    excluded_labels.update(manually_excluded_fields)

    # Создаем опциональные поля, исключая основные
    for match in matches:
        if match not in excluded_labels:
            field = ft.TextField(label=match)
            optional_entries[match] = field

    return optional_entries

# Функция загрузки шаблонов
def load_templates():
    if not os.path.exists("Templates of motivational parts"):
        os.makedirs("Templates of motivational parts")
    return [f for f in os.listdir("Templates of motivational parts") if f.endswith('.docx')]

def load_template_text(template_name):
    # Папка, где хранятся шаблоны
    templates_directory = "Templates of motivational parts"

    # Убедитесь, что имя шаблона заканчивается на .docx
    template_name = f"{template_name}.docx" if not template_name.endswith(".docx") else template_name

    # Формируем полный путь к файлу
    template_path = os.path.join(templates_directory, template_name)

    # Проверяем, существует ли файл по указанному пути
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Шаблон '{template_name}' не найден в папке '{templates_directory}'.")

    # Если файл найден, выводим путь для отладки
    print(f"Файл найден: {template_path}")

    # Открываем шаблон .docx
    doc = Document(template_path)

    # Извлекаем текст всех абзацев
    template_text = "\n".join([para.text for para in doc.paragraphs])

    return template_text


