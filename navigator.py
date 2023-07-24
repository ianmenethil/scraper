import logging
import sys
import time

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait


class Navigator:
    def __init__(self, driver):
        self.driver = driver

    def navigate_barracudaLogin(self, barracuda_username, barracuda_password, barracuda_url):
        logging.info('fn_navigate_barracudaLogin() BEGIN')
        self.driver.get(barracuda_url)
        time.sleep(1)
        try:
            unInput1 = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.ID, "username")))
            time.sleep(1)
            unInput1.send_keys(barracuda_username)
            logging.info('Username entered')
            time.sleep(1)
            buttonNextButton1 = self.driver.find_element(By.ID, "submit")
            buttonNextButton1.click()
            time.sleep(2)
        except TimeoutException:
            logging.info("Reached timeout exception block")
            unInput_input = input("Element not found. Press 'Enter' to try again or enter 'exit' to quit: ")
            logging.info(f"User entered: {unInput_input}")
            if unInput_input.lower() == 'exit':
                sys.exit()
        pwInput = WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.ID, "i0118")))
        pwInput.send_keys(barracuda_password)
        logging.info('Password entered')
        time.sleep(1)
        buttonSignIn = self.driver.find_element(By.ID, "idSIButton9")
        buttonSignIn.click()
        # logging.info('Sign In clicked')
        time.sleep(2)
        buttonSMSclick = self.driver.find_element(
            By.XPATH, "//div[@data-value='OneWaySMS']")
        buttonSMSclick.click()
        input("Script Halted | Enter OTP from SMS then press enter")
        time.sleep(1)

        try:
            noMoreCheckboxes = WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.ID, "KmsiCheckboxField")))
            noMoreCheckboxes.click()
            time.sleep(1)
            buttonYes = self.driver.find_element(By.ID, "idSIButton9")
            buttonYes.click()
            logging.info("Checkbox done")
        except TimeoutException:
            logging.info("Element not found within the given time. Skipping this step.")
        logging.info("Sleep 10:Barracuda Page")
        time.sleep(10)

    def navigate_acceptTerms(self):
        logging.info("https://ess.barracudanetworks.com/log")
        self.driver.get("https://ess.barracudanetworks.com/log")
        time.sleep(1)
        try:
            logging.info(msg="looking for acceptCookies - Id: onetrust-accept-btn-handler")
            acceptCookies = WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler")))
            self.driver.execute_script(
                "arguments[0].scrollIntoView();", acceptCookies)
            try:
                acceptCookies.click()
                logging.info(msg="Cookie accepted via Selenium click.")
            except WebDriverException:
                try:
                    self.driver.execute_script("arguments[0].click();", acceptCookies)
                    logging.info("Cookie accepted via JavaScript click.")
                except Exception as e:
                    logging.info(f"Failed to click the cookie button: {e}")
        except TimeoutException:
            logging.info("Accept cookies button not found within 10 seconds. Continuing without accepting cookies.")
            time.sleep(3)
        try:
            logging.info("looking for buttonMessageLogs - By.LINK_TEXT, Message Log")
            buttonMessageLogs = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.LINK_TEXT, "Message Log")))
            logging.info('buttonMessageLogs found')
            for i in range(5):
                try:
                    buttonMessageLogs.click()
                    break
                except WebDriverException:
                    logging.info(msg="WebDriverException: Element is not clickable at point (x, y). Trying again.")
                    time.sleep(2)
        except TimeoutException:
            logging.info(msg="Message Log button not found within 10 seconds.")
            time.sleep(5)

    def navigate_DropdownValues(self, wait, element_name, value):
        dropdown_element = wait.until(
            EC.presence_of_element_located((By.ID, element_name)))
        dropdown = Select(dropdown_element)
        dropdown.select_by_visible_text(value)

    def navigate_setupQEPageDetails(self):
        try:
            from_header = WebDriverWait(self.driver, 60).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "td.from")))
            from_header.click()
            time.sleep(1)
            emailDisplayDropdownSelection = WebDriverWait(self.driver, 60).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "li[data-menu-item-value='both']")))
            emailDisplayDropdownSelection.click()
            logging.info(
                "Email Display: Both selected | Sleep 5 seconds to load data.")
            time.sleep(5)
            domainDropdown = WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.ID, "domain_id_select")))
            domainDropdownSelect = Select(domainDropdown)
            domainDropdownSelect.select_by_visible_text("All domains")
            time.sleep(1)
            advancedSearch = WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.ID, "log-advanced-search-toggle")))
            advancedSearch.click()
            time.sleep(1)
            wait = WebDriverWait(self.driver, 60)
            self.navigate_DropdownValues(
                wait, "domain_id_select", "All domains")
            logging.info('domain_id_select: All domains')
            time.sleep(1)
            self.navigate_DropdownValues(wait, "search_action", "Quarantined")
            logging.info('search_action: Quarantined')
            time.sleep(1)
            self.navigate_DropdownValues(wait, "limit", "200")
            logging.info('limit: 200')
            time.sleep(1)
            self.navigate_DropdownValues(wait, "search_range_select", "1 day")
            logging.info('search_range_select: 1 day')
            time.sleep(1)
            self.navigate_DropdownValues(
                wait, "search_delivery_status", "Not Delivered")
            logging.info('search_delivery_status: Not Delivered')
            time.sleep(1)
            buttonSearch = WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.ID, "search-btn")))
            buttonSearch.click()
            logging.info(
                "Search button clicked. Waiting for table data to load. Sleep 5")
            time.sleep(5)
            checkbox_td = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'td.details')))
            checkbox = checkbox_td.find_element(By.XPATH, './/input[@type="checkbox"]')
            # Click on the checkbox
            checkbox.click()
            logging.info("Select All tick box clicked")
            exportButton = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div#log-bd div#log-main form#log-form div#log-main-tb div.toolbar span.button-group button[value="export"]')))
            time.sleep(1)
            exportButton.click()
            logging.info('Sleep 10')
            time.sleep(10)
            # tableData = WebDriverWait(self.driver, 60).until(
            #     EC.presence_of_element_located((By.ID, "log-rows-bd")))
            # time.sleep(1)
            # return tableData
        except TimeoutException:
            logging.info("navigate_setupQEPageDetails() TimeoutException")
