import bluetooth
import csv
from typing import List
import requests
import pytz
from datetime import datetime
import os
import time
import ftplib


def discover_mac(device_id: str, timestamp: int, online_status: int, source: str):
    """
    Collect MAC address from nearby devices
    """

    print('Discovering MAC addresses')
    nearby_devices = bluetooth.discover_devices()

    if nearby_devices is None:
        return None

    data = []
    for address in nearby_devices:
        data.append([str(device_id), str(timestamp), str(online_status), str(address), str(source)])

    print(str(len(nearby_devices)) + ' MAC addresses detected')
    return data


def generate_file_path(device_id: str, timestamp: int, file_directory: str = None):
    """
    Generate the file path based on deviceID, timestamp and file directory.
    """

    date_time = datetime.fromtimestamp(timestamp)
    file_name = str(device_id) + '_' + str(date_time.year) + str(date_time.month) + str(date_time.day) + '.csv'
    file_path = os.path.join(file_directory, file_name) if file_directory else file_name
    return file_path


def write_to_file(data: List[List[str]], file_path: str) -> int:
    """
    Write the data received to a file
    """

    last_entry_number = __check_last_entry_number(file_path)

    print('writing entries...')

    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        i = 0
        for i, row in enumerate(data):
            row.insert(0, str(last_entry_number + i + 1))
            writer.writerow(row)

    print(str(i + 1) + ' Entries written')
    return 1


def write_to_ftp(host: str, port: int, user_name: str, password: str, ftp_file_path: str, local_file_path) -> int:
    """
    Write the target csv file to the FTP server
    """

    print('Writing to FTP server...')

    with ftplib.FTP() as ftp:
        ftp.connect(host, port)
        ftp.login(user_name, password)

        # Open the file for appending in binary mode
        stor_cmd = 'STOR ' + os.path.basename(ftp_file_path)
        with open(local_file_path, 'rb') as local_csv_file:
            ftp.storbinary(stor_cmd, local_csv_file)

    print('File successfully appended to FTP server!')
    return 1


def __check_last_entry_number(file_path) -> int:
    """
    Check the last entry number in the file
    """

    try:
        with open(file_path, 'r', newline='') as file:
            reader = csv.reader(file)
            return int(list(reader)[-1][0])
    except:
        return 0


def collect_data(device_id: str, timestamp: int, online_status: int, source: str, delay_time: int = 5,
                 batch_size: int = 4):
    """
    Collect data on periodic basis
    """

    print(str(timestamp) + ' : Collecting data...')

    data_batch = []
    for i in range(batch_size):
        print('Collecting batch' + str(i))
        data = discover_mac(device_id, timestamp, synced, source)
        if data is not None:
            data_batch.extend(data)
        time.sleep(delay_time)
    print(str(len(data_batch)) + ' entries collected')

    print('Sanitizing data...')
    sanitized_data = remove_duplicate(data_batch, 3)
    print(str(len(sanitized_data)) + ' sanitized entries collected')
    return sanitized_data


def remove_duplicate(data: List[List[str]], column: int):
    """
    Remove duplicate data in a column of matrix
    """

    print('Removing duplicate data...')
    sanitized_data = []
    found = []
    for row in data:
        if row[column] not in found:
            sanitized_data.append(row)
            found.append(row[column])

    return sanitized_data


def get_time():
    """
    Returns unix time and reports true if time is fetched from online source
    """

    print('Requesting time...')
    try:
        response = requests.get("http://worldtimeapi.org/api/wet")
        data = response.json()
        time = data['utc_datetime']
        timestr = time[:time.find(".")].replace("T", " ")
        synced = True
    except:
        time = pytz.timezone('UTC').normalize(datetime.now().astimezone(pytz.timezone('UTC')))
        timestr = str(time)[:str(time).find(".")]
        synced = False

    stylized = int(datetime.strptime(timestr, '%Y-%m-%d %H:%M:%S').timestamp())
    return stylized, synced


if __name__ == '__main__':
    device_id = 'RaspberryPi3'
    source = 'BT'
    delay_time = 5
    batch_size = 4
    directory = os.path.expanduser("~") + '/Desktop'

    ftp_host = 'caffeinelibrary.ca'
    ftp_port = 3301
    ftp_username = 'jerry'
    ftp_password = 'jerry'

    while True:
        timestamp, synced = get_time()
        data = collect_data(device_id, timestamp, synced, source, delay_time, batch_size)
        file_path = generate_file_path(device_id, timestamp, directory)
        write_to_file(data, file_path)
        try:
            write_to_ftp(ftp_host, ftp_port, ftp_username, ftp_password, file_path, file_path)
