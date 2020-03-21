from selenium import webdriver
import time
import os
import _thread
import datetime
import csv
import re

# prevent loading image and set up disk cache
# chromeOptions = webdriver.ChromeOptions()
# prefs = { 'disk-cache-size':4096}
# chromeOptions.add_experimental_option('prefs', prefs)


start_point = "@10.7754483,106.6895788,15z"
initial_URL = "https://www.google.com/maps"
target_URL = initial_URL + "/" + start_point + "?hl=vi"

timeDelay = 5
timeMiniDelay = 0.2
nullValue = "None"
max_attempt = 20  # maxmimum attempt to locate element

set_keywords = ["school", "hospital", "bank", "restaurant", "bar", "coffee", "parking lot", "post office",
                "supermarket", "park", "garden", "beach", "store", "bus terminal", "sport center", "University",
                "Theater", "Mall", "FireStation", "Police office", "ATM", "Gas station", "Temple"]
start_index = 3
current_key_word = ""

main_driver = webdriver.Chrome(os.getcwd() + "/chromedriver")
main_driver.get(target_URL)
main_driver.implicitly_wait(timeDelay)

# Write to file
filename = str(time.ctime()) + ".csv"
filename = filename.replace(":", "-").replace(' ', '_')
output_file = csv.writer(open("data/" + filename, "a", encoding='utf-8'))
output_file.writerow(["location_name", "review_num", "type", "address", "lat", "lon"])


def append_to_file(content):
    output_file.writerow(content)


def go_back(driver):
    back_button = find_element_by_xpath_until_found(driver,
                                                    "//button[@class='section-back-to-list-button blue-link noprint']",
                                                    False)
    back_button.click()


def init_search(driver, keyword):
    search_bar_input = find_element_by_xpath_until_found(driver, "//input[@id='searchboxinput']", False)
    search_bar_input.click()
    search_bar_input.clear()
    search_bar_input.send_keys(keyword)

    search_bar_button = find_element_by_xpath_until_found(driver, "//button[@id='searchbox-searchbutton']", False)
    search_bar_button.click()


def get_result_div(driver):
    result_div_list = driver.find_elements_by_class_name("section-result")
    while len(result_div_list) == 0:  # if not found, meaning that is not loaded yet
        result_div_list = driver.find_elements_by_class_name("section-result")

    for count in range(0, len(result_div_list)):
        current_div_list = driver.find_elements_by_class_name("section-result")
        while len(current_div_list) == 0:
            current_div_list = driver.find_elements_by_class_name("section-result")

        fetch_return(main_driver, current_div_list[count])


def fetch_return(driver, div):
    div.click()

    location_name = find_element_by_xpath_until_found(driver,
                                                      "//div[@class='section-hero-header-title-description']//h1["
                                                      "contains(@class, 'section-hero-header-title-title')]",
                                                      True)

    review_num = driver.find_element_by_xpath(
        "(//span[@class='section-rating-term'])[1]/span/span/button[@class='widget-pane-link']").text.strip("()")
    # more exactly use below
    # addr = driver.find_element_by_xpath("//div[contains(@class, 'section-info-hoverable') and descendant-or-self::span[@aria-label='Địa chỉ']]").text
    addr = driver.find_element_by_xpath("//div[@class='section-info-line']//span[@class='widget-pane-link']").text
    keyword = driver.find_element_by_xpath(
        "(//span[@class='section-rating-term'])[2]/span/button[@class='widget-pane-link']").text
    print(location_name)
    current_url = driver.current_url
    lat, lon, _ = re.search(r"(?<=\/@)[^\/]+", current_url).group().split(',')

    store_info(location_name, review_num, keyword, addr, lat, lon)

    # back to list search result
    go_back(driver)
    while driver.current_url == current_url:
        time.sleep(timeMiniDelay)


def store_info(place_name, review_num, keyword, addr, lat, lon):
    info = [place_name, review_num, keyword, addr, lat, lon]
    append_to_file(info)


def turn_page(driver):
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
            print("Can not find element by xpath -> ", xpath, " with count ", count)
            if count >= max_attempt and is_text:
                return nullValue
            time.sleep(timeMiniDelay)
            pass


def start(driver):
    for k in range(start_index, len(set_keywords)):
        current_key_word = set_keywords[k]
        init_search(driver, current_key_word)
        while True:
            time.sleep(timeDelay)
            get_result_div(driver)
            if turn_page(driver) == False:
                break


if __name__ == '__main__':
    start(main_driver)
    output_file.close()
