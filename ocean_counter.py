from ftplib import FTP
from datetime import date
import json
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from counter_config import *
from setup import *



def get_data_from_ftp(ftp_dir, d_start, d_finish):
    FTP_SERVER, FTP_USER, FTP_PASS = setup()
    with FTP(FTP_SERVER) as ftp:
        ftp.login(FTP_USER, FTP_PASS)
        ftp.cwd(ftp_dir)
        files = ftp.nlst()
        filtered_files = []
        for file in files:
            if file[5:] >= d_start and file[5:] <= d_finish:
                filtered_files.append(file)
        # Получили список файлов для скачивания
        filtered_files.sort(key=lambda file: file[5:])

        #скачиваем файлы и считаем посетителей за день
        file_counts =[]
        for file in filtered_files:
            with open('_sensors.tmp', 'wb') as sf:
                ftp.retrbinary('RETR '+file, sf.write)
            with open('_sensors.tmp') as sf:
                count = 0
                for line in sf:
                    if len(line) == 1:
                        break
                    i = int(line.split(' ')[1])
                    count += i
            sensor = int(file[0:4])
            year_month_date = file[5:]
            file_counts.append([sensor, year_month_date, count])
    return file_counts


def get_by_month_counts(sensors, file_counts):
    floor_counts = {}
    for sensor, file, count in file_counts:
        year = int(file[0:4])
        month = int(file[5:7])
        if sensor in sensors:        # == 103 or sensor == 202:
            if year not in floor_counts:
                floor_counts[year] ={}
                floor_counts[year][month] = count
            else:
                if month not in floor_counts[year]:
                    floor_counts[year][month] = count
                else:
                    floor_counts[year][month] += count
    return floor_counts

def get_by_day_counts(sensors, file_counts):
    floor_counts = {}
    for sensor, file, count in file_counts:
        year = int(file[0:4])
        month = int(file[5:7])
        day = int(file[8:])
        if sensor in sensors:
            if year not in floor_counts:
                floor_counts[year] ={}
                if month not in floor_counts[year]:
                    floor_counts[year][month] = {}
                floor_counts[year][month][day] = count
            else:
                if month not in floor_counts[year]:
                    floor_counts[year][month] = {}
                    floor_counts[year][month][day] = count
                else:
                    if day not in floor_counts[year][month]:
                        floor_counts[year][month][day] = count
                    else:
                        floor_counts[year][month][day] += count
    return floor_counts


def plot_counts_1_floor(counts_y_1, counts_y_2):
    fig, ax = plt.subplots()
    ax.grid()
    ax.set_title("Посещаемость ОКЕАН (1 этаж)", fontsize=16)
    ax.set_xlabel("декабрь", fontsize=14)
    ax.set_ylabel("Посетители", fontsize=14)

    ax.tick_params(which='major', length=10, width=2)
    ax.tick_params(which='minor', length=5, width=1)
    plt.xlim(1, 31)
    plt.ylim(0, 15000)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))

    fig.set_figwidth(20)
    fig.set_figheight(10)

    i = 1
    x = []
    y1 = []
    y2 = []
    for month in counts_y_1:
        for day in counts_y_1[month]:
            x.append(i)
            c1 = counts_y_1[month][day]
            y1.append(c1)
            i += 1
    for month in counts_y_2:
        for day in counts_y_2[month]:
            c2 = counts_y_2[month][day]
            y2.append(c2)

    ax.plot(x, y1, 'o-', label = '2019')
    #x.append(i+1) #корректриовка на високосный год, если попадает февраль
    ax.plot(x, y2, 's-', label = '2020')

    ax.legend(loc="upper left")
    plt.show()


def plot_counts(counts, file_name):
    fig, ax = plt.subplots()
    ax.grid()
    ax.set_title("Посещаемость ОКЕАН", fontsize=16)
    ax.set_xlabel("март", fontsize=14)
    ax.set_ylabel("Посетители", fontsize=14)
    ax.tick_params(which='major', length=10, width=2)
    ax.tick_params(which='minor', length=5, width=1)
    plt.xlim(1, 30)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))

    fig.set_figwidth(20)
    fig.set_figheight(10)

    for year in counts:
        i = 0
        x = []
        y1 = []
        y2 = []
        y3 = []
        for month in counts[year]:
            for day in counts[year][month]:
                x.append(i)
                c1, c2, c3 = counts[year][month][day]
                y1.append(int(c1))
                y2.append(int(c2))
                y3.append(int(c3))
                i += 1

        ax.plot(x, y1, 'o-.', label = '1 этаж' +str(year))
        ax.plot(x, y2, 'x-.', label = '2 этаж' +str(year))
        ax.plot(x, y3, 's-.', label = '3 этаж' +str(year))

    ax.legend(loc="upper left")
    plt.show()

def first_floor_count():
    file_counts = get_data_from_ftp(FTP_DIR1, '2019-12-03', '2019-12-27')
    by_day_counts19 = get_by_day_counts(SENSORS[0], file_counts)

    file_counts = get_data_from_ftp(FTP_DIR1, '2020-12-01', '2020-12-25')
    by_day_counts20 = get_by_day_counts(SENSORS[0], file_counts)

    plot_counts_1_floor(by_day_counts19[2019], by_day_counts20[2020])

def third_floor_count():
    file_counts = get_data_from_ftp(FTP_DIR2, '2019-12-03', '2019-12-21')
    by_day_counts19 = get_by_day_counts(SENSORS[2], file_counts)

    file_counts = get_data_from_ftp(FTP_DIR2, '2020-12-01', '2020-12-19')
    by_day_counts20 = get_by_day_counts(SENSORS[2], file_counts)

    plot_counts_1_floor(by_day_counts19[2019], by_day_counts20[2020])


def read_counts_from_json(file_name):
    with open(file_name) as json_file:
        data_json = json.load(json_file)
    return data_json


def write_counts_to_json(data_json,file_name):
    with open(file_name, 'w') as json_file:
        string_json = json.dumps(data_json, indent=4)
        json_file.write(string_json)
        

def write_counter(file_name):
    file_counts = get_data_from_ftp(FTP_DIR1, '2020-01-01', '2020-12-18')
    by_day_counts = get_by_day_counts(SENSORS[0], file_counts)
    write_counts_to_json(by_day_counts,file_name)
    


def main(): 
#    write_counter('2020_1st_floor.json')

    first_floor_count()
#    third_floor_count()
#    init_date = date.today()
#    i_d = date(init_date.year, init_date.month, 1)
#    s = str(i_d)
#    print(s)

if __name__ == "__main__":
     main()
