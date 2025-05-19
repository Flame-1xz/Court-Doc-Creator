# import stanza
# import pymorphy2
# import re
#
def create_template_from_document():
    pass
# # Загружаем модели Stanza и pymorphy2
# stanza.download('ru', processors='tokenize,ner', verbose=False)
# nlp = stanza.Pipeline('ru', processors='tokenize,ner', verbose=False)
# morph = pymorphy2.MorphAnalyzer()
#
# # Пример текста
# text = (
#     "рассмотрев в открытом судебном заседании по иску Пищиковой Оксаны Валериевны "
#     "к ООО «АГР» о расторжении брака. "
#     "Пищикова Оксана Валерьевна приобрела у Иванова Михаила Александровича автомобиль. "
#     "Пищикова О.В. хочет развестись с Ивановым М.А. "
#     "ООО «АГР» не хочет идти на уступки"
# )
#
# # Функция для нормализации частей ФИО с учетом пола
# def normalize_fio_parts(fio_parts):
#     normalized_parts = []
#
#     # Определяем род имени
#     name = fio_parts[1]  # Имя — это вторая часть ФИО
#     name_parsed = morph.parse(name)[0]
#     gender = name_parsed.tag.gender  # Определяем пол по имени
#
#     for i, part in enumerate(fio_parts):
#         # Для фамилии и отчества учитываем род
#         if i == 0:  # Фамилия
#             # Приводим фамилию к нормальной форме
#             parsed = morph.parse(part)[0]
#             base_surname = parsed.normal_form  # Базовая форма фамилии
#
#             # Проверяем род имени и меняем фамилию в зависимости от этого
#             if gender == 'masc' and 'femn' in [p.tag.gender for p in morph.parse(base_surname)]:
#                 # Если род имени мужской, убираем "а" из фамилии (преобразуем "Пищикова" в "Пищиков")
#                 base_surname = base_surname.rstrip('а')
#
#             normalized_parts.append(base_surname.capitalize())
#         elif i == 1:  # Имя
#             parsed = morph.parse(part)[0]
#             # Приводим имя к нормальной форме
#             normalized_parts.append(parsed.normal_form.capitalize())
#         elif i == 2:  # Отчество
#             parsed = morph.parse(part)[0]
#             base_patronymic = parsed.normal_form  # Базовая форма отчества
#
#             # Если род имени мужской, оставляем отчество как есть
#             if gender == 'masc':
#                 normalized_parts.append(base_patronymic.capitalize())
#             elif gender == 'femn':
#                 # Женский род, меняем окончание отчества на "на"
#                 base_patronymic = base_patronymic.replace('ич', 'на')
#                 normalized_parts.append(base_patronymic.capitalize())
#
#     return normalized_parts
#
# # Функция для поиска юридических лиц и их нормализации
# def normalize_organization(org_name):
#     # Приводим название организации к нормальной форме (упрощаем для замены)
#     return org_name.strip()
#
# # Обработка текста с помощью Stanza
# doc = nlp(text)
#
# # Словарь для хранения уникальных нормализованных ФИО и их меток
# fio_dict = {}
# fio_forms = {}
# fio_abbr = {}
# fio_count = 1
#
# # Словарь для юридических лиц
# org_dict = {}
# org_count = 1
#
# # Словарь для ролей
# roles = {"истец": [], "ответчик": [], "другое лицо": []}
#
# # Функция для обработки контекста и назначения ролей
# def assign_role_based_on_context(text, person_name, roles):
#     print(f"Проверка контекста для: {person_name}")  # Отладка: выводим имя для проверки
#
#     # Разбиваем ФИО на части
#     fio_parts = person_name.split()
#     normalized_fio = ' '.join(normalize_fio_parts(fio_parts))
#
#     # Ищем фразу "исковое заявление" и все, что после неё до "к"
#     pattern1 = r"исковое заявление\s+(.*?)\s+к"
#     pattern2 = r"по иску\s+(.*?)\s+к"
#     matches = re.findall(pattern1, text)
#     # Если не нашли, ищем второй паттерн
#     if not matches:
#         matches = re.findall(pattern2, text)
#
#     # Обрабатываем все найденные фрагменты, считаем их истцами
#     for match in matches:
#         # Разбиваем по частям и нормализуем, добавляем в список истцов
#         people = [person.strip() for person in match.split(",")]
#         for person in people:
#             person = person.strip()  # Убираем лишние пробелы
#             fio_parts = person.split()
#             normalized_person = ' '.join(normalize_fio_parts(fio_parts))  # Нормализуем каждого человека
#             if normalized_person and normalized_person not in roles['истец']:
#                 roles['истец'].append(normalized_person)
#                 print(f"Найден истец: {normalized_person}")
#
#     # Если человек уже в списке истцов, не добавляем его в другое лицо
#     if normalized_fio in roles['истец']:
#         print(f"{normalized_fio} уже является истцом")
#         return 'plaintiff'
#
#     # Ищем все сущности после "к" до "о" для определения ответчика
#     pattern = r"к\s+(.*?)\s+о"
#     matches = re.findall(pattern, text)
#
#     # Обрабатываем все найденные фрагменты, считаем их ответчиками
#     for match in matches:
#         # Разбиваем по частям и нормализуем, добавляем в список ответчиков
#         people = [person.strip() for person in match.split(",")]
#         for person in people:
#             person = person.strip()  # Убираем лишние пробелы
#             fio_parts = person.split()
#             normalized_person = ' '.join(normalize_fio_parts(fio_parts))  # Нормализуем каждого человека
#             if normalized_person and normalized_person not in roles['ответчик']:
#                 roles['ответчик'].append(normalized_person)
#                 print(f"Найден ответчик: {normalized_person}")
#
#     # Если человек уже в списке ответчиков, не добавляем его в другое лицо
#     if normalized_fio in roles['ответчик']:
#         print(f"{normalized_fio} уже является ответчиком")
#         return 'defendant'
#
#     # Если контексты для истца и ответчика не найдены, добавляем как другое лицо
#     else:
#         print(f"Контекст для другого лица: {normalized_fio}")  # Отладка
#         if normalized_fio not in roles['другое лицо']:
#             roles['другое лицо'].append(normalized_fio)
#         return 'другое лицо'
#
# # Извлекаем и нормализуем сущности типа 'PER' (персоналии) и 'ORG' (организации)
# for ent in doc.entities:
#     if ent.type == 'PER':  # Персоналии
#         fio_parts = ent.text.split()
#         if len(fio_parts) == 3:  # Только для ФИО с тремя частями
#             normalized_parts = normalize_fio_parts(fio_parts)
#             normalized_fio = " ".join(normalized_parts)
#
#             # Определим роль на основе контекста
#             role = assign_role_based_on_context(text, normalized_fio, roles)
#
#             # Используем роль вместо тега типа ФИО1, ФИО2
#             if normalized_fio not in fio_dict:  # Если новое нормализованное ФИО
#                 fio_dict[normalized_fio] = f"{{{role.capitalize()}}}"
#
#             # Добавляем сокращенные формы в fio_abbr
#             fio_abbr[f"{normalized_parts[0]} {normalized_parts[1][0]}.{normalized_parts[2][0]}."] = normalized_fio
#
#             # Сохраняем формы каждой части ФИО
#             if normalized_fio not in fio_forms:
#                 fio_forms[normalized_fio] = {part: set() for part in normalized_parts}
#             for part, normalized_part in zip(fio_parts, normalized_parts):
#                 fio_forms[normalized_fio][normalized_part].add(part)
#
#
# # Функция для генерации падежных форм фамилии
# def generate_surname_cases(surname, gender):
#     """
#     Генерирует все падежные формы фамилии в единственном числе с учетом заданного рода.
#
#     :param surname: Фамилия в начальной форме.
#     :param gender: Род ('masc' или 'femn').
#     :return: Словарь с падежными формами фамилии.
#     """
#     parsed_surname = morph.parse(surname)[0]
#     surname_forms = {}
#     for case in ['nomn', 'gent', 'datv', 'accs', 'ablt', 'loct']:
#         # Указываем род и единственное число
#         surname_form = parsed_surname.inflect({case, gender, 'sing'})
#         if surname_form:
#             surname_forms[case] = surname_form.word.capitalize()
#     return surname_forms
#
#
# # Функция для обработки сокращённых форм ФИО
# def generate_abbr_cases(fio_parts):
#     surname, name, patronymic = fio_parts
#     # Создаем сокращенные формы ФИО
#     abbr_fio_full = f"{surname} {name[0]}.{patronymic[0]}."
#     return abbr_fio_full
#
#
# # Обновление структуры fio_forms для сокращённых форм
# for normalized_fio, replacement in fio_dict.items():
#     fio_parts = normalized_fio.split()
#     surname, name, patronymic = fio_parts
#
#     # Определяем род по имени
#     name_gender = morph.parse(name)[0].tag.gender
#
#     # Генерация всех падежей для фамилии с учетом рода и числа
#     surname_forms = generate_surname_cases(surname, name_gender)
#
#     # Создание сокращенных форм и добавление в fio_forms
#     abbr_fio_full = generate_abbr_cases(fio_parts)
#     if abbr_fio_full not in fio_forms[normalized_fio]:
#         fio_forms[normalized_fio][abbr_fio_full] = set()
#
#     for case, surname_form in surname_forms.items():
#         abbr_case_form = f"{surname_form} {name[0]}.{patronymic[0]}."
#         fio_forms[normalized_fio][abbr_fio_full].add(abbr_case_form)
#
#
# # Функция для замены всех форм ФИО в тексте
# def replace_fio_in_text(text, fio_dict, fio_forms,org_dict):
#     for normalized_fio, replacement in fio_dict.items():
#         surname, name, patronymic = normalized_fio.split()
#         # Генерируем шаблоны для каждой части
#         patterns = [
#             rf"{surname_form}\s+{name_form}\s+{patronymic_form}"
#             for surname_form in fio_forms[normalized_fio][surname]
#             for name_form in fio_forms[normalized_fio][name]
#             for patronymic_form in fio_forms[normalized_fio][patronymic]
#         ]
#         # Добавляем сокращённые формы (инициалы)
#         abbr_forms = fio_forms[normalized_fio].get(f"{surname} {name[0]}.{patronymic[0]}.", set())
#         patterns.extend(abbr_forms)
#
#         # Объединяем все шаблоны в один регулярное выражение
#         combined_pattern = "|".join(patterns)
#         # Заменяем все формы ФИО на метку
#         text = re.sub(combined_pattern, replacement, text, flags=re.IGNORECASE)
#     # Меняем все организации в тексте
#     for org_name, replacement in org_dict.items():
#         text = re.sub(rf"\b{re.escape(org_name)}\b", replacement, text, flags=re.IGNORECASE)
#
#     return text
#
# # Заменяем ФИО в тексте
# new_text = replace_fio_in_text(text, fio_dict, fio_forms,org_dict)
#
# # Выводим результаты
# print("Нормализованные ФИО:", list(fio_dict.keys()))
# print("Измененный текст:", new_text)
# print("Роли:", roles)
