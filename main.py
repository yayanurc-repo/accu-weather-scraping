import sys
import scraper_bs4_selenium as accu_weather


def get_menu():
    return accu_weather.menu_to_number(input('Type 1 or 2: '))


def get_keyword():
    kwd = input('\nInput your keyword: ')
    kw = kwd.replace(' ', '+')
    is_data_found = accu_weather.find_keyword(kw)
    return is_data_found


def get_back_main_menu():
    return input('\nBack to Main Menu? y/n: ').lower()


while True:
    print('░░░░░░ Accu Weather Menu ░░░░░░')
    print('░   1. Scraping by keyword    ░')
    print('░   2. Exit                   ░')
    print('░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░')

    menu = get_menu()
    while menu not in range(1, 3):
        menu = get_menu()
    else:
        if menu == 1:
            keyword = get_keyword()
            # while not keyword:
            #     keyword = get_keyword()

            back = get_back_main_menu()
            while back not in ('y', 'n'):
                back = get_back_main_menu()
            else:
                if back == 'y':
                    accu_weather.print_new_empty_line()
                    continue
                else:
                    print('\nSee you later!')
                    break
        else:
            print('\nSee you later!')
            sys.exit()
