import os
import sys

import pymorphy2
import re

# Инициализация морфологического анализатора
morph = pymorphy2.MorphAnalyzer(path=r'C:\Users\64spe\AppData\Local\Programs\Python\Python312\Lib\site-packages\pymorphy2_dicts_ru\data')

# Шаблон для поиска переменных с указанием падежа
case_pattern = r"\{(\w+):(\w+)\}"

# Функция изменения падежа
def change_case(phrase, case):
    words = phrase.split()
    converted_words = []
    for word in words:
        parsed_word = morph.parse(word)[0]
        if parsed_word.inflect({case}):
            converted_word = parsed_word.inflect({case}).word
            if word.isupper():
                converted_word = converted_word.upper()
            elif word.istitle():
                converted_word = converted_word.capitalize()
        else:
            converted_word = word
        converted_words.append(converted_word)
    return " ".join(converted_words)

# Замена переменных с учетом падежей
def replace_variables_with_case(text, variables):

    def replace_match(match):
        var_name = match.group(1)  # Имя переменной
        case = match.group(2)      # Указанный падеж
        if var_name in variables:
            return change_case(variables[var_name], case)  # Применяем функцию изменения падежа
        return match.group(0)  # Если переменной нет, оставляем исходный текст

    return re.sub(case_pattern, replace_match, text)

#Функция для удаления лишних пробелов и переносов текста
def clean_text(text):
    # Удалить лишние пробелы и заменить несколько пробелов одним
    text = re.sub(r'\s+', ' ', text)
    # Удалить переносы строк
    text = text.replace('\n', ' ').replace('\r', '')
    # Удалить лишние пробелы в начале и конце текста
    return text.strip()
