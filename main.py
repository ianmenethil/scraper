# Flow 1 is not coded.
import logging
import sys
import time

from selenium import webdriver

import userInputs
from config import check_config_changes, load_config
from navigator import Navigator

logging.basicConfig(filename='logs/scraper.log', level=logging.INFO, encoding='utf-8',
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filemode='w')
console = logging.StreamHandler()
console.setLevel(level=logging.INFO)
logging.getLogger('').addHandler(console)


def main(driver):
    logging.info('Main function started')
    try:
        config = load_config('config.yaml')
    except ValueError as e:
        logging.error(msg=f"An error occurred while loading configuration: {e}")
        sys.exit(1)

    nav = Navigator(driver=driver)
    choice = None
    time.sleep(1)
    while True:
        try:
            if not choice:
                choice = userInputs.get_choice()
            if choice == '2':
                logging.info('fn_main: Flow2')
                should_exit, wait_time, choice = userInputs.inputs_Flow2()
                nav.navigate_barracudaLogin(config['BARRACUDA_USERNAME'], config['BARRACUDA_PASSWORD'],
                                            config['BARRACUDA_URL'])
                nav.navigate_acceptTerms()
                should_exit = startGetData(nav, wait_time, choice)
            if should_exit:
                break
        except Exception as e:
            logging.error(msg=f"An error occurred on main(): {e}")
            break


def startGetData(nav, wait_time, choice):
    logging.info('fn_startGetData() BEGIN')
    if choice == "1":
        should_exit = getDataManually(nav)
    elif choice == "2":
        should_exit = getDataAutomatically(nav, wait_time)
    return should_exit


def getDataManually(nav):
    while True:
        table = nav.navigate_setupQEPageDetails()
        rescan_choice = input("Enter '1' to get new data or '2' to exit: ")
        logging.info(f"User entered: {rescan_choice}")
        if rescan_choice == "2":
            return True
    return False


def getDataAutomatically(nav, wait_time):
    while True:
        logging.info('startGetData: [Flow2] getting getNewData_callDuplicates()')
        nav.navigate_setupQEPageDetails()

        for minute in range(wait_time // 60):
            logging.info(f"Sleep time | Total left: {wait_time//60 - minute} minutes.")
            time.sleep(60)
    return False


if __name__ == '__main__':
    chrome_options = webdriver.ChromeOptions()
    # chrome_driver_path = "C:\\binaries\\chrome-win32\\chromedriver.exe"
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": "D:\\0.Code\\1.Scripts\\python\\barracuda\\scraper\\data",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True})
    driver = webdriver.Chrome(options=chrome_options)

    main(driver)
