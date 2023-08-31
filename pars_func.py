import os
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
from selenium.webdriver import ActionChains
from ics import Calendar, Event
from datetime import datetime
import dateparser
from icalendar import Calendar, Event


# Определяем путь к папке, где находится скрипт
script_directory = os.path.dirname(os.path.abspath(__file__))


# Определяем путь к файлу драйвера в папке скрипта
driver_path = os.path.join(script_directory, "msedgedriver")

# Создаем объект Service с указанием пути к файлу драйвера
service = Service(driver_path)
options = Options()

global driver



def hihi():
    print('YOOOOOOOOOOOOOOO!!!')

def date_converter(pair_number, day, month, year):
    # создают дату со временем в соответсвии с датой и номера пары
    # возвращает начало и конец пары
    time_of_pair = {1: [[8, 30], [10, 00]],
                    2: [[10, 10], [11, 40]],
                    3: [[11, 50], [13, 20]],
                    4: [[14, 0], [15, 30]],
                    5: [[15, 40], [17, 10]],
                    6: [[17, 20], [18, 50]]
                    }
    timing_of_pair = time_of_pair[int(pair_number)]
    hour_begin = timing_of_pair[0][0]
    minute_begin = timing_of_pair[0][1]
    hour_end = timing_of_pair[1][0]
    minute_end = timing_of_pair[1][1]
    date_time_str_begin = f"{int(day)} {str(month)} {int(year)} {hour_begin:02d}:{minute_begin:02d}"
    date_time_str_end = f"{int(day)} {str(month)} {int(year)} {hour_end:02d}:{minute_end:02d}"
    return dateparser.parse(date_time_str_begin), dateparser.parse(date_time_str_end)

def check_group(group_number):
    driver = webdriver.Edge(service=service, options=options)
    try:
        # Открытие страницы
        url = "https://rasp.rea.ru/"  # Замените на URL нужного веб-сайта
        driver.get(url)

        # Нахождение поля ввода номера группы
        group_input = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, "search")))
        group_input.clear()
        group_input.send_keys(group_number)
        group_input.send_keys(Keys.ENTER)
        driver.implicitly_wait(0.5)
        FindError = driver.find_elements(By.XPATH, "//h2[contains(text(), 'По запросу')]")
        if len(FindError) > 0:
            return False
        global current_url
        current_url = driver.current_url
        return True
    finally:
        # Закрываем браузер в любом случае
        driver.quit()

def send_schedule(update, group_numbers, chat_id):
    update.message.reply_text("⏳ Загружаю файл...\nОсталось совсем чуть-чуть")
    driver = webdriver.Edge(service=service, options=options)
    driver.get(current_url)
    # driver.implicitly_wait(2)
    # Поиск кнопки по CSS-селектору
    next_week_button = driver.find_element(By.XPATH, "//button[@class='content weekselbtn']")
    # Нажатие на кнопку с помощью JavaScript
    # driver.implicitly_wait(1)
    driver.execute_script("arguments[0].scrollIntoView(true);", next_week_button)
    
    
    # Ожидание загрузки страницы
    wait = WebDriverWait(driver, 2)  # Установите время ожидания (в секундах) вместо 10, если необходимо
    wait.until(EC.presence_of_element_located((By.ID, "zoneTimetable")))  # Здесь указывается локатор элемента, который должен быть видимым перед извлечением содержимого
    # Нахождение элемента <div id="zoneTimetable">
    zoneTimetable = driver.find_element(By.ID, 'zoneTimetable')
    driver.implicitly_wait(1)
    # Нахождение элемента <div class="row"> внутри zoneTimetable
    row = zoneTimetable.find_element(By.CLASS_NAME, 'row')
    # Нахождение элементов <div class="col-lg-6"> внутри row
    col_lg_6_elements = row.find_elements(By.CLASS_NAME, 'col-lg-6')
    cal = Calendar()
    # Проход по каждому <div class="col-lg-6">
    for col_lg_6 in col_lg_6_elements:
        # Нахождение всех элементов <div class="slot"> внутри col_lg_6
        slots_in_day = col_lg_6.find_elements(By.CLASS_NAME, 'slot')
        for slot in slots_in_day:
            # Проверка отсутствия элемента <td colspan="3"> внутри slot
            if not slot.find_elements(By.XPATH, ".//td[@colspan='3']"):
                # Нахождение второго <td> элемента внутри slot
                second_td = slot.find_element(By.XPATH, ".//td[2]")
                a_elements = second_td.find_elements(By.TAG_NAME, 'a')
                for a in a_elements:
                    driver.execute_script("arguments[0].scrollIntoView(true);", a)
                    driver.execute_script("arguments[0].click();", a)
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'element-info-body')))
                    # Нахождение элемента 'element-info-body' и получение его текста
                    info_body = driver.find_elements(By.CLASS_NAME, 'element-info-body')
                    teacher_info = ''
                    auditorium = ''
                    counter = 0
                    if len(info_body) == 1:
                        html_code = info_body[0].get_attribute("outerHTML")
                        soup = BeautifulSoup(html_code, 'html.parser')
                        # Название предмета
                        lesson_title = soup.find('h5').text.strip()
                        type_of_lesson = soup.find('strong').text.strip()
                        # Дата проведения
                        date_info = soup.find(text=re.compile(r'\d+ \w+ \d+')).strip()
                        match = re.match(r"(\w+), (\d+) (\w+) (\d+), (\d+) (\w+)", date_info)
                        if match:
                            # Извлечение элементов из регулярного выражения
                            day_of_week, day, month, year, lesson_number, lesson_word = match.groups()
                        teacher_info = soup.find('a').text.strip()
                        name_parts = teacher_info.split()[1:]  # Выбираем последние три элемента списка
                        teacher_name = ' '.join(name_parts)  # Объединяем элементы списка в строку с пробелами
                        room_info = re.findall(r'(\d+)\sкорпус\s-\s+(\d+)', soup.text)
                        if room_info:
                            corpus, room_number = room_info[0]
                            auditorium = f"{corpus}-{room_number}"
                        event = Event()
                        event.add('summary', lesson_title)
                        event.add('description', type_of_lesson + '\n' + teacher_name)
                        begin, end = date_converter(lesson_number, day, month, year)
                        event.add('location', f"{auditorium}")
                        event.add('dtstart', begin)  # Дата и время начала
                        event.add('dtend', end)
                        cal.add_component(event)
                        # event = Event()
                        # event.name = lesson_title
                        # event.begin, event.end = date_converter(lesson_number, day, month, year)
                        # event.location = f"{auditorium}"
                        # event.description = f"{teacher_info}"
                        # cal.events.add(event)
                        temp_lesson_title = lesson_title
                    else:
                        event = Event()
                        for each_info_body in info_body:
                            counter += 1
                            html_code = each_info_body.get_attribute("outerHTML")
                            soup = BeautifulSoup(html_code, 'html.parser')
                            # Название предмета
                            lesson_title = soup.find('h5').text.strip()
                            type_of_lesson = soup.find('strong').text.strip()
                            # Дата проведения
                            date_info = soup.find(text=re.compile(r'\d+ \w+ \d+')).strip()
                            match = re.match(r"(\w+), (\d+) (\w+) (\d+), (\d+) (\w+)", date_info)
                            if match:
                                # Извлечение элементов из регулярного выражения
                                day_of_week, day, month, year, lesson_number, lesson_word = match.groups()
                            # Проверка на существование подгрупп в одном предмете
                            if counter > 1 and lesson_title == temp_lesson_title:
                                teacher_info = soup.find('a').text.strip()
                                name_parts = teacher_info.split()[1:]  # Выбираем последние три элемента списка
                                teacher_name += '\n' + ' '.join(
                                    name_parts)  # Объединяем элементы списка в строку с пробелами
                                room_info = re.findall(r'(\d+)\sкорпус\s-\s+(\d+)', soup.text)
                                if room_info:
                                    corpus, room_number = room_info[0]
                                    auditorium = auditorium + '\n' + str(corpus) + '-' + str(room_number)
                                cal.subcomponents.remove(event)
                            else:
                                teacher_info = soup.find('a').text.strip()
                                name_parts = teacher_info.split()[1:]  # Выбираем последние три элемента списка
                                teacher_name = ' '.join(
                                    name_parts)  # Объединяем элементы списка в строку с пробелами
                                room_info = re.findall(r'(\d+)\sкорпус\s-\s+(\d+)', soup.text)
                                if room_info:
                                    corpus, room_number = room_info[0]
                                    auditorium = f"{corpus}-{room_number}"
                            event = Event()
                            event.add('summary', lesson_title)
                            event.add('description', type_of_lesson + '\n' + teacher_name)
                            begin, end = date_converter(lesson_number, day, month, year)
                            event.add('location', auditorium)
                            event.add('dtstart', begin)  # Дата и время начала
                            event.add('dtend', end)
                            cal.add_component(event)
                            # event = Event()
                            # event.name = lesson_title
                            # event.begin, event.end = date_converter(lesson_number, day, month, year)
                            # event.location = f"{auditorium}"
                            # event.description = f"{teacher_info}"
                            # cal.events.add(event)
                            temp_lesson_title = lesson_title
                    close_button = driver.find_element(By.CSS_SELECTOR, 'button.close')
                    driver.execute_script("arguments[0].click();", close_button)
    # file_path = 'events.ics'
    valid_groupnumber = re.sub(r'[/:]', '-', group_numbers[chat_id])
    current_datetime = datetime.now()
    file_path = str(valid_groupnumber) + '_' + current_datetime.strftime('%Y-%m-%d_%H-%M-%S') + '.ics'
    # file_path = f'{valid_groupnumber}_{(datetime.now())}.ics'
    with open(file_path, 'wb') as f:
        f.write(cal.to_ical())
    # Отправляем файл пользователю
    update.message.reply_document(open(file_path, 'rb'))
    # Удаляем временный файл
    os.remove(file_path)
    driver.quit()