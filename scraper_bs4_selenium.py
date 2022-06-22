import calendar

from bs4 import BeautifulSoup
# import re
# import json
# import pandas as pd
from fake_headers import Headers
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from threading import Event, Thread
from webdriver_manager.chrome import ChromeDriverManager


def menu_to_number(menu):
    try:
        menu = int(menu)
    except ValueError:
        menu = 0
    return menu


def print_new_empty_line():
    print('', end='\n')


def call_repeatedly(interval, func, *args):
    stopped = Event()

    def loop():
        while not stopped.wait(interval):  # the first call is in `interval` secs
            func(*args, end=' ')

    Thread(target=loop).start()
    return stopped.set


def get_soup(url):
    options = Options()
    # options.add_argument('headless')
    options.headless = True

    header = Headers(
        browser="chrome",  # Generate only Chrome UA
        os="mac",  # Generate any Mac platform
        headers=False,  # generate misc headers
    )
    custom_user_agent = header.generate()['User-Agent']
    options.add_argument(f"user-agent={custom_user_agent}")

    os_user_path = str(Path.home())
    chromedriver_path = '/.wdm/drivers/chromedriver/mac64/102.0.5005.61/chromedriver'

    # while True:
    progress = call_repeatedly(1, print, "★")  # Adding custom progress

    driver_path = f'{os_user_path}{chromedriver_path}'
    if driver_path is None:
        driver_path = ChromeDriverManager().install()
    driver = webdriver.Chrome(executable_path=driver_path, options=options)
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, 'lxml')
    driver.close()

    progress()  # Removing custom progress
    print_new_empty_line()
    return soup


def get_detail(city_list, selected_menu_city):
    selected_city = city_list[selected_menu_city - 1]
    url_detail = selected_city.split('$')[1]
    soup = get_soup(url_detail)

    current_weather_degree = soup.find('div', attrs={'class': 'cur-con-weather-card__panel'}) \
        .find('div', attrs={'class': 'forecast-container'}) \
        .find('div', attrs={'class': 'temp-container'}) \
        .find('div', attrs={'class': 'temp'}) \
        .getText(strip=True)
    try:
        current_weather_phrase = soup \
            .find('span', attrs={'class': 'phrase'}) \
            .getText(strip=True)
        current_weather_phrase = f', {current_weather_phrase}'
    except AttributeError:
        current_weather_phrase = ''
    try:
        current_weather_minute_cast = soup.find('p', attrs={'class': 'minutecast-banner__phrase'}) \
            .getText(strip=True)
        current_weather_minute_cast = f', {current_weather_minute_cast}'
    except AttributeError:
        current_weather_minute_cast = ''
    current_weather = f'{current_weather_degree}{current_weather_phrase}{current_weather_minute_cast}'

    current_date = soup.find('p', attrs={'class': 'date'}).getText(strip=True)
    current_day = current_date.split('/')[1]
    current_month = current_date.split('/')[0]
    current_date = f'{calendar.month_name[int(current_month)]}, {current_day}'

    current_time = soup.find('p', attrs={'class': 'cur-con-weather-card__subtitle'}).getText(strip=True)

    weather_quality = soup.find('div', attrs={'class': 'cur-con-weather-card__panel details-container'}) \
        .find_all('div', attrs={'class': 'spaced-content detail'})

    air_quality = weather_quality[0].find('span', attrs={'class': 'value'}).getText(strip=True)

    wind = weather_quality[1].find('span', attrs={'class': 'value'}).getText(strip=True)

    wind_gusts = weather_quality[2].find('span', attrs={'class': 'value'}).getText(strip=True)

    tomorrow_weather_card = soup.find('div', attrs={'data-qa': 'tomorrowWeatherCard'}) \
        .find('a') \
        .find('div', attrs={'class': 'card-content'})
    tomorrow_weather_degree = tomorrow_weather_card \
        .find('div', attrs={'class': 'forecast-container'}) \
        .find('div', attrs={'class': 'temp-container'}) \
        .find('div', attrs={'class': 'temp'}) \
        .getText(strip=True)
    tomorrow_weather_phrase = tomorrow_weather_card \
        .find('div', attrs={'class': 'phrase'}) \
        .getText(strip=True)
    tomorrow_weather = f'{tomorrow_weather_degree}, {tomorrow_weather_phrase}'

    weather = {
        'current_weather': current_weather,
        'current_date': current_date,
        'current_time': current_time,
        'air_quality': air_quality,
        'wind': wind,
        'wind_gusts': wind_gusts,
        'tomorrow_weather': tomorrow_weather
    }

    print(f"\n░░░ {selected_city.split('$')[0]} >>> Weather = {weather} ░░░")


def get_menu_city(tag_a_list, city_list):
    selected_menu_city = menu_to_number(input(f'Select one between 1 and {len(tag_a_list)}: '))

    while selected_menu_city not in range(1, len(tag_a_list) + 1):
        selected_menu_city = menu_to_number(input(f'Wrong, Select one between 1 and {len(tag_a_list)}: '))
    else:
        selected_city = city_list[selected_menu_city - 1].split('$')[0]
        print(f'\n░░░ Selected city: {selected_city} ░░░\n')
    return selected_menu_city


def show_menu_city(tag_a_list):
    print('\n░░░░░░░░░░░░░░░░░░░░░ City Menu ░░░░░░░░░░░░░░░░░░░░░')
    count_list = 0
    for a in tag_a_list:
        count_list += 1
        city = a.getText(strip=True)

        if city.__contains__('('):
            city = city.split('(')[0].replace(')', '')

        print(f"   {count_list}. {city}")
    print('░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░')


def get_city_list(tag_a_list):
    city_list = []
    for a in tag_a_list:
        city = a.getText(strip=True)

        href = a['href']
        # params_tag_a = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
        # city_key = params_tag_a['key'][0]

        if city.__contains__('('):
            city = city.split('(')[0].replace(')', '')

        url_detail = f'https://www.accuweather.com{href}'
        city_list.append(f'{city}${url_detail}')
    return city_list


def get_back_to_city_menu():
    back_to_city_menu = input('\nBack to Last City Menu? y/n: ').lower()
    while back_to_city_menu not in ('y', 'n'):
        back_to_city_menu = input('Back to Last City Menu? y/n: ').lower()
    return back_to_city_menu


def find_keyword(keyword):
    url = f'https://www.accuweather.com/en/search-locations?query={keyword}'
    print(f'\n░░░ Url: {url} ░░░\n')

    soup = get_soup(url)

    try:
        tag_a_list = soup.find('div', attrs={'class': 'locations-list content-module'}).find_all('a', href=True)
    except AttributeError:
        print(f'\n░░░ No data found ({keyword}) ░░░')
        tag_a_list = None

    if tag_a_list is not None:
        city_list = get_city_list(tag_a_list)

        while True:
            show_menu_city(tag_a_list)
            selected_menu_city = get_menu_city(tag_a_list, city_list)

            get_detail(city_list, selected_menu_city)

            back_to_city_menu = get_back_to_city_menu()
            if back_to_city_menu == 'y':
                continue
            else:
                return True
    else:
        return False
