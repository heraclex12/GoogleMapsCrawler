from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os
import csv
import re

start_point = "@{lat},{lon},15z"
initial_URL = "https://www.google.com/maps/search"

time_delay = 5
time_mini_delay = 0.3
max_attempt = 20


options = Options()
options.add_argument('--headless')
main_driver = webdriver.Chrome(os.getcwd() + "/chromedriver", options=options)
main_driver.implicitly_wait(time_delay)

if __name__ == '__main__':
    new_data = []
    for filename in os.listdir(os.getcwd() + "/data"):
        with open("data/" + filename, "r", encoding='utf-8') as csv_file:
            data = csv.reader(csv_file)
            next(data, None)
            cnt = 0
            for row in data:
                target_URL = initial_URL + "/" + row[0].replace(" ", "+") + "/" + start_point.format(lat=row[4], lon=row[5]) + "?hl=vi"
                main_driver.get(target_URL)
                attempt_cnt = 0
                while True:
                    content = str(main_driver.page_source)
                    place_id = re.search(r"(?<=\")ChI[^\\]+", content)
                    attempt_cnt += 1
                    if place_id is None:
                        time.sleep(time_mini_delay)
                        if attempt_cnt > max_attempt:
                            print("Empty place_id:", row[0])
                            break
                    else:
                        place_id = place_id.group()
                        break

                new_data.append([place_id, ] + row)
                cnt += 1
                if cnt % 1000 == 0:
                    print(cnt)

        with open("data/" + "new_" + filename, "w", encoding='utf-8') as output_file:
            writer = csv.writer(output_file)
            writer.writerow(["place_id", "location_name", "review_num", "type", "address", "lat", "lon", "img"])
            writer.writerow(new_data)

    main_driver.quit()

