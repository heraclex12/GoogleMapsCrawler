from selenium import webdriver
import time
import os
import _thread
import datetime
import csv
import re
import atexit
from collections import deque

# prevent loading image and set up disk cache
# chromeOptions = webdriver.ChromeOptions()
# prefs = { 'disk-cache-size':4096}
# chromeOptions.add_experimental_option('prefs', prefs)

start_point = "@{lat},{lon},15z"
initial_URL = "https://www.google.com/maps"

starting_coordinate = [
    "10.7754483_106.6895788",
    "12.2428411_109.1819358",
    "10.9688102_106.8805736",
    "21.053238_105.8260943"
]

time_delay = 5
time_mini_delay = 0.2
nullValue = "None"
max_attempt = 20  # maxmimum attempt to locate element

# set_keywords = ["school", "hospital", "bank", "restaurant", "bar", "coffee", "parking lot", "post office",
#                 "supermarket", "park", "garden", "beach", "store", "bus terminal", "sport center", "University",
#                 "Theater", "Mall", "FireStation", "Police office", "ATM", "Gas station", "Temple"]

set_keywords = ["mall", ]
start_index = 0
current_key_word = ""

main_driver = webdriver.Chrome(os.getcwd() + "/chromedriver")
main_driver.implicitly_wait(time_delay)

# Write to file
# filename = str(time.ctime()) + ".csv"
# filename = filename.replace(":", "-").replace(' ', '_')
# output_file = csv.writer(open("data/" + filename, "a", encoding='utf-8'))
# output_file.writerow(["location_name", "review_num", "type", "address", "lat", "lon"])
output_file = None
file = None


list_location_gotten = set()
list_needed_get = deque()

count_other_country = 0


def append_to_file(content):
    output_file.writerow(content)
    file.flush()


def go_back(driver):
    back_button = find_element_by_xpath_until_found(driver,
                                                    "//button[@class='section-back-to-list-button blue-link noprint']",
                                                    False)
    if back_button is not None:
        cnt = 0
        while True:
            try:
                back_button.click()
                break
            except:
                cnt += 1
                if cnt > max_attempt:
                    print("!!!!---Can not go_back. Maybe can't find the back button ", cnt)
                    break


def init_search(driver, keyword):
    try:
        search_bar_input = find_element_by_xpath_until_found(driver, "//input[@id='searchboxinput']", False)
        search_bar_input.click()
        search_bar_input.clear()
        search_bar_input.send_keys(keyword)

        search_bar_button = find_element_by_xpath_until_found(driver, "//button[@id='searchbox-searchbutton']", False)
        search_bar_button.click()

    except:
        driver.delete_all_cookies()
        driver.quit()
        time.sleep(time_delay)
        driver = webdriver.Chrome(os.getcwd() + "/chromedriver")
        driver.get(target_URL)
        driver.implicitly_wait(time_delay)

    return driver


def get_result_div(driver):
    result_div_list = driver.find_elements_by_class_name("section-result")
    cnt = 0
    while len(result_div_list) == 0:  # if not found, meaning that is not loaded yet
        result_div_list = driver.find_elements_by_class_name("section-result")
        cnt += 1
        if cnt > max_attempt:
            print("!!!!--- Can't find location results in search")
            return

    cnt = 0
    for count in range(0, len(result_div_list)):
        current_div_list = driver.find_elements_by_class_name("section-result")
        while len(current_div_list) == 0:
            current_div_list = driver.find_elements_by_class_name("section-result")
            cnt += 1
            if cnt > max_attempt:
                print("!!!!--- Can't find location results in search")
                return

        try:
            current_result = current_div_list[count]
            fetch_return(main_driver, current_result)
        except IndexError:
            print("!!!!---IndexOutOfRange error")


def fetch_return(driver, div):
    cnt = 0
    global count_other_country
    while True:
        try:
            div.click()
            break
        except:
            print("Please wait to load...")
            time.sleep(time_mini_delay)
            cnt += 1
            if cnt > max_attempt:
                print("!!!!---Oops! Some error in listing location")
                go_back(driver)
                return

    time.sleep(time_mini_delay)
    cnt = 0
    while True:
        try:
            current_url = driver.current_url
            lat = re.search(r"(?<=!3d)-?[0-9\.]+", driver.current_url).group()
            lon = re.search(r"(?<=!4d)-?[0-9\.]+", driver.current_url).group()
            key = (lat + "_" + lon)
            break

        except:
            print("Please wait to load...")
            time.sleep(time_mini_delay)
            cnt += 1
            if cnt > max_attempt:
                print("!!!!---Oops! Some error in extract coordinate")
                go_back(driver)
                return

    keyword = current_key_word
    review_num = 0
    img = None
    addr = None
    if key not in list_location_gotten:
        location_name = find_element_by_xpath_until_found(driver,
                                                          "//div[@class='section-hero-header-title-description']//h1["
                                                          "contains(@class, 'section-hero-header-title-title')]",
                                                          True)
        try:
            review_num = driver.find_element_by_xpath(
                "(//span[@class='section-rating-term'])[1]/span/span/button[@class='widget-pane-link']").text.strip("()")
        except:
            print("!!!!---Can not find number review: " + location_name)

        try:
            addr = driver.find_element_by_xpath("//div[contains(@class, 'section-info-hoverable') and descendant-or-self::span[@aria-label='Địa chỉ']]").text
            # addr = driver.find_element_by_xpath("//div[@class='section-info-line']//span[@class='widget-pane-link']").text
            if re.search(r"(Việt Nam|Vietnam|VN)", addr) is None:
                count_other_country += 1
                go_back(driver)
                return
        except:
            print("!!!!---Can not find address: " + location_name)

        try:
            img = driver.find_element_by_xpath("//div[@class='section-hero-header-image']//img").get_attribute("src")
        except:
            print("!!!!---Can not find thumbnail image: " + location_name)

        try:
            keyword = driver.find_element_by_xpath(
                "(//span[@class='section-rating-term'])[2]/span/button[@class='widget-pane-link']").text
        except:
            print("!!!!---Can not find key word: " + location_name)

        print("-> Successfull get: " + location_name)
        store_info(location_name, review_num, keyword, addr, lat, lon, img)
        list_needed_get.append(key)
        list_location_gotten.add(key)

    # back to list search result
    go_back(driver)
    cnt = 0
    while driver.current_url == current_url:
        time.sleep(time_mini_delay)
        cnt += 1
        if cnt > max_attempt:
            print("!!!!---Some issues make current URL dont change, so need to break out of loop")
            break


def store_info(place_name, review_num, keyword, addr, lat, lon, img):
    info = [place_name, review_num, keyword, addr, lat, lon, img]
    append_to_file(info)


def turn_page(driver):
    if count_other_country >= max_attempt:
        return False

    try:
        next_button = driver.find_element_by_xpath("//button[contains(@id, 'section-pagination-button-next')]")
        next_button.click()
    except:
        # can not click, no next page
        return False
    return True


def find_element_by_xpath_until_found(driver, xpath, is_text):
    count = 0
    while True:
        try:
            element = driver.find_element_by_xpath(xpath)
            if is_text:
                return element.text
            else:
                return element
        except:
            count += 1
            print("!!!!---Can not find element by xpath -> ", xpath, " with count ", count)
            if count >= max_attempt:
                if is_text:
                    return nullValue
                else:
                    return None
            time.sleep(time_mini_delay)
            pass


def load_exist_place(key_word):
    list_place = None
    set_place = set()
    try:
        with open("temp/" + key_word + "_list.csv", "r", encoding='utf-8') as csv_file:
            data = csv.reader(csv_file)
            list_place = deque([r[0] for r in data])
        with open("temp/" + key_word + "_set.csv", "r", encoding='utf-8') as csv_file:
            data = csv.reader(csv_file)
            set_place = {r[0] for r in data}

    except:
        pass

    return set_place, list_place


def backup_list_place():
    with open("temp/" + current_key_word + "_list.csv", "w", encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, delimiter='\n')
        writer.writerow(list_needed_get)
        csv_file.flush()
    with open("temp/" + current_key_word + "_set.csv", "w", encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, delimiter='\n')
        writer.writerow(list_location_gotten)
        csv_file.flush()


def start(driver):
    global target_URL
    global current_key_word
    global list_needed_get
    global list_location_gotten
    global output_file
    global file

    for k in range(start_index, len(set_keywords)):
        current_key_word = set_keywords[k]
        if os.path.isfile(os.getcwd() + "/data/" + current_key_word + ".csv"):
            file = open("data/" + current_key_word + ".csv", "a", encoding='utf-8')
            output_file = csv.writer(file)
            list_location_gotten, list_needed_get = load_exist_place(current_key_word)
        else:
            file = open("data/" + current_key_word + ".csv", "a", encoding='utf-8')
            output_file = csv.writer(file)
            output_file.writerow(["location_name", "review_num", "type", "address", "lat", "lon", "img"])
            list_location_gotten = set()
            list_needed_get = deque(starting_coordinate)

        lat, lon = list_needed_get.popleft().split('_')
        print("Starting scope: ", lat, lon)
        target_URL = initial_URL + "/" + start_point.format(lat=lat, lon=lon) + "?hl=vi"
        driver.get(target_URL)
        driver = init_search(driver, current_key_word)

        while True:
            time.sleep(time_mini_delay)
            get_result_div(driver)
            if not turn_page(driver):
                if list_needed_get:
                    lat, lon = list_needed_get.popleft().split('_')
                    print("Change scope: ", lat, lon)
                    target_URL = initial_URL + "/" + start_point.format(lat=lat, lon=lon) + "?hl=vi"
                    driver.get(target_URL)
                    driver = init_search(driver, current_key_word)
                else:
                    break


if __name__ == '__main__':
    try:
        start(main_driver)

    except:
        backup_list_place()
    finally:
        file.close()

    atexit.register(backup_list_place)
