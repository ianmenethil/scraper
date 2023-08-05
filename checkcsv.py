import csv
import logging
import os
import re
import traceback
import pandas as pd

# DATA_DIRECTORY = 'D:\\_code\\_menethil\\_brcd\\scraper\\data'
DATA_DIRECTORY = './data/'
MAIN_FILE = './data/main.csv'
FILE_EXTENSION = '.csv'
# MID = ['Message ID', '"Message ID"']
PATTERNS = [
            r"(?<!\d)\d{4}-\d{4}(\d{7})(?!\d)",
            r"(?<!\d)(\d{4}-\d{2})(\d{3}-\d{2})(\d{4})(?!\d)",
            r"(?<=PM\d{3}\s)(\d{1}\s\d{4}\s\d{2}\s\d{2})(?=\s\d{4})",
            r"(?<=PN\d{4}\s)(\d{4}\s\d{4}\s\d{4})(?=\s\d{3})",
            r"(Number\s{0,1}:?\s{0,1})(\d{1,5}[-\s]?\d{1,5}[-\s]?\d{1,5}[-\s]?\d{1,5}[-\s]?\d{1,5})(?!\d)",
            r"(PN\s{0,1}:?\s{0,1})(\d{1,5}[-\s]?\d{1,5}[-\s]?\d{1,5}[-\s]?\d{1,5}[-\s]?\d{1,5})(?!\d)",
            r"(?<!\d)4(\d{3}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4})(?!\d)",
            r"(?<!\d)5[1-5](\d{2}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4})(?!\d)",
            r"(?<!\d)3[47](\d{2}[-\s]?\d{6}[-\s]?\d{5})(?!\d)",
            r"(?<!\d)(\d{4}-\d{2})(\d{3}-\d{2})(\d{4})(?!\d),"]
UNWANTED_CHARS = ['\u0251', '\u2009']
UNWANTED_BYTES = [b'\\x8f', b'\\ufffd']

logging.basicConfig(
    filename="logs\\checkcsv.log",
    level=logging.DEBUG,
    encoding="utf-8",
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filemode="a",)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger("").addHandler(console)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)
pd.set_option("display.max_colwidth", 100)

def check_credit_card(df):
    try:
        df['Subject'] = df['Subject'].astype(str).apply(obfuscate_cc)
    except Exception as e_exception:
        logging.error("Unexpected error occurred:%s", {e_exception})
        raise
    return df

def obfuscate_cc(credit_card_data):
    for pattern in PATTERNS:
        credit_card_data = re.sub(pattern, lambda m: m.group(0)[:4] + " XXXX XXXX " + m.group(0)[-4:], credit_card_data)
    return credit_card_data

def find_csv_files():
    logging.info(msg=f"Finding CSV files in {DATA_DIRECTORY}")
    all_files = [file for file in os.listdir(DATA_DIRECTORY) if file.endswith(FILE_EXTENSION)]
    return [file for file in all_files if file != os.path.basename(MAIN_FILE)]

def read_data_from_csv(file_path):
    try:
        logging.info(msg=f"[def read_data_from_csv(file_path):]Reading data from {file_path}")
        with open(file_path, mode='r', encoding='utf-8', errors='replace') as file:
            reader = csv.reader(file)
            print(f'Reading from file: {file_path}')
            try:
                headers = next(reader)  # Check that reader is not empty
            except StopIteration:
                logging.error("CSV file is empty:%s,", file_path)
                return ([], [])
            data = list(reader)
        return (headers, data)
    except (FileNotFoundError, PermissionError) as e_exception:
        logging.error("Unexpected error occurred:%s,", e_exception)
        return ([], [])

def func_merge_data(main_file_path, new_file_path):
    try:
        logging.info("Start merging data from %s to %s", new_file_path, main_file_path)
        logging.info("Reading data from %s", main_file_path)
        logging.info("Reading data from %s", new_file_path)
        if not os.path.isfile(new_file_path):
            logging.error("File not found:%s", {new_file_path})
            return
        headers1, data1 = read_data_from_csv(main_file_path)
        headers2, data2 = read_data_from_csv(new_file_path)
        if 'Message ID' not in headers1 or 'Message ID' not in headers2:
            logging.error("'Message ID' not in headers")
            return
        message_id_index1 = headers1.index('Message ID')
        message_id_index2 = headers2.index('Message ID')

        # if MID not in headers1 or MID not in headers2:
        #     logging.error("%s not in headers", MID)
        #     return
        # message_id_index1 = headers1.index(MID)
        # message_id_index2 = headers2.index(MID)
        existing_message_ids = set(row[message_id_index1] for row in data1)
        unique_data = [row for row in data2 if row[message_id_index2] not in existing_message_ids]
        unique_data = [row + [0] for row in unique_data]
        merged_data = data1 + unique_data
        with open(main_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers1)
            writer.writerows(merged_data)
            logging.info("Finished merging data to %s", main_file_path)
        os.remove(new_file_path)
    except (FileNotFoundError, csv.Error) as e_exception:
        logging.error("Unexpected error occurred: %s\n%s", e_exception, traceback.format_exc())

def find_chars_in_csv(file_path, char1, char2):
    print(f"[def find_chars_in_csv(file_path, char1, char2):]Checking for characters in {file_path}")
    with open(file_path, mode='r', encoding='utf-8', errors='replace') as file:
        for i, line in enumerate(file, start=1):
            if i % 1000 == 0:
                print(f"Processing line {i}")
            if char1 in line or char2 in line:
                raise ValueError(f"Character {char1} or {char2} found in line {i} of file {file_path}:\n{line}")

def find_byte_in_csv(file_path, byte):
    with open(file_path, mode='rb') as file:
        for i, line in enumerate(iterable=file, start=1):
            if i % 1000 == 0:
                print(f"Processing line {i}")
            if byte in line:
                raise ValueError(f"Byte {byte} found in line {i} of file {file_path}:\n{line.decode(errors='replace')}")

def remove_unwanted_chars(file_path, chars, replacement=' '):
    with open(file_path, mode='r', encoding='utf-8', errors='replace') as file:
        lines = file.readlines()
    with open(file_path, mode='w', encoding='utf-8') as file:
        for line in lines:
            for char in chars:
                if char in line:
                    line = line.replace(char, replacement)
            file.write(line)

def remove_unwanted_bytes(file_path, bytes, replacement=b' '):
    with open(file_path, 'rb') as file:
        data = file.read()
    for byte in bytes:
        data = data.replace(byte, replacement)
    with open(file_path, 'wb') as file:
        file.write(data)

csv_files = find_csv_files()
os.path.join(DATA_DIRECTORY, MAIN_FILE)
for file in csv_files:
    file_path = os.path.join(DATA_DIRECTORY, file)
    try:
        remove_unwanted_bytes(file_path, UNWANTED_BYTES)
        remove_unwanted_chars(file_path, UNWANTED_CHARS)
        for char in UNWANTED_CHARS:
            find_chars_in_csv(file_path, char, char)
        for byte in UNWANTED_BYTES:
            find_byte_in_csv(file_path, byte)
        func_merge_data(MAIN_FILE, file_path)
    except FileNotFoundError as error:
        print(f"Error: {error}")
    except Exception as error:  # pylint: disable=broad-except
        print(f"Unexpected error occurred: {error}")
