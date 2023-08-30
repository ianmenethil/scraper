import sys
import time
from selenium import webdriver
from navigator import Navigator
from configs_setup import MAIN_CONFIG_FILE, load_config, setup_logger
import mailer
S = time.sleep

logger = setup_logger('getMainLogger', "logs/main.log")

def start_get_data_auto(nav, wait_time):
    logger.info('Setting up Message Logs table')
    nav.setup_messagelogs_table()
    logger.info("About to call mailer script.")
    try:
        mailer.main(interactive=False, once=True)
        logger.info("Mailer script called successfully.")
    except Exception as except_err:  # ignore pylint: disable=broad-except
        logger.error("Failed to call mailer script: %s", except_err)
    for minute in range(wait_time // 60):
        logger.info("Sleep time | Total left: %s minutes.", wait_time // 60 - minute)
        S(60)

def load_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    # CHROME_DRIVER_PATH = ""
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": "D:\\_code\\_menethil\\_brcd\\scraper\\data",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True})
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    chrome_options.add_argument("--disable-usb")
    chrome_options.add_argument("--log-level=3")
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    return webdriver.Chrome(options=chrome_options)

def get_timer_from_user():
    default_wait_time = 1200  # 20 minutes
    wait_time = input("""Press enter to use the default timer(20 minutes) or enter a new timer in minutes: """)
    wait_time = default_wait_time if wait_time == "" else int(wait_time) * 60
    return wait_time

def go_to_barracuda(nav, wait_time):
    logger.info("Navigating to Barracuda main screen")
    nav.brcd_main_screen()
    S(2)
    logger.info("Navigating to Message Log screen")
    start_get_data_auto(nav, wait_time)
    S(1)

def main(web_driver):
    logger.info('Main function started')
    try:
        config = load_config(MAIN_CONFIG_FILE)
        wait_time = get_timer_from_user()
    except ValueError as error:
        logger.error("An error occurred while loading configuration: %s", error)
        sys.exit(1)
    nav = Navigator(driver=web_driver)
    logger.info("Navigator started: Logging in to Barracuda")
    nav.barracuda_login_screen(config['BARRACUDA_USERNAME'], config['BARRACUDA_PASSWORD'], config['BARRACUDA_URL'])
    S(2)
    while True:
        try:
            logger.info("Starting main loop")
            go_to_barracuda(nav, wait_time)
        except ValueError as error:
            logger.error("An error occurred on main(): %s", error)
            break
        except Exception as e_except:  # ignore pylint: disable=broad-except
            logger.error("Unexpected error occurred in main(): %s", e_except)
            break

if __name__ == '__main__':
    driver = load_chrome_driver()
    main(driver)
