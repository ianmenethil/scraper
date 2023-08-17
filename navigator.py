import logging
import sys
import time
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
S = time.sleep

class Navigator:
    def __init__(self, driver):
        self.driver = driver

    def interact_with_element(self, locator, action, data=None, description=None, error_message=None):
        try:
            element = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located(locator))
            if action == "send_keys":
                element.send_keys(data)
            elif action == "click":
                element.click()
            if description:
                logging.info("%s", description)
            S(1)
        except TimeoutException as timeout_exception:
            logging.error("Error interacting with element %s: %s", locator, timeout_exception)
        except Exception as exception:
            logging.error("Error interacting with element %s: %s", locator, exception)
            if error_message:
                user_input = input(error_message)
                logging.error("User entered: %s", user_input)
                if user_input.lower() == 'exit':
                    sys.exit()
                elif user_input.lower() == '':
                    pass

    def scr_brcd_login_screen(self, barracuda_username, barracuda_password, barracuda_url):
        logging.debug("scr_brcd_login_screen")
        self.driver.get(barracuda_url)
        S(1)
        self.interact_with_element((By.ID, "username"), "send_keys", barracuda_username, 'Username entered', "Username Element not found. Press 'Enter' to try again or enter 'exit' to quit: ")
        self.interact_with_element((By.ID, "submit"), "click", None, 'Next button clicked', "Next button not found. Press 'Enter' to continue manually or enter 'exit' to quit: ")
        self.interact_with_element((By.ID, "password"), "send_keys", barracuda_password, 'Password entered', "Password field not found. Press 'Enter' to continue manually or enter 'exit' to quit: ")
        self.interact_with_element((By.ID, "submit"), "click", None, 'Sign-in button clicked', "Sign-in button not found. Press 'Enter' to continue manually or enter 'exit' to quit: ")
        self.interact_with_element((By.ID, "KmsiCheckboxField"), "click", None, 'Checkbox clicked', "Checkbox not found. Press 'Enter' to continue manually or enter 'exit' to quit: ")
        self.interact_with_element((By.ID, "idSIButton9"), "click", None, 'Yes button clicked', "Yes button not found. Press 'Enter' to continue manually or enter 'exit' to quit: ")

        logging.info("Barracuda Page")
        S(3)
        # If using MFA, uncomment the following lines
        # password_field = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.ID, "i0118")))
        # password_field.send_keys(barracuda_password)
        # logging.info('Password entered')
        # S(1)
        # signin_button = self.driver.find_element(By.ID, "idSIButton9")
        # signin_button.click()
        # S(5)

        # # OTP via SMS
        # trigger_otp_button = self.driver.find_element(By.XPATH, "//div[@data-value='OneWaySMS']")
        # trigger_otp_button.click()
        # input("Script Halted | Enter OTP from SMS then press enter")
        # S(2)

    def brcd_main_screen(self):
        logging.info("https://ess.barracudanetworks.com/log")
        self.driver.get("https://ess.barracudanetworks.com/log")
        S(1)
        try:
            logging.info(msg="looking for accept_cookies - Id: onetrust-accept-btn-handler")
            accept_cookies = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler")))
            self.driver.execute_script("arguments[0].scrollIntoView();", accept_cookies)
            try:
                accept_cookies.click()
                logging.info(msg="Cookie accepted via Selenium click.")
            except WebDriverException:
                try:
                    self.driver.execute_script("arguments[0].click();", accept_cookies)
                    logging.info("Cookie accepted via JavaScript click.")
                except Exception as e_except:  # pylint: disable=broad-except
                    logging.error("Failed to click the cookie button: %s", {e_except})
        except TimeoutException:
            logging.error("Accept cookies button not found within 10 seconds. Continuing without accepting cookies.")
            S(3)
        try:
            logging.info("looking for message_logs_button - By.LINK_TEXT, Message Log")
            message_logs_button = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.LINK_TEXT, "Message Log")))
            logging.info('message_logs_button found')
            for _ in range(5):
                try:
                    message_logs_button.click()
                    break
                except WebDriverException:
                    logging.error(msg="WebDriverException: Element is not clickable at point (x, y). Trying again.")
                    S(2)
        except TimeoutException:
            logging.error(msg="Message Log button not found within 10 seconds.")
            S(5)

    def setup_dropdown_values(self, wait, element_name, value):
        dropdown_element = wait.until(EC.presence_of_element_located((By.ID, element_name)))
        dropdown = Select(dropdown_element)
        dropdown.select_by_visible_text(value)

    def setup_messagelogs_table(self):
        try:
            from_header = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "td.from")))
            from_header.click()
            S(1)
            emaildisplay_dropdown_option = WebDriverWait(self.driver, 60).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "li[data-menu-item-value='both']")))
            emaildisplay_dropdown_option.click()
            logging.info("Email Display: Both selected | Sleep 5 seconds to load data.")
            S(5)
            domain_dropdown_option = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.ID, "domain_id_select")))
            domain_dropdown_option_select = Select(domain_dropdown_option)
            domain_dropdown_option_select.select_by_visible_text("All domains")
            S(1)
            advancedsearch_dropdown_option = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.ID, "log-advanced-search-toggle")))
            advancedsearch_dropdown_option.click()
            S(1)
            wait = WebDriverWait(self.driver, 60)
            self.setup_dropdown_values(wait, "domain_id_select", "All domains")
            logging.info('domain_id_select: All domains')
            S(1)
            self.setup_dropdown_values(wait, "search_action", "Quarantined")
            logging.info('search_action: Quarantined')
            S(1)
            self.setup_dropdown_values(wait, "limit", "200")
            logging.info('limit: 200')
            S(1)
            self.setup_dropdown_values(wait, "search_range_select", "1 day")
            logging.info('search_range_select: 1 day')
            S(1)
            self.setup_dropdown_values(wait, "search_delivery_status", "Not Delivered")
            logging.info('search_delivery_status: Not Delivered')
            S(1)
            search_button = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.ID, "search-btn")))
            search_button.click()
            logging.info("Search button clicked. Waiting for table data to load. Sleep 5")
            S(5)
            checkbox_td = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'td.details')))
            checkbox = checkbox_td.find_element(By.XPATH, './/input[@type="checkbox"]')
            checkbox.click()
            logging.info("Select All tick box clicked")
            export_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div#log-bd div#log-main form#log-form div#log-main-tb div.toolbar span.button-group button[value="export"]')))
            S(1)
            export_button.click()
            logging.info('Sleep 10')
            S(10)
        except TimeoutException:
            logging.info("setup_messagelogs_table() TimeoutException")
