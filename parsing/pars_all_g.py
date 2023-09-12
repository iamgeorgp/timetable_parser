from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import re
import sqlite3
from icalendar import Calendar, Event
import glob
import dateparser
import time 

# F: get lesson star&end 
def date_converter(pair_number, day, month, year):
    # create a date with time according to the date and number of the lesson
    # return the beginning and end of the lesson
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

# F: service + office driver 
def ind_driver():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    # Go up a level to the shared project folder and go to the "config" folder
    config_directory = os.path.join(os.path.dirname(script_directory), "config")
    # The path to the driver in the "config" folder
    driver_path = os.path.join(config_directory, "msedgedriver.exe")
    print(driver_path)
    # Create objects Service & Options
    service = Service(driver_path)
    options = Options()
    options.add_argument('--page-load-strategy=interactive')  
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

    options.add_argument("--disable-popup-blocking")
    prefs = {
        'profile.managed_default_content_settings.fonts': 1  # Disable font loading
    }
    options.add_experimental_option('prefs', prefs)
    return driver_path, service, options




def send_current_schedule(driver, url_group, number_group, type_week):
    driver.get(url_group)
    time.sleep(3)
    if type_week == 'next_week':
        next_week_button = driver.find_element(By.XPATH, "//button[@class='content weekselbtn']")
        driver.execute_script("arguments[0].scrollIntoView(true);", next_week_button)
        next_week_button.click()
    
    wait = WebDriverWait(driver, 10)
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
                    begin, end = date_converter(lesson_number, day, month, year)
                    event.add('location', auditorium)
                    event.add('dtstart', begin)
                    event.add('dtend', end)
                    cal.add_component(event)
                
                close_button = driver.find_element(By.CSS_SELECTOR, 'button.close')
                driver.execute_script("arguments[0].click();", close_button)
    script_directory = os.path.dirname(os.path.abspath(__file__))
    # Получить текущую директорию скрипта (папка "bot_main")
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Подняться на уровень выше к общей папке проекта и зайти в папку "config"
    group_ics_path = os.path.join(os.path.dirname(script_directory), "group_schedule_ics", type_week)
    # Полный путь к файлу базы данных в папке "databases"

    valid_groupnumber = re.sub(r'[/:]', '-', number_group)

    file_path = group_ics_path + '\\' + str(valid_groupnumber)  + '.ics' # + '_' + current_datetime.strftime('%Y-%m-%d_%H-%M-%S')
    
    with open(file_path, 'wb') as f:
            f.write(cal.to_ical())

        

    









def pars_ics_for_db():
    
    # Получить список всех файлов в папке
    
    # Получить текущую директорию скрипта
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Полный путь к файлу базы данных в папке "databases"
    database_path = os.path.join(script_directory, '..', 'databases', 'hsci.db')
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM schedules")
    result = cursor.fetchall()

    driver_path, service, chrome_options = ind_driver()
    driver = webdriver.Edge(service=service, options=chrome_options)

    for each_group in result:
        number_currnet_group, url_current_group  = each_group[0], each_group[1]
        send_current_schedule(driver, url_current_group, number_currnet_group, 'current_week')
        # send_current_schedule(url_current_group, number_currnet_group, 'next_week')

def del_all_ics():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(script_directory, '..', 'group_schedule_ics', 'current_week')
    files = glob.glob(os.path.join(folder_path, "*"))
    # Удалить каждый файл в папке
    for file in files:
        try:
            os.remove(file)
        except Exception as e:
            print(f"File removing error {file}: {e}")