import csv
import logging
import os
import re
import traceback

# Constants
DATA_DIRECTORY = './data/'
MAIN_FILE = './data/main.csv'
FILE_EXTENSION = '.csv'
CREDIT_CARD_PATTERNS = [
            r"(?<!\d)4(\d{3}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4})(?!\d)",  # visa
            r"(?<!\d)5[1-5](\d{2}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4})(?!\d)",  # mc
            r"(?<!\d)3[47](\d{2}[-\s]?\d{6}[-\s]?\d{5})(?!\d)",  # amex
            r"(?:\D|^)(5[1-5][0-9]{2}(?:\ |\-|)[0-9]{4}(?:\ |\-|)[0-9]{4}(?:\ |\-|)[0-9]{4})(?:\D|$)",  # mc
            r"(?:\D|^)(4[0-9]{3}(?:\ |\-|)[0-9]{4}(?:\ |\-|)[0-9]{4}(?:\ |\-|)[0-9]{4})(?:\D|$)",  # visa
            r"(?:\D|^)((?:34|37)[0-9]{2}(?:\ |\-|)[0-9]{6}(?:\ |\-|)[0-9]{5})(?:\D|$)",
            r"([^0-9-]|^)(3(4[0-9]{2}|7[0-9]{2})( |-|)[0-9]{6}( |-|)[0-9]{5})([^0-9-]|$)",  # amex
            r"([^0-9-]|^)(4[0-9]{3}( |-|)([0-9]{4})( |-|)([0-9]{4})( |-|)([0-9]{4}))([^0-9-]|$)",
            r"([^0-9-]|^)(5[0-9]{3}( |-|)([0-9]{4})( |-|)([0-9]{4})( |-|)([0-9]{4}))([^0-9-]|$)"]
UNWANTED_CHARS = ['\u0251', '\u2009']
UNWANTED_BYTES = [b'\\x8f', b'\\ufffd']

logger = logging.getLogger('getCheckcsvLogger')
logger.setLevel(logging.DEBUG)
# File handler
file_handler = logging.FileHandler("logs/checkcsv.log", mode="w", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(file_format)
logger.addHandler(file_handler)
# Console handler
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
console.setFormatter(console_format)
logger.addHandler(console)

class CSVHandler:
    @staticmethod
    def read_data_from_csv(file_path):
        # sourcery skip: remove-unnecessary-else, use-named-expression
        try:
            logger.info("Reading data from %s", {file_path})
            with open(file_path, mode='r', encoding='utf-8', errors='replace') as file:
                reader = csv.reader(file)
                headers = next(reader, None)
                if headers:
                    return headers, list(reader)
                else:
                    logger.error("CSV file is empty: %s", {file_path})
                    return [], []
        except (FileNotFoundError, PermissionError) as error:
            logger.error("Unexpected error occurred: %s", {error})
            return [], []

    @staticmethod
    def find_chars_in_csv(file_path, *chars):
        logger.info("Checking for characters in %s", {file_path})
        with open(file_path, mode='r', encoding='utf-8', errors='replace') as file:
            for i, line in enumerate(file, start=1):
                for char in chars:
                    if char in line:
                        raise ValueError(f"Character {char} found in line {i} of file {file_path}:\n{line}")

    @staticmethod
    def find_byte_in_csv(file_path, byte_to_find):
        with open(file_path, mode='rb') as file:
            for i, line in enumerate(file, start=1):
                if byte_to_find in line:
                    raise ValueError(f"Byte {byte_to_find} found in line {i} of file {file_path}:\n{line.decode(errors='replace')}")

    @staticmethod
    def remove_unwanted_chars(file_path, chars_to_remove, replacement=' '):
        with open(file_path, mode='r', encoding='utf-8', errors='replace') as file:
            lines = [line.replace(char, replacement) for char in chars_to_remove for line in file.readlines()]
        with open(file_path, mode='w', encoding='utf-8') as file:
            file.writelines(lines)

    @staticmethod
    def remove_unwanted_bytes(file_path, bytes_to_remove, replacement=b' '):
        with open(file_path, 'rb') as file:
            data = file.read()
            for byte in bytes_to_remove:
                data = data.replace(byte, replacement)
        with open(file_path, 'wb') as file:
            file.write(data)

def merge_data(main_file_path, new_file_path):
    """
    Merges data from the new_file into the main_file based on unique 'Message ID'.
    Once merged, the new_file is deleted.
    """
    try:
        if not os.path.isfile(new_file_path):
            logger.error("File not found: %s", new_file_path)
            return
        headers1, data1 = CSVHandler.read_data_from_csv(main_file_path)
        headers2, data2 = CSVHandler.read_data_from_csv(new_file_path)
        if 'Message ID' not in headers1 or 'Message ID' not in headers2:
            logger.error("'Message ID' not in headers")
            return
        message_id_index1 = headers1.index('Message ID')
        message_id_index2 = headers2.index('Message ID')
        existing_message_ids = {row[message_id_index1] for row in data1}
        unique_data = [row for row in data2 if row[message_id_index2] not in existing_message_ids]
        unique_data = [row + [0] for row in unique_data]
        merged_data = data1 + unique_data
        with open(main_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers1)
            writer.writerows(merged_data)
            logger.info("Finished merging data to %s", main_file_path)
        os.remove(new_file_path)
    except (FileNotFoundError, csv.Error) as e_exception:
        logger.error("Unexpected error occurred: %s\n%s", e_exception, traceback.format_exc())

def obfuscate_cc(credit_card_data):
    for pattern in CREDIT_CARD_PATTERNS:
        credit_card_data = re.sub(pattern, lambda m: f"{m.group(0)[:4]} XXXX XXXX {m.group(0)[-4:]}", credit_card_data)
        # credit_card_data = re.sub(pattern, lambda m: m.group(0)[:4] + " XXXX XXXX " + m.group(0)[-4:], credit_card_data)
    return credit_card_data

def find_csv_files(directory, main_file):
    all_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith(FILE_EXTENSION)]
    return [file for file in all_files if file != main_file]

def check_credit_card(data_frame):
    """Obfuscates credit card details in the 'Subject' column of a dataframe."""
    try:
        data_frame['Subject'] = data_frame['Subject'].astype(str).apply(obfuscate_cc)
    except Exception as e_exception:
        logger.error("Unexpected error occurred: %s", {e_exception})
        raise
    return data_frame

def main():
    csv_files = find_csv_files(DATA_DIRECTORY, MAIN_FILE)
    for file_path in csv_files:
        try:
            CSVHandler.remove_unwanted_bytes(file_path, UNWANTED_BYTES)
            CSVHandler.remove_unwanted_chars(file_path, UNWANTED_CHARS)
            CSVHandler.find_chars_in_csv(file_path, *UNWANTED_CHARS)
            for byte in UNWANTED_BYTES:
                CSVHandler.find_byte_in_csv(file_path, byte)
            merge_data(MAIN_FILE, file_path)
        except FileNotFoundError as error:
            logger.error("Error: %s", error)
        except Exception as error:
            logger.error("Unexpected error occurred: %s", error)

if __name__ == "__main__":
    main()
