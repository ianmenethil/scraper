# import logging
import time
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from configs_setup import setup_logger
S = time.sleep
logger = setup_logger('getNavigatorLogger', "logs/main.log")

class Navigator:
    def __init__(self, driver):
        self.driver = driver

    def barracuda_login_screen(self, barracuda_username, barracuda_password, barracuda_url):
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
            logger.error("Username field or submit button could not be found within the given time.")
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

    def messagelogs_screen(self):
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
            logger.error("Accept cookies button not found. Continuing without accepting cookies.")
            S(3)
        # try:
        #     # logger.info("Looking for Message Logs Button")
        #     message_logs_button = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.LINK_TEXT, "Message Log")))
        #     logger.info('Message Logs Button found')
        #     try:
        #         message_logs_button.click()
        #     except WebDriverException:
        #         logger.error(msg="WebDriverException: Message Logs Button Element is not clickable at point.")
        #         S(2)
        # except TimeoutException:
        #     logger.error(msg="Message Log button not found.")
        #     S(5)

    def setup_dropdown_values(self, wait, element_name, value):
        dropdown_element = wait.until(EC.visibility_of_element_located((By.ID, element_name)))
        dropdown = Select(dropdown_element)
        dropdown.select_by_visible_text(value)

    def setup_messagelogs_table(self):
        try:
            logger.info("Setting up Message Logs table")
            # Email address formatting, change default format to "Both" to display sender name and email address
            from_header = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "td.from")))
            from_header.click()
            logger.info('"From" clicked')
            S(1)
            emaildisplay_dropdown_option = WebDriverWait(self.driver, 60).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "li[data-menu-item-value='both']")))
            # emaildisplay_dropdown_option.click()
            success = self.try_click(emaildisplay_dropdown_option)
            if not success:
                logger.error("Failed to set emails to both.")
            else:
                logger.info('Email Display formatting set to: "Both"')
            S(5)

            # Change domains to "All domains"
            domain_dropdown_option = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.ID, "domain_id_select")))
            domain_dropdown_option_select = Select(domain_dropdown_option)
            domain_dropdown_option_select.select_by_visible_text("All domains")
            S(1)

            # Click on Advanced Search button to display more options
            advancedsearch_dropdown_option = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.ID, "log-advanced-search-toggle")))
            advancedsearch_dropdown_option.click()
            logger.info('Advanced Search button clicked')
            S(2)

            # Change table limit to 200
            limit_dropdown_option = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.ID, "limit")))
            limit_dropdown_option_select = Select(limit_dropdown_option)
            limit_dropdown_option_select.select_by_visible_text("200")
            S(2)

            wait = WebDriverWait(self.driver, 60)
            # self.setup_dropdown_values(wait, "domain_id_select", "All domains")
            # logger.info('Domains: All domains')
            # S(1)
            self.setup_dropdown_values(wait, "search_action", "Quarantined")
            logger.info('Email Status: Quarantined')
            S(1)
            # self.setup_dropdown_values(wait, "limit", "200")
            # logger.info('Table Limit: 200')
            # S(1)
            self.setup_dropdown_values(wait, "search_range_select", "2 days")
            logger.info('Date Range: 2 days')
            S(1)
            self.setup_dropdown_values(wait, "search_delivery_status", "Not Delivered")
            logger.info('Delivery Status: Not Delivered')
            S(1)
        except TimeoutException:
            logger.error("setup_messagelogs_table() TimeoutException")
        except Exception:  # ignore pylint: disable=broad-except
            logger.error("setup_messagelogs_table")

    def search_and_export(self):
        try:
            wait = WebDriverWait(self.driver, 60)
            # Click on Search button to display table data
            search_button = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.ID, "search-btn")))
            logger.info("Search button clicked. Waiting for table data to load.")
            search_button.click()
            S(5)

            checkbox_td = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'td.details')))
            checkbox = checkbox_td.find_element(By.XPATH, './/input[@type="checkbox"]')
            logger.info("Select All tick box clicked")
            checkbox.click()
            S(2)

            # Click on Export button to download table data
            export_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div#log-bd div#log-main form#log-form div#log-main-tb div.toolbar span.button-group button[value="export"]')))
            S(1)
            logger.info('Export clicked, waiting for download to complete.')
            export_button.click()
            S(3)
        except TimeoutException:
            logger.info("search_and_export() TimeoutException")
        except Exception:  # ignore pylint: disable=broad-except
            logger.error("search_and_export Exception")

    def try_click(self, element):
        """Try various methods to click an element."""
        # Native Selenium click
        try:
            element.click()
            return True
        except WebDriverException:
            pass
        # JavaScript click
        try:
            self.driver.execute_script("arguments[0].click();", element)
            return True
        except WebDriverException:
            pass
        # ActionChains click
        try:
            actions = ActionChains(self.driver)
            actions.move_to_element(element).click().perform()
            return True
        except WebDriverException:
            pass
        # If none of the methods work, return False
        return False

    # def setup_messagelogs_table(self):
    #     try:
    #         # Email address formatting, change default format to "Both" to display sender name and email address
    #         from_header = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "td.from")))
    #         from_header.click()
    #         logger.info('"From" clicked')
    #         S(1)
    #         emaildisplay_dropdown_option = WebDriverWait(self.driver, 60).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "li[data-menu-item-value='both']")))
    #         emaildisplay_dropdown_option.click()
    #         logger.info('Email Display formatting set to: "Both"')
    #         S(5)

    #         # Change domains to "All domains"
    #         domain_dropdown_option = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.ID, "domain_id_select")))
    #         domain_dropdown_option_select = Select(domain_dropdown_option)
    #         domain_dropdown_option_select.select_by_visible_text("All domains")
    #         S(1)

    #         # Click on Advanced Search button to display more options
    #         advancedsearch_dropdown_option = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.ID, "log-advanced-search-toggle")))
    #         advancedsearch_dropdown_option.click()
    #         logger.info('Advanced Search button clicked')
    #         S(2)

    #         # Change table limit to 200
    #         limit_dropdown_option = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.ID, "limit")))
    #         limit_dropdown_option_select = Select(limit_dropdown_option)
    #         limit_dropdown_option_select.select_by_visible_text("200")
    #         S(2)

    #         wait = WebDriverWait(self.driver, 60)
    #         # self.setup_dropdown_values(wait, "domain_id_select", "All domains")
    #         # logger.info('Domains: All domains')
    #         # S(1)
    #         self.setup_dropdown_values(wait, "search_action", "Quarantined")
    #         logger.info('Email Status: Quarantined')
    #         S(1)
    #         # self.setup_dropdown_values(wait, "limit", "200")
    #         # logger.info('Table Limit: 200')
    #         # S(1)
    #         self.setup_dropdown_values(wait, "search_range_select", "2 days")
    #         logger.info('Date Range: 2 days')
    #         S(1)
    #         self.setup_dropdown_values(wait, "search_delivery_status", "Not Delivered")
    #         logger.info('Delivery Status: Not Delivered')
    #         S(1)

    #         # Click on Search button to display table data
    #         search_button = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.ID, "search-btn")))
    #         logger.info("Search button clicked. Waiting for table data to load.")
    #         search_button.click()
    #         S(5)

    #         checkbox_td = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'td.details')))
    #         checkbox = checkbox_td.find_element(By.XPATH, './/input[@type="checkbox"]')
    #         logger.info("Select All tick box clicked")
    #         checkbox.click()
    #         S(2)

    #         # Click on Export button to download table data
    #         export_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div#log-bd div#log-main form#log-form div#log-main-tb div.toolbar span.button-group button[value="export"]')))
    #         S(1)
    #         logger.info('Export clicked, waiting for download to complete.')
    #         export_button.click()
    #         S(3)
    #     except TimeoutException:
    #         logger.info("setup_messagelogs_table() TimeoutException")
