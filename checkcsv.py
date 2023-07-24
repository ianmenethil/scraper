import csv
import logging
import os
import re
import traceback

data_directory = 'D:\\0.Code\\1.Scripts\\python\\barracuda\\scr\\data'
UNWANTED_CHARS = ['\u0251', '\u2009']
UNWANTED_BYTES = [b'\x8f', b'\ufffd']

def fnCheckCC(df):
    try:
        df['Subject'] = df['Subject'].astype(str).apply(obfuscate_cc)
    except Exception as e:
        print(f"An error occurred in fnCheckCC: {e}")
        raise
    return df


def obfuscate_cc(ccData):
    patterns = [ r"(?<!\d)\d{4}-\d{4}(\d{7})(?!\d)",
        r"(?<!\d)(\d{4}-\d{2})(\d{3}-\d{2})(\d{4})(?!\d)",
        r"(?<=PM\d{3}\s)(\d{1}\s\d{4}\s\d{2}\s\d{2})(?=\s\d{4})",
        r"(?<=PN\d{4}\s)(\d{4}\s\d{4}\s\d{4})(?=\s\d{3})",
        r"(Number\s{0,1}:?\s{0,1})(\d{1,5}[-\s]?\d{1,5}[-\s]?\d{1,5}[-\s]?\d{1,5}[-\s]?\d{1,5})(?!\d)",
        r"(PN\s{0,1}:?\s{0,1})(\d{1,5}[-\s]?\d{1,5}[-\s]?\d{1,5}[-\s]?\d{1,5}[-\s]?\d{1,5})(?!\d)",
        r"(?<!\d)4(\d{3}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4})(?!\d)",
        r"(?<!\d)5[1-5](\d{2}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4})(?!\d)",
        r"(?<!\d)3[47](\d{2}[-\s]?\d{6}[-\s]?\d{5})(?!\d)",
        #this
        r"(?<!\d)(\d{4}-\d{2})(\d{3}-\d{2})(\d{4})(?!\d),"]
    for pattern in patterns:
        ccData = re.sub(pattern, lambda m: m.group(0)[:4] + " XXXX XXXX " + m.group(0)[-4:], ccData)
    return ccData

def fnFindCSVFiles(directory):
    logging.info(msg=f"[def fnFindCSVFiles(directory):]Finding CSV files in {directory}")
    return [file for file in os.listdir(directory) if file.endswith('.csv') and file != 'main.csv']

def fnReadCSVData(file_path):
    try:
        logging.info(msg=f"[def fnReadCSVData(file_path):]Reading data from {file_path}")
        with open(file_path, mode='r', encoding='utf-8', errors='replace') as file:
            reader = csv.reader(file)
            print(f'Reading from file: {file_path}')  # Add this line

            # Check that reader is not empty
            try:
                headers = next(reader)
            except StopIteration:
                logging.error(f"CSV file is empty: {file_path}")
                return ([], [])

            data = list(reader)
        return (headers, data)
    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}\n{traceback.format_exc()}")  # Include traceback in error message
        return ([], [])

def fnMergeData(main_file_path, new_file_path):
    try:
        logging.info(f"Start merging data from {new_file_path} to {main_file_path}")
        headers1, data1 = fnReadCSVData(main_file_path)
        headers2, data2 = fnReadCSVData(new_file_path)

        # Check that 'Message ID' is in headers
        if 'Message ID' not in headers1 or 'Message ID' not in headers2:
            logging.error("'Message ID' not in headers")
            return

        message_id_index1 = headers1.index('Message ID')
        message_id_index2 = headers2.index('Message ID')
        existing_message_ids = set(row[message_id_index1] for row in data1)
        unique_data = [row for row in data2 if row[message_id_index2] not in existing_message_ids]
        unique_data = [row + [0] for row in unique_data]
        merged_data = data1 + unique_data
        with open(main_file_path, 'w', newline='', encoding='utf-8') as csvfile:  # Add encoding='utf-8'
            writer = csv.writer(csvfile)
            writer.writerow(headers1)
            writer.writerows(merged_data)
            logging.info(f"Finished merging data to {main_file_path}")
        os.remove(new_file_path)
    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}\n{traceback.format_exc()}")  # Include traceback in error message


def find_chars_in_csv(file_path, char1, char2):
    print(f"[def find_chars_in_csv(file_path, char1, char2):]Checking for characters in {file_path}")
    with open(file_path, mode='r', encoding='utf-8', errors='replace') as file:
        for i, line in enumerate(file, start=1):
            if i % 1000 == 0:
                print(f"Processing line {i}")
            if char1 in line or char2 in line:
                raise Exception(f"Character {char1} or {char2} found in line {i} of file {file_path}:\n{line}")


def find_byte_in_csv(file_path, byte):
    with open(file_path, mode='rb') as file:  # Open the file in binary mode
        for i, line in enumerate(iterable=file, start=1):
            if i % 1000 == 0:
                print(f"Processing line {i}")
            if byte in line:
                raise Exception(f"Byte {byte} found in line {i} of file {file_path}:\n{line.decode(errors='replace')}")

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

csv_files = fnFindCSVFiles(data_directory)
main_file = os.path.join(data_directory, 'main.csv')

for file in csv_files:
    file_path = os.path.join(data_directory, file)
    try:
        remove_unwanted_bytes(file_path, UNWANTED_BYTES)
        remove_unwanted_chars(file_path, UNWANTED_CHARS)
                # Run the check functions for each CSV file
        for char in UNWANTED_CHARS:
            find_chars_in_csv(file_path, char, char)
        for byte in UNWANTED_BYTES:
            find_byte_in_csv(file_path, byte)

        fnMergeData(main_file, file_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")