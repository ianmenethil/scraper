# import logging
import sys
import time
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from configs_setup import setup_logger
S = time.sleep
logger = setup_logger('getNavigatorLogger', "logs/main.log")

class Navigator:
    def __init__(self, driver):
        self.driver = driver

    def barracuda_login_screen(self, barracuda_username, barracuda_password, barracuda_url):
        # sourcery skip: class-extract-method, extract-duplicate-method
        logger.info("Barracuda login screen")
        self.driver.get(barracuda_url)
        S(1)
        try:
            username_field = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.ID, "username")))
            S(1)
            username_field.send_keys(barracuda_username)
            logger.info('Username entered')
            S(1)
            next_button = self.driver.find_element(By.ID, "submit")
            next_button.click()
            S(1)
        except TimeoutException:
            logger.error("Reached timeout exception block")
            username_field = input("Element not found. Press 'Enter' to try again or enter 'exit' to quit: ")
            logger.error("User entered: %s", {username_field})
            if username_field.lower() == 'exit':
                sys.exit()
        try:
            password_field = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.ID, "password")))
            S(1)
            password_field.send_keys(barracuda_password)
            logger.info('Password entered')
            S(1)
            signin_button = self.driver.find_element(By.ID, "submit")
            signin_button.click()
            S(5)
        except TimeoutException:
            logger.error("Reached timeout exception block")
            password_field = input("password_field Element not found. Press 'Enter' to continue manually or enter 'exit' to quit: ")
            logger.error("User entered: %s", {password_field})
            if password_field.lower() == 'exit':
                sys.exit()
        try:
            tick_checkbox = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.ID, "KmsiCheckboxField")))
            tick_checkbox.click()
            S(1)
            yes_button = self.driver.find_element(By.ID, "idSIButton9")
            yes_button.click()
            logger.info("Checkbox done")
            S(5)
        except TimeoutException:
            logger.error("Checkbox Element not found within the given time. Skipping this step.")
        logger.info("Barracuda Page")

    def brcd_main_screen(self):
        logger.info("https://ess.barracudanetworks.com/log")
        self.driver.get("https://ess.barracudanetworks.com/log")
        S(5)
        try:
            logger.info(msg="Looking for accept cookies via Id: onetrust-accept-btn-handler")
            accept_cookies = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler")))
            self.driver.execute_script("arguments[0].scrollIntoView();", accept_cookies)
            try:
                accept_cookies.click()
                logger.info(msg="Cookie accepted via Selenium click.")
            except WebDriverException:
                try:
                    self.driver.execute_script("arguments[0].click();", accept_cookies)
                    logger.info("Cookie accepted via JavaScript click.")
                except Exception as e_except:  # pylint: disable=broad-except
                    logger.error("Failed to click the cookie button: %s", {e_except})
        except TimeoutException:
            logger.error("Accept cookies button not found within 10 seconds. Continuing without accepting cookies.")
            S(3)
        try:
            logger.info("Looking for Message Logs Button")
            message_logs_button = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.LINK_TEXT, "Message Log")))
            logger.info('message_logs_button found')
            for _ in range(5):
                try:
                    message_logs_button.click()
                    break
                except WebDriverException:
                    logger.error(msg="WebDriverException: Element is not clickable at point (x, y). Trying again.")
                    S(2)
        except TimeoutException:
            logger.error(msg="Message Log button not found within 10 seconds.")
            S(5)

    # def setup_dropdown_values(self, wait, element_name, value):
    #     dropdown_element = wait.until(EC.presence_of_element_located((By.ID, element_name)))
    #     dropdown = Select(dropdown_element)
    #     dropdown.select_by_visible_text(value)

    def setup_dropdown_values(self, wait, element_name, value):
        dropdown_element = wait.until(EC.visibility_of_element_located((By.ID, element_name)))
        dropdown = Select(dropdown_element)
        dropdown.select_by_visible_text(value)

    def setup_messagelogs_table(self):  # sourcery skip: extract-duplicate-method
        try:
            from_header = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "td.from")))
            from_header.click()
            S(1)
            emaildisplay_dropdown_option = WebDriverWait(self.driver, 60).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "li[data-menu-item-value='both']")))
            emaildisplay_dropdown_option.click()
            logger.info("Email Display: Both selected")
            S(5)
            domain_dropdown_option = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.ID, "domain_id_select")))
            domain_dropdown_option_select = Select(domain_dropdown_option)
            domain_dropdown_option_select.select_by_visible_text("All domains")
            S(1)
            advancedsearch_dropdown_option = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.ID, "log-advanced-search-toggle")))
            advancedsearch_dropdown_option.click()
            S(2)
            limit_dropdown_option = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.ID, "limit")))
            limit_dropdown_option_select = Select(limit_dropdown_option)
            limit_dropdown_option_select.select_by_visible_text("200")
            S(2)
            wait = WebDriverWait(self.driver, 60)
            self.setup_dropdown_values(wait, "domain_id_select", "All domains")
            logger.info('Domains: All domains')
            S(1)
            self.setup_dropdown_values(wait, "search_action", "Quarantined")
            logger.info('Email Status: Quarantined')
            S(1)
            self.setup_dropdown_values(wait, "limit", "200")
            logger.info('Table Limit: 200')
            S(1)
            self.setup_dropdown_values(wait, "search_range_select", "1 day")
            logger.info('Date Range: 1 day')
            S(1)
            self.setup_dropdown_values(wait, "search_delivery_status", "Not Delivered")
            logger.info('Delivery Status: Not Delivered')
            S(1)
            search_button = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.ID, "search-btn")))
            logger.info("Search button clicked. Waiting for table data to load.")
            search_button.click()
            S(5)
            checkbox_td = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'td.details')))
            checkbox = checkbox_td.find_element(By.XPATH, './/input[@type="checkbox"]')
            logger.info("Select All tick box clicked")
            checkbox.click()
            S(2)
            export_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div#log-bd div#log-main form#log-form div#log-main-tb div.toolbar span.button-group button[value="export"]')))
            S(1)
            logger.info('Export clicked, waiting for download to complete.')
            export_button.click()
            S(3)
        except TimeoutException:
            logger.info("setup_messagelogs_table() TimeoutException")
