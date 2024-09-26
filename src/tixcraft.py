import logging
import random
import time
import traceback
from time import sleep

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import url_contains, element_to_be_clickable
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from src.common.alert_util import close_alert
from src.common.my_driver import MyDriver
from src.common.ocr_util import image_to_text


REFRESH_INTERVAL = 1


class TixCraft:
    default_page = 'https://tixcraft.com/'

    def __init__(self, config):
        self.config = config
        self.driver = MyDriver()
        self.consent_is_closed = False

    def setup_browser(self):
        self.driver.get(self.default_page)
        self.driver.maximize_window()

    def set_cookie(self):
        self.driver.add_cookie({
            'name': 'SID',
            'value': self.config.sid_cookie,
        })

    def close_consent(self):
        selector = 'button#onetrust-reject-all-handler'
        try:
            WebDriverWait(self.driver, 2).until(element_to_be_clickable((By.CSS_SELECTOR, selector)))
            reject_all = self.driver.retry_find_element(selector)
            reject_all.click()
        except TimeoutException:
            pass

    def enter_captcha(self):
        selector = 'img#TicketForm_verifyCode-image'
        while True:
            result = image_to_text(self.driver, selector)
            logging.info(f'ocr: {result}')
            # refresh the ocr if the length of result is wrong
            if len(result) != 4:
                captcha = self.driver.retry_find_element(selector)
                captcha.click()
                time.sleep(0.1)
                continue

            captcha_input = self.driver.retry_find_element('input#TicketForm_verifyCode')
            captcha_input.send_keys(result)
            break

    def login(self):
        sign_in = self.driver.retry_find_element('a.justify-content-center')
        sign_in.click()
        facebook_sign_in = self.driver.retry_find_element('#loginFacebook')
        facebook_sign_in.retry_click()
        email = self.driver.retry_find_element('#email')
        email.send_keys(self.config.facebook_account)
        password = self.driver.retry_find_element('#pass')
        password.send_keys(self.config.facebook_password)
        # consent = self.driver.retry_find_element(
        #     '.x1ja2u2z.x78zum5.x2lah0s.x1n2onr6.xl56j7k.x6s0dn4.xozqiw3.x1q0g3np.xi112ho.x17zwfj4.x585lrc.x1403ito.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.xn6708d.x1ye3gou.xtvsq51.x1r1pt67')
        # consent.retry_click()
        # login_button = self.driver.retry_find_element('#loginbutton')
        # login_button.click()
        # continue_button = self.driver.retry_find_element(
        #     '.x1ja2u2z.x78zum5.x2lah0s.x1n2onr6.xl56j7k.x6s0dn4.xozqiw3.x1q0g3np.xi112ho.x17zwfj4.x585lrc.x1403ito.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.xn6708d.x1ye3gou.xtvsq51.x1r1pt67')
        # continue_button.click()
        try:
            WebDriverWait(self.driver, 60).until(url_contains(self.default_page))
        except TimeoutException:
            pass

    def fetch_sid(self) -> str:
        cookie = self.driver.get_cookie('SID')
        return cookie['value']

    def close(self):
        self.driver.close()

    def execute(self):
        def handle_events():
            events = self.driver.retry_find_elements('#gameList > table > tbody > tr')
            # TODO: [P2] only select a target date
            random.shuffle(events)
            # sold_out_text_list = ['Sold out', '已售完']
            find_ticket_text_list = ['立即訂購', 'Find tickets']

            event_is_available = False
            for event in events:
                # handle the event if it's available
                if any(text in event.text for text in find_ticket_text_list):
                    find_tickets_button = event.retry_find_element('button', retries=1)
                    self.driver.enforce_click(find_tickets_button)
                    event_is_available = True

            if not event_is_available:
                sleep(REFRESH_INTERVAL)
                self.driver.refresh()

        def handle_areas():
            seats = self.driver.retry_find_elements('.area-list > li > a')
            random.shuffle(seats)
            for seat in reversed(seats):
                self.driver.enforce_click(seat)

        def handle_tickets():
            # TODO: support ticket type selection
            quantity = self.driver.retry_find_element('table#ticketPriceList > tbody > tr').retry_find_element('select')
            select = Select(quantity)

            # select max quantity
            select.select_by_index(len(select.options) - 1)

            # check agreement
            agreement = self.driver.retry_find_element('#TicketForm_agree')
            self.driver.enforce_click(agreement)

            # enter_captcha
            self.enter_captcha()

            # click submit button
            submit = self.driver.retry_find_element('.btn-primary')
            self.driver.enforce_click(submit)

            close_alert(self.driver)

        def handle_confirm():
            time.sleep(1)

        def handle_checkout():
            time.sleep(1)

        self.driver.get(self.config.target_page)
        while True:
            try:
                url = self.driver.current_url
                if '/activity/detail' in url:
                    self.driver.get(url.replace('detail', 'game'))
                elif '/activity/game' in url:
                    handle_events()
                elif '/ticket/area' in url:
                    handle_areas()
                elif '/ticket/ticket' in url:
                    handle_tickets()
                elif '/ticket/order' in url:
                    handle_confirm()
                elif '/ticket/checkout' in url:
                    handle_checkout()


            except Exception as e:
                print(traceback.format_exc())
                logging.error(f'get error: {e}')
