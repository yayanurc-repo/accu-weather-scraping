import calendar

from bs4 import BeautifulSoup
from fake_headers import Headers
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def get_soup(url):
    options = Options()
    options.headless = True

    header = Headers(
        browser="chrome",  # Generate only Chrome UA
        os="mac",  # Generate any Mac platform
        headers=False,  # generate misc headers
    )
    custom_user_agent = header.generate()['User-Agent']
    options.add_argument(f"user-agent={custom_user_agent}")

    driver_path = ChromeDriverManager().install()
    if driver_path is None:
        driver_path = ChromeDriverManager().install()
    driver = webdriver.Chrome(executable_path=driver_path, options=options)
    driver.get(f'https://www.accuweather.com{url}')

    soup = BeautifulSoup(driver.page_source, 'lxml')
    driver.close()

    return soup


def get_detail(selected_city, url_detail):
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

    print(f"\n░░░ {selected_city} >>> Weather = {weather} ░░░")


get_detail('London, London, GB', '/web-api/three-day-redirect?key=328328&target=')
