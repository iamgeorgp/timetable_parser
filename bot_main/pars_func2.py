'''
Main Functions for Web Parsing
'''
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

from datetime import datetime

from icalendar import Calendar, Event
# from ics import Calendar, Event

import w_func

# F: service + office driver 
def ind_driver():
    # script_directory = os.path.dirname(os.path.abspath(__file__))
    # driver_path = os.path.join(script_directory, "msedgedriver")

    # Получить текущую директорию скрипта (папка "bot_main")
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Подняться на уровень выше к общей папке проекта и зайти в папку "config"
    config_directory = os.path.join(os.path.dirname(script_directory), "config")

    # Путь к драйверу в папке "config"
    driver_path = os.path.join(config_directory, "msedgedriver")

    # Create objects Service & Options
    service = Service(driver_path)
    options = Options()
    options.add_argument('--page-load-strategy=interactive')  # Установка значения "interactive"
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-browser-side-navigation')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-default-apps')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-logging')
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--disable-bundled-ppapi-flash')
    options.add_argument('--disable-extensions')
    options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_argument("--blink-settings=imagesEnabled=false")
    prefs = {
        'profile.managed_default_content_settings.fonts': 1  # Отключение загрузки шрифтов
    }
    options.add_experimental_option('prefs', prefs)
    return service, options



# global driver
# global service

# Path to Edge driver 
# script_directory = os.path.dirname(os.path.abspath(__file__))
# driver_path = os.path.join(script_directory, "msedgedriver")
    
# # Создаем объект Service с указанием пути к файлу драйвера
# service = Service(driver_path)
# global chrome_options





# F: check group number input 
async def check_group(group_number):
    service, options = ind_driver()
    driver = webdriver.Edge(service=service, options=options)
    try:
        url = "https://rasp.rea.ru/"  
        driver.get(url)
        group_input = WebDriverWait(driver, 0.1).until(EC.presence_of_element_located((By.ID, "search")))
        group_input.send_keys(group_number)
        group_input.send_keys(Keys.ENTER)
        driver.implicitly_wait(1)
        contains_digits = any(char.isdigit() for char in group_number)
        FindError = driver.find_elements(By.XPATH, "//h2[contains(text(), 'По запросу')]")
        if not(contains_digits) or len(FindError) > 0:
            return False
        global current_url
        current_url = driver.current_url
        return True
    finally:
        driver.quit()

def send_schedule(message, group_numbers, chat_id):
    message.answer("⏳ Downloading...")
    ind_driver()
    driver = webdriver.Edge(service=service, options=chrome_options)
    driver.get(current_url)
    
    try:
        wait = WebDriverWait(driver, 1)  # Увеличьте время ожидания, если это необходимо
        wait.until(EC.presence_of_element_located((By.ID, "zoneTimetable")))
        
        zoneTimetable = driver.find_element(By.ID, 'zoneTimetable')
        slots = zoneTimetable.find_elements(By.CLASS_NAME, 'slot')
        
        cal = Calendar()
        
        for slot in slots:
            if not slot.find_elements(By.XPATH, ".//td[@colspan='3']"):
                second_td = slot.find_element(By.XPATH, ".//td[2]")
                a_elements = second_td.find_elements(By.TAG_NAME, 'a')
                
                for a in a_elements:
                    driver.execute_script("arguments[0].scrollIntoView(true);", a)
                    driver.execute_script("arguments[0].click();", a)
                    
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'element-info-body')))
                    info_body = driver.find_elements(By.CLASS_NAME, 'element-info-body')
                    
                    for each_info_body in info_body:
                        html_code = each_info_body.get_attribute("outerHTML")
                        soup = BeautifulSoup(html_code, 'html.parser')
                        
                        lesson_title = soup.find('h5').text.strip()
                        type_of_lesson = soup.find('strong').text.strip()
                        date_info = soup.find(text=re.compile(r'\d+ \w+ \d+')).strip()
                        
                        match = re.match(r"(\w+), (\d+) (\w+) (\d+), (\d+) (\w+)", date_info)
                        if match:
                            day_of_week, day, month, year, lesson_number, lesson_word = match.groups()
                        
                        teacher_info = soup.find('a').text.strip()
                        name_parts = teacher_info.split()[1:]
                        teacher_name = ' '.join(name_parts)
                        
                        room_info = re.findall(r'(\d+)\sкорпус\s-\s+(\d+)', soup.text)
                        auditorium = ''
                        
                        if room_info:
                            corpus, room_number = room_info[0]
                            auditorium = f"{corpus}-{room_number}"
                        
                        event = Event()
                        event.add('summary', lesson_title)
                        event.add('description', type_of_lesson + '\n' + teacher_name)
                        begin, end = w_func.date_converter(lesson_number, day, month, year)
                        event.add('location', auditorium)
                        event.add('dtstart', begin)
                        event.add('dtend', end)
                        cal.add_component(event)
                    
                    close_button = driver.find_element(By.CSS_SELECTOR, 'button.close')
                    driver.execute_script("arguments[0].click();", close_button)
        
        valid_groupnumber = re.sub(r'[/:]', '-', group_numbers[chat_id])
        current_datetime = datetime.now()
        file_path = str(valid_groupnumber) + '_' + current_datetime.strftime('%Y-%m-%d_%H-%M-%S') + '.ics'
        
        with open(file_path, 'wb') as f:
            f.write(cal.to_ical())
        
        message.answer_document(open(file_path, 'rb'))
        os.remove(file_path)
    
    finally:
        driver.quit()


def send_n_schedule(update, group_numbers, chat_id):
    update.message.reply_text("⏳ Загружаю файл...\nОсталось совсем чуть-чуть")
    
    driver = webdriver.Edge(service=service, options=options)
    driver.get(current_url)
    print(f'!!!!---!!!  {current_url}')
    next_week_button = driver.find_element(By.XPATH, "//button[@class='content weekselbtn']")
    driver.execute_script("arguments[0].scrollIntoView(true);", next_week_button)
    next_week_button.click()

    
    try:
        wait = WebDriverWait(driver, 10)  # Увеличьте время ожидания, если это необходимо
        wait.until(EC.presence_of_element_located((By.ID, "zoneTimetable")))
        
        zoneTimetable = driver.find_element(By.ID, 'zoneTimetable')
        slots = zoneTimetable.find_elements(By.CLASS_NAME, 'slot')
        
        cal = Calendar()

        
        
        for slot in slots:
            if not slot.find_elements(By.XPATH, ".//td[@colspan='3']"):
                second_td = slot.find_element(By.XPATH, ".//td[2]")
                a_elements = second_td.find_elements(By.TAG_NAME, 'a')
                
                for a in a_elements:
                    driver.execute_script("arguments[0].scrollIntoView(true);", a)
                    driver.execute_script("arguments[0].click();", a)
                    
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'element-info-body')))
                    info_body = driver.find_elements(By.CLASS_NAME, 'element-info-body')
                    
                    for each_info_body in info_body:
                        html_code = each_info_body.get_attribute("outerHTML")
                        soup = BeautifulSoup(html_code, 'html.parser')
                        
                        lesson_title = soup.find('h5').text.strip()
                        type_of_lesson = soup.find('strong').text.strip()
                        date_info = soup.find(text=re.compile(r'\d+ \w+ \d+')).strip()
                        
                        match = re.match(r"(\w+), (\d+) (\w+) (\d+), (\d+) (\w+)", date_info)
                        if match:
                            day_of_week, day, month, year, lesson_number, lesson_word = match.groups()
                        
                        teacher_info = soup.find('a').text.strip()
                        name_parts = teacher_info.split()[1:]
                        teacher_name = ' '.join(name_parts)
                        
                        room_info = re.findall(r'(\d+)\sкорпус\s-\s+(\d+)', soup.text)
                        auditorium = ''
                        
                        if room_info:
                            corpus, room_number = room_info[0]
                            auditorium = f"{corpus}-{room_number}"
                        
                        event = Event()
                        event.add('summary', lesson_title)
                        event.add('description', type_of_lesson + '\n' + teacher_name)
                        begin, end = w_func.date_converter(lesson_number, day, month, year)
                        event.add('location', auditorium)
                        event.add('dtstart', begin)
                        event.add('dtend', end)
                        cal.add_component(event)
                    
                    close_button = driver.find_element(By.CSS_SELECTOR, 'button.close')
                    driver.execute_script("arguments[0].click();", close_button)
        
        valid_groupnumber = re.sub(r'[/:]', '-', group_numbers[chat_id])
        current_datetime = datetime.now()
        file_path = str(valid_groupnumber) + '_' + current_datetime.strftime('%Y-%m-%d_%H-%M-%S') + '.ics'
        
        with open(file_path, 'wb') as f:
            f.write(cal.to_ical())
        
        update.message.reply_document(open(file_path, 'rb'))
        os.remove(file_path)
    
    finally:
        driver.quit()