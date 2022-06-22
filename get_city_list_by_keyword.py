from bs4 import BeautifulSoup
from fake_headers import Headers
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def get_city_list_by_keyword(keyword):
    url = f'https://www.accuweather.com/en/search-locations?query={keyword}'

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
    driver = webdriver.Chrome(executable_path=driver_path, options=options)
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, 'lxml')
    driver.close()

    try:
        tag_a_list = soup.find('div', attrs={'class': 'locations-list content-module'}).find_all('a', href=True)
    except AttributeError:
        print(f'\n░░░ No data found (london) ░░░')
        tag_a_list = None

    count_list = 0
    if tag_a_list is not None:
        for a in tag_a_list:
            count_list += 1
            href = a['href']
            city = a.getText(strip=True)
            print(f'{count_list}. {city} => https://www.accuweather.com{href}')


get_city_list_by_keyword('london')
