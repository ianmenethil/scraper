import logging
import sys
import time
from selenium import webdriver
from navigator import Navigator
from configs_setup import CONFIG_FILE, load_config
S = time.sleep

logger = logging.getLogger('getMainLogger')
logger.setLevel(logging.DEBUG)
# File handler
file_handler = logging.FileHandler("logs/mailer.log", mode="w", encoding="utf-8")
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

def start_get_data_auto(nav, wait_time):
    while True:
        logger.info('start_get_data_auto')
        nav.setup_messagelogs_table()
        for minute in range(wait_time // 60):
            logger.info("Sleep time | Total left: %s minutes.", wait_time//60 - minute)
            S(60)
    # return False

def load_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    # CHROME_DRIVER_PATH = "D:\\_code\\_binaries\\chrome-win32\\chromedriver.exe"
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": "D:\\_code\\_menethil\\_brcd\\scraper\\data",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True})
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    chrome_options.add_argument("--disable-usb")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    return webdriver.Chrome(options=chrome_options)

def auto_flow():
    default_wait_time = 1200  # 20 minutes
    wait_time = input("""Press enter to use the default timer(20 minutes) or enter a new timer in minutes: """)
    wait_time = default_wait_time if wait_time == "" else int(wait_time) * 60
    return wait_time

def main(web_driver):
    """Main function to start the automation process."""
    logging.info('Main function started')
    try:
        config = load_config(CONFIG_FILE)
    except ValueError as error:
        logging.error("An error occurred while loading configuration: %s", error)
        sys.exit(1)
    nav = Navigator(driver=web_driver)
    while True:
        try:
            wait_time = auto_flow()
            S(3)
            nav.scr_brcd_login_screen(config['BARRACUDA_USERNAME'], config['BARRACUDA_PASSWORD'], config['BARRACUDA_URL'])
            S(2)
            nav.brcd_main_screen()
            S(2)
            start_get_data_auto(nav, wait_time)
            S(1)
        except ValueError as error:
            logging.error("An error occurred on main(): %s", error)
            break
        except Exception as e_except:  # ignore pylint: disable=broad-except
            logging.error("Unexpected error occurred in main(): %s", e_except)
            break

if __name__ == '__main__':
    driver = load_chrome_driver()
    main(driver)
