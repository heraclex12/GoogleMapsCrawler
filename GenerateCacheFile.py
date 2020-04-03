import csv
import os


if __name__ == '__main__':
    for filename in os.listdir(os.getcwd() + "/data"):
        if not os.path.isfile(os.getcwd() + "/temp/" + filename.replace(".csv", "_set.csv")):
            with open("data/" + filename, 'r', encoding='utf-8') as csv_file:
                data = csv.reader(csv_file)
                next(data, None)
                with open("temp/" + filename.replace(".csv", "_set.csv"), 'w') as file:
                    for row in data:
                        key = row[4] + '_' + row[5]
                        file.write(key + '\n')

                with open("temp/" + filename.replace(".csv", "_list.csv"), 'w') as file:
                    for row in data:
                        key = row[4] + '_' + row[5]
                        file.write(key + '\n')
