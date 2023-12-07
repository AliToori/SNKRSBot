#!/usr/bin/env python3
"""
    *******************************************************************************************
    SNKRsBot: Nike Sneakers auto-purchase bot
    Author: Ali Toori, Python Bot Developer
    Website: https://botflocks.com/
    LinkedIn: https://www.linkedin.com/in/alitoori/
    *******************************************************************************************
"""
import concurrent.futures
import logging.config
import os
import pickle
import sys
import time
from pathlib import Path
from time import sleep
import ntplib
import pandas as pd
import pyfiglet
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from selenium import webdriver
import undetected_chromedriver as uc
from multiprocessing import freeze_support
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    'formatters': {
        'colored': {
            '()': 'colorlog.ColoredFormatter',  # colored output
            # --> %(log_color)s is very important, that's what colors the line
            'format': '[%(asctime)s,%(lineno)s] %(log_color)s[%(message)s]',
            'log_colors': {
                'DEBUG': 'green',
                'INFO': 'cyan',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            },
        },
        'simple': {
                'format': '[%(asctime)s,%(lineno)s] [%(message)s]',
            },
    },
    "handlers": {
        "console": {
            "class": "colorlog.StreamHandler",
            "level": "INFO",
            "formatter": "colored",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "simple",
            "filename": "SNKRsBot_logs.log"
        },
    },
    "root": {"level": "INFO",
             "handlers": ["console", "file"]
             }
})

LOGGER = logging.getLogger()


class SNKRsBot:
    def __init__(self):
        self.stopped = False
        self.PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
        self.PROJECT_ROOT = Path(self.PROJECT_ROOT)
        # start_date = str((datetime.now() - timedelta(7)).strftime('%m/%d/%Y'))
        # end_date = str((datetime.now() - timedelta(0)).strftime('%m/%d/%Y'))
        self.file_path_accounts = str(self.PROJECT_ROOT / 'SNKRsRes/Accounts.csv')
        self.file_path_proxies = str(self.PROJECT_ROOT / 'SNKRsRes/proxies.txt')
        self.file_path_uagents = str(self.PROJECT_ROOT / 'SNKRsRes/user_agents.txt')
        self.NIKE_HOME_URL = "https://www.nike.com"
        self.SNKRS_HOME_URL = "https://www.nike.com/launch"
        self.SNKRS_STOCK_URL = "https://www.nike.com"
        self.NIKE_PROFILE_URL = "https://www.nike.com/member/profile/"
        self.NIKE_CART_URL = "https://www.nike.com/cart"
        self.NIKE_CHECKOUT_URL = "https://www.nike.com/checkout"

    @staticmethod
    def enable_cmd_colors():
        # Enables Windows New ANSI Support for Colored Printing on CMD
        from sys import platform
        if platform == "win32":
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

    # Trial logic
    @staticmethod
    def trial(trial_date):
        ntp_client = ntplib.NTPClient()
        try:
            response = ntp_client.request('pool.ntp.org')
            local_time = time.localtime(response.ref_time)
            current_date = time.strftime('%Y-%m-%d %H:%M:%S', local_time)
            current_date = datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S')
            return trial_date > current_date
        except:
            pass

    # Get user agent
    def get_user_agent(self, account_num):
        with open(self.file_path_uagents) as f:
            content = f.readlines()
        u_agents_list = [x.strip() for x in content]
        return u_agents_list[int(account_num)]

    # Get proxy
    def get_proxy(self, account_num):
        with open(self.file_path_proxies) as f:
            content = f.readlines()
        proxies_list = [x.strip() for x in content]
        return proxies_list[int(account_num)]

    # Get web driver
    def get_driver(self, account, headless=False):
        account_num = str(account["AccountNo"]).strip()
        proxy = account["Proxy"]
        LOGGER.info(f'Launching chrome browser')
        # For absolute chromedriver path
        driver_BIN = str(self.PROJECT_ROOT / 'SNKRsRes/bin/chromedriver.exe')
        # user_dir = str(self.PROJECT_ROOT / 'SNKRsRes/UserData')
        options = uc.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-extensions')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--ignore-certificate-errors')
        # options.add_argument(f"--user-data-dir={user_dir}")
        prefs = {f'profile.default_content_settings.popups': 0,
                 "credentials_enable_service": False,
                 "profile.password_manager_enabled": False}
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument(f'--user-agent={self.get_user_agent(account_num)}')
        # if proxy != "No":
        #     options.add_argument(f"--proxy-server={proxy}")
        if headless:
            options.add_argument('--headless')
        driver = uc.Chrome(executable_path=driver_BIN, options=options)
        return driver

    # Finish and quit browser
    def finish(self, driver):
        LOGGER.info(f'Quiting the browser instance')
        try:
            driver.close()
            driver.quit()
        except:
            LOGGER.info(f'Issue while quiting the browser instance')

    # Waits for an element
    @staticmethod
    def wait_until_visible(driver, xpath=None, element_id=None, name=None, class_name=None, tag_name=None, css_selector=None, duration=10000, frequency=0.01):
        if xpath:
            WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        elif element_id:
            WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.ID, element_id)))
        elif name:
            WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.NAME, name)))
        elif class_name:
            WebDriverWait(driver, duration, frequency).until(
                EC.element_to_be_clickable((By.CLASS_NAME, class_name)))
        elif tag_name:
            WebDriverWait(driver, duration, frequency).until(
                EC.visibility_of_element_located((By.TAG_NAME, tag_name)))
        elif css_selector:
            WebDriverWait(driver, duration, frequency).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))

    # Login to the nike account
    def login_nike(self, driver, account):
        email = str(account["Email"]).strip()
        password = str(account["Password"]).strip()
        LOGGER.info(f'Signing-in to Nike account: {email}')
        cookies = 'Cookies_' + email + '.pkl'
        cookies_file_path = self.PROJECT_ROOT / 'SNKRsRes' / cookies
        # Try signing-in via cookies
        if os.path.isfile(cookies_file_path):
            LOGGER.info(f'Requesting: {str(self.NIKE_HOME_URL)}: account: {email}')
            driver.get(self.NIKE_HOME_URL)
            LOGGER.info(f'Loading cookies ... Account: {email}')
            with open(cookies_file_path, 'rb') as cookies_file:
                cookies = pickle.load(cookies_file)
            for cookie in cookies:
                driver.add_cookie(cookie)
            try:
                # Wait for profile to become visible
                self.wait_until_visible(driver=driver, css_selector='#AccountMenu', duration=5)
                LOGGER.info(f'Cookies login successful ... Account: {email}')
                # driver.refresh()
                return True
            except:
                LOGGER.info(f'Cookies login failed ... Account: {email}')
                # self.captcha_login(email=email, password=password)
        # Try logout
        # try:
        #     self.wait_until_visible(driver=driver, css_selector='span[data-qa="user-name"]', duration=5)
        #     self.wait_until_visible(driver=driver, css_selector='button[type="button"]', duration=5)
        #     driver.find_element_by_css_selector('button[type="button"]').click()
        #     self.wait_until_visible(driver=driver, css_selector="button[class='portrait-dropdown link']", duration=5)
        #     driver.find_element_by_css_selector("button[class='portrait-dropdown link']").click()
        # except:
        #     pass
        # Try sign-in normally using credentials
        LOGGER.info(f"Logging in using credentials: account: {email}")
        try:
            LOGGER.info(f"Waiting for login: account: {email}")
            LOGGER.info(f'Requesting: {str(self.SNKRS_STOCK_URL)} account: {email}')
            driver.get(self.SNKRS_STOCK_URL)
            # Wait and click login button
            # self.wait_until_visible(driver=driver, css_selector='button[type="button"]')
            # driver.find_element_by_css_selector('button[type="button"]').click()
            self.wait_until_visible(driver=driver, css_selector='button[data-path="sign in"]')
            driver.find_element_by_css_selector('button[data-path="sign in"]').click()
            LOGGER.info(f'Filling email: account: {email}')
            self.wait_until_visible(driver=driver, css_selector='input[type="email"]')
            email_input = driver.find_element_by_css_selector('input[type="email"]')
            email_input.clear()
            email_input.send_keys(email)
            LOGGER.info(f'Filling password: account: {email}')
            password_input = driver.find_element_by_css_selector('input[type="password"]')
            password_input.clear()
            password_input.send_keys(password)
            driver.find_element_by_css_selector('input[type="button"]').click()
            LOGGER.info(f'Credentials submitted: account: {email}')
            LOGGER.info(f'Waiting for user profile: account: {email}')
            self.wait_until_visible(driver=driver, css_selector='span[data-qa="user-name"]')
            use_name = driver.find_element_by_css_selector('span[data-qa="user-name"]').text
            LOGGER.info(f'UserName: {use_name}')
            LOGGER.info('Successful sign-in')
            # Store user cookies for later use
            LOGGER.info(f'Saving cookies for: Account: {email}')
            with open(cookies_file_path, 'wb') as cookies_file:
                pickle.dump(driver.get_cookies(), cookies_file)
            LOGGER.info(f'Cookies have been saved: Account: {email}')
            return True
        except:
            pass

    # Removes cart items
    def empty_cart(self, driver, email):
        try:
            LOGGER.info(f'Requesting: {self.NIKE_CART_URL} account: {email}')
            driver.get(self.NIKE_CART_URL)
            self.wait_until_visible(driver=driver, css_selector='h4')
            LOGGER.info(f"Waiting for cart empty message to become visible: account: {email}")
            self.wait_until_visible(driver=driver, css_selector='button[name="remove-item-button"]', duration=3)
            driver.find_element_by_css_selector('button[name="remove-item-button"]').click()
            self.wait_until_visible(driver=driver, css_selector='p[data-automation="no-items"]', duration=5)
            LOGGER.info(f"Cart has been cleared: account: {email}")
        except:
            LOGGER.info(f"Cart has no item: account: {email}")

    def select_shoes_color(self, driver, account):
        shoes_color = account["ShoesColor"]
        LOGGER.info("Waiting for color grid to become visible:")
        self.wait_until_visible(driver=driver, xpath='//*[@id="ColorwayDiv"]/div/div')
        LOGGER.info("Selecting color from the color grid:")
        LOGGER.info(f"Color to be selected: {shoes_color}")
        for color in driver.find_elements_by_css_selector('.colorway-anchor.noGrayOverlayColor'):
            if shoes_color in str(color).strip():
                color.click()
                LOGGER.info("Shoes color selected:" + str(shoes_color))
                return True
            else:
                continue

    def add_to_cart(self, driver, account):
        LOGGER.info(f"Adding item to cart")
        shoes_sizes = str(account["ShoesSizes"]).split(':')
        email = account["Email"]
        actions = ActionChains(driver)
        # Scroll to the Add-To-Cart button
        try:
            self.wait_until_visible(driver, css_selector="button[class='ncss-btn-primary-dark btn-lg capitalize']", duration=5)
        except:
            pass
        driver.find_element_by_tag_name('html').send_keys(Keys.SPACE)
        driver.find_element_by_tag_name('html').send_keys(Keys.SPACE)
        try:
            LOGGER.info(f"Waiting for cart button: account: {email}")
            self.wait_until_visible(driver, css_selector="button[class='ncss-btn-primary-dark btn-lg capitalize']", duration=10)
            cart_btn = driver.find_element_by_css_selector("button[class='ncss-btn-primary-dark btn-lg capitalize']")
            actions.move_to_element(cart_btn)
        except:
            return False
        # LOGGER.info("Waiting for size grid to become clickable:" + ' Account No. ' + str(account_num))
        LOGGER.info("Selecting size")
        # Select shoes size
        for shoes_size in shoes_sizes:
            LOGGER.info("Size to be selected:" + str(shoes_size))
            for size in driver.find_elements_by_css_selector('li[data-qa="size-available"]'):
                LOGGER.info(f"Item size: {size.text}")
                if str(size.text).strip() == shoes_size:
                    size.click()
                    LOGGER.info(f"Size has been selected: {str(size.text).strip()}")
                    break
                else:
                    continue
        LOGGER.info("Adding to cart:")
        self.wait_until_visible(driver, css_selector="button[class='ncss-btn-primary-dark btn-lg capitalize']", duration=10)
        driver.find_element_by_css_selector("button[class='ncss-btn-primary-dark btn-lg capitalize']").click()
        self.wait_until_visible(driver, css_selector="button[class='ncss-btn-primary-dark']")
        driver.find_element_by_css_selector("button[class='ncss-btn-primary-dark']").click()
        LOGGER.info("Waiting for checkout page")
        self.wait_until_visible(driver, css_selector="h1", duration=10)
        LOGGER.info(f"Item has been added to cart: {email}")
        return True

    # Change shipping details
    def change_delivery_option(self, driver, account):
        first_name = account["FirstName"]
        last_name = account["LastName"]
        address = account["Address"]
        email = account["Email"]
        phone = account["Phone"]
        LOGGER.info(f"Editing shipping details: {email}")
        self.wait_until_visible(driver, css_selector='a[aria-label="Edit Shipping"]')
        driver.find_element_by_css_selector('a[aria-label="Edit Shipping"]').click()
        self.wait_until_visible(driver, css_selector='button[class="ncss-btn-clear u-underline"]')
        driver.find_element_by_css_selector('button[class="ncss-btn-clear u-underline"]').click()
        self.wait_until_visible(driver, css_selector='[id="firstName"]')
        f_name = driver.find_element_by_css_selector('[id="firstName"]')
        f_name.clear()
        f_name.send_keys(first_name)
        l_name = driver.find_element_by_css_selector('[id="lastName"]')
        l_name.clear()
        l_name.send_keys(last_name)
        addr = driver.find_element_by_css_selector('[id="address1"]')
        addr.clear()
        addr.send_keys(address)
        e_mail = driver.find_element_by_css_selector('[id="email"]')
        e_mail.clear()
        e_mail.send_keys(email)
        phone_num = driver.find_element_by_css_selector('[id="phoneNumber"]')
        phone_num.clear()
        phone_num.send_keys(phone)
        LOGGER.info("Saving changes")
        # Save change
        driver.find_element_by_css_selector('button[type="submit"]').click()
        # Continue to Payment
        self.wait_until_visible(driver, css_selector='button[type="button"]')
        driver.find_element_by_css_selector('button[type="button"]').click()
        # Continue to order
        try:
            self.wait_until_visible(driver, css_selector='button[data-attr="continueToOrderReviewBtn"]')
            driver.find_element_by_css_selector('button[data-attr="continueToOrderReviewBtn"]').click()
        except:
            pass

    # Add a new payment card
    def add_new_card(self, driver, account):
        card_num = account["CardNumber"]
        expiry = account["CardExpiry"]
        cvv = account["CVV"]
        driver.find_element_by_tag_name('html').send_keys(Keys.END)
        LOGGER.info("Adding new card")
        # Click Edit button under Payment
        self.wait_until_visible(driver, css_selector='a[aria-label="Edit Payment"]')
        driver.find_element_by_css_selector('a[aria-label="Edit Payment"]').click()
        # Add New card
        self.wait_until_visible(driver=driver, css_selector='[id="newCard"]')
        driver.find_element_by_css_selector('[id="newCard"]').click()
        # Enter card number
        self.wait_until_visible(driver=driver, css_selector='[id="creditCardNumber"]')
        driver.find_element_by_css_selector('[id="creditCardNumber"]').send_keys(card_num)
        # Enter Expiration date
        driver.find_element_by_css_selector('[id="expirationDate"]').send_keys(expiry)
        # select state by visible text
        driver.find_element_by_css_selector('[id="cvNumber"]').send_keys(cvv)
        driver.find_element_by_css_selector('[for="saveCreditCardData"]').click()
        LOGGER.info("Click add new card button:")
        driver.find_element_by_css_selector('.test-payment-use-card').click()
        self.wait_until_visible(driver, css_selector='button[data-attr="continueToOrderReviewBtn"]')
        driver.find_element_by_css_selector('button[data-attr="continueToOrderReviewBtn"]').click()

    # Place order
    def place_order(self, driver, cvv):
        driver.find_element_by_tag_name('html').send_keys(Keys.END)
        try:
            # Enter card CVV number
            self.wait_until_visible(driver, css_selector='[id="cvNumber"]')
            driver.find_element_by_css_selector('[id="cvNumber"]').send_keys(cvv)
            # Continue to order
            self.wait_until_visible(driver, css_selector='button[data-attr="continueToOrderReviewBtn"]')
            driver.find_element_by_css_selector('button[data-attr="continueToOrderReviewBtn"]').click()
            return True
        except:
            return False

    # Get a new drop
    def get_drop(self, driver, account):
        LOGGER.info("Getting new drop")
        email = account["Email"]
        product_title = str(account["ProductTitle"]).lower()
        product_url = account["ProductURL"]
        LOGGER.info(f'Requesting: {self.SNKRS_STOCK_URL} account: {email}')
        driver.get(self.SNKRS_STOCK_URL)
        # Stay and continuously look for a drop
        while True:
            # Wait for items to be visible
            LOGGER.info("Waiting for items")
            self.wait_until_visible(driver, css_selector='a[data-qa="product-card-link"]')
            for item in driver.find_elements_by_css_selector('a[data-qa="product-card-link"]'):
                item_title = str(item.get_attribute('aria-label')).replace("'", "").lower()
                item_url = item.get_attribute('aria-label')
                if product_title in item_title or product_url in item_url:
                    LOGGER.info(f"Item found: {product_url}")
                    LOGGER.info(f"Requesting item: {product_url}")
                    driver.get(product_url)
                    return True
            driver.refresh()

    # Buy a drop
    def buy_drop(self, account):
        email = account["Email"]
        change_shipping = account["ChangeShipping"]
        add_new_card = account["AddNewCard"]
        card_cvv = str(account["CVV"])
        # Get a webdriver instance
        driver = self.get_driver(account=account)
        # Check and login to the website
        self.login_nike(driver=driver, account=account)
        # Try delete the items from the cart if there's any
        self.empty_cart(driver=driver, email=email)
        # Get drop
        self.get_drop(driver=driver, account=account)
        item_purchased = False
        self.add_to_cart(driver=driver, account=account)
        # Submit delivery and payment
        if str(change_shipping).lower() == 'yes':
            self.change_delivery_option(driver=driver, account=account)
        # Submit delivery and payment
        if str(add_new_card).lower() == 'yes':
            # Submit card information
            self.add_new_card(driver=driver, account=account)
        # Place order
        order_placed = self.place_order(driver=driver, cvv=card_cvv)
        # Break the while loop if item is purchased
        if order_placed:
            LOGGER.info("Order is being placed")
        LOGGER.info("Browser will be closed automatically within 5 minutes:")
        sleep(300)
        # Quit the driver
        self.finish(driver=driver)

    def main(self):
        freeze_support()
        self.enable_cmd_colors()
        trial_date = datetime.strptime('2021-08-05 23:59:59', '%Y-%m-%d %H:%M:%S')
        # Print ASCII Art
        print('************************************************************************\n')
        pyfiglet.print_figlet('____________                      SNKRsBot ____________\n', colors='RED')
        print('Author: Ali Toori, Bot Developer\n'
              'Website: https://botflocks.com/\nLinkedIn: https://www.linkedin.com/in/alitoori/\n************************************************************************')
        # Trial version logic
        # if self.trial(trial_date):
        if True:
            LOGGER.info(f'SNKRsBot launched')
            if os.path.isfile(self.file_path_accounts):
                account_df = pd.read_csv(self.file_path_accounts, index_col=None)
                accounts = []
                for account in account_df.iloc:
                    accounts.append(account)
                    self.buy_drop(account)
                num_workers = len(accounts)

                # Get accounts from Accounts.csv
                # We can use a with statement to ensure threads are cleaned up promptly
                # with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
                #     executor.map(self.buy_drop, accounts)
        # else:
        #     LOGGER.warning("Your trial has been expired, To get full version, please contact fiverr.com/AliToori !")


if __name__ == "__main__":
    nike_bot = SNKRsBot()
    nike_bot.main()

