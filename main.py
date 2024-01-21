import sys
import time as t
from datetime import datetime, time
from selenium import webdriver
from navigator import Navigator
from configs_setup import MAIN_CONFIG_FILE, load_config, setup_logger

import mailer

logger = setup_logger('getMainLogger', "logs/main.log")
end_of_day = time(17, 30, 0)
S = t.sleep


def start_get_data_auto(nav, wait_time, initial_run=True):
    logger.info("Checking if it is the first run of the day.")
    if initial_run:
        nav.setup_messagelogs_table()
        logger.info("First run of the day. Setting up Message Logs table.")
    else:
        logger.info("Not the first run of the day. Skipping setup. Going to search and export")
    logger.info("About to call search_and_export script.")
    nav.search_and_export()
    try:
        mailer.main(interactive=False, once=True)
        logger.info("Mailer script called successfully.")
    except Exception as except_err:
        logger.error("Failed to call mailer script: %s", except_err)
    try:
        total_minutes = wait_time // 60
        for minute in range(0, total_minutes, 5):
            logger.info("Next run in %s minutes.", total_minutes - minute)
            S(300)  # Sleep for 5 minutes
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt detected. Attempting to close resources gracefully.")
        try:
            driver.quit()
            nav.driver.quit()
        except Exception as exception_error:  # ignore pylint: disable=broad-except
            logger.error("Error while quitting the driver: %s", exception_error)
        sys.exit(0)


def load_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    # CHROME_DRIVER_PATH = ""
    chrome_options.add_experimental_option(
        "prefs", {
            "download.default_directory": "F:\\_Python\\__Zenith\\_barracuda\\scraper\\data",
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    chrome_options.add_argument("--disable-usb")
    # chrome_options.add_argument("--log-level=3")
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    logger.info("Starting Chrome driver with options: %s", chrome_options.arguments)
    return webdriver.Chrome(options=chrome_options)


def get_timer_from_user():
    default_wait_time = 1200  # 20 minutes
    wait_time = input("Press enter to use the default timer(20 minutes) or enter a new timer in minutes: ")
    try:
        wait_time = int(wait_time) * 60
    except ValueError:
        wait_time = default_wait_time
        logger.info("User entered nothing or invalid input. Using default wait time: %s", wait_time)
    return wait_time


def goto_barracuda_messagelogs_screen(nav):
    logger.debug("Starting goto_barracuda_messagelogs_screen() function.")
    nav.messagelogs_screen()
    S(2)


def get_data(nav, wait_time):
    logger.debug("Starting get_data() function.")
    start_get_data_auto(nav, wait_time)
    S(1)


def main(web_driver):
    logger.debug('Starting main() function.')
    try:
        config = load_config(MAIN_CONFIG_FILE)
        wait_time = get_timer_from_user()
    except ValueError as va_error:
        logger.error("An error occurred while loading configuration: %s", va_error)
        sys.exit(1)
    nav = Navigator(driver=web_driver)
    logger.info("Navigator started: Logging in to Barracuda")
    nav.barracuda_login_screen(config['BARRACUDA_USERNAME'], config['BARRACUDA_PASSWORD'], config['BARRACUDA_URL'])
    S(2)
    goto_barracuda_messagelogs_screen(nav)
    while True:
        current_time = datetime.now().time()
        logger.info("Current time: %s, | End of day is set as: %s | Script will stop automatically at %s", current_time, end_of_day, end_of_day)
        if current_time >= end_of_day:
            logger.info("Ending script, people have gone home...")
            driver.quit()
            sys.exit(0)
        try:
            get_data(nav, wait_time)
        except ValueError as va_error:
            logger.error("An error occurred on main(): %s", va_error)
            break
        except Exception as exception_error:
            logger.error("Unexpected error occurred in main(): %s", exception_error)
            break


if __name__ == '__main__':
    driver = load_chrome_driver()
    main(driver)
