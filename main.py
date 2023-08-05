import logging
import sys
import time
from selenium import webdriver
from navigator import Navigator
import _menethil._brcd.scraper.user_inputs as user_inputs
from _menethil._brcd.scraper.configs_setup import load_config
S = time.sleep

logging.basicConfig(filename='logs/scraper.log',
                    level=logging.INFO, encoding='utf-8',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filemode='w')
console = logging.StreamHandler()
console.setLevel(level=logging.INFO)
logging.getLogger('').addHandler(console)

def main(web_driver):
    logging.info('Main function started')
    try:
        config = load_config('config.yaml')
    except ValueError as error:
        logging.error(msg=f"An error occurred while loading configuration: {error}")
        sys.exit(1)
    nav = Navigator(driver=web_driver)
    choice = None
    S(1)
    while True:
        try:
            if not choice:
                choice = user_inputs.get_choice()
            if choice == '2':
                logging.info('fn_main: Flow2')
                wait_time, choice = user_inputs.auto_flow()
                nav.scr_brcd_login_screen(config['BARRACUDA_USERNAME'],
                                          config['BARRACUDA_PASSWORD'],
                                          config['BARRACUDA_URL'])
                nav.brcd_main_screen()
                start_get_data(nav, wait_time, choice)
        except ValueError as error:
            logging.error("An error occurred on main():%s", error)
            break

def start_get_data(nav, wait_time, choice):
    logging.info('fn_start_get_data() BEGIN')
    if choice == "2":
        start_get_data_auto(nav, wait_time)
    else:
        logging.error("Invalid choice.")
        # should_exit = True
    # return should_exit
    return None

def start_get_data_auto(nav, wait_time):
    while True:
        logging.info('start_get_data: [Flow2] getting getNewData_callDuplicates()')
        nav.navigate_setupQEPageDetails()
        for minute in range(wait_time // 60):
            logging.info("Sleep time | Total left: %s minutes.", wait_time//60 - minute)
            S(60)
    return False

if __name__ == '__main__':
    chrome_options = webdriver.ChromeOptions()
    CHROME_DRIVER_PATH = "D:\\_code\\_binaries\\chrome-win32\\chromedriver.exe"
    # chrome_options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" # for windows
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": "D:\\_code\\_menethil\\_brcd\\scraper\\data",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True})
    driver = webdriver.Chrome(options=chrome_options)
    main(driver)