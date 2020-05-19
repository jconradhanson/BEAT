import json
import logging
import re
from time import sleep

from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote import webelement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

# MODULE
import browser
from definitions import path_css_selectors
from definitions import path_save_errors
from definitions import default_timeout


class Crawler:
    def __init__(self, width=2560, height=1600):
        """ Crawl Google Maps for business info """
        with open(path_css_selectors, 'r') as f:
            self.css_selectors = json.load(f)

        self.browser = browser.get_firefox(width=width, height=height)
        # self.browser = browser.get_chrome(width=width, height=height)
        # self.page_count = 0

    def quit(self):
        if self.browser:
            self.browser.quit()

    def wait_for(self, key: str):
        """
        Wait for the element to fully load.

        Args:
            key: str
                CSS Selector key to wait for

        Returns: boolean
            if element fully loaded
        """
        try:
            WebDriverWait(driver=self.browser, timeout=default_timeout) \
                .until(expected_conditions
                       .presence_of_element_located((By.CSS_SELECTOR, self.css_selectors[key])))
        except TimeoutException:
            self.browser.save_screenshot(path_save_errors + f"{key} wait_for error.png")
            logging.error(f"{key} failed", exc_info=False)
            return False
        return True

    def can_click(self, key: str):
        """
        Wait till an element can be clicked.

        Args:
            key: str
                CSS Selector key of element to click

        Returns: boolean
            if element can be clicked
        """
        try:
            WebDriverWait(driver=self.browser, timeout=default_timeout) \
                .until(expected_conditions.
                       element_to_be_clickable((By.CSS_SELECTOR, self.css_selectors[key])))
        except TimeoutException:
            # self.browser.save_screenshot(path_save_errors + f"{key} can_click error.png")
            logging.info(f"Can't click: {key}", exc_info=False)
            return False
        return True

    # def search_subject(self, city: str, state_code: str, subject: str):
    #     """
    #     Search maps for 'subject' in 'city', 'state_code'.
    #     Save results to table.
    #
    #     Args:
    #         city: str
    #             to search in
    #         state_code: str
    #             to search in
    #         subject: str
    #             to search for
    #     """
    #     businesses = []
    #     self.browser.get("https://www.google.com/maps")
    #
    #     try:  # TO SEARCH SUBJECT IN CITY, STATE
    #         search_box = self.browser.find_element_by_css_selector(self.css_selectors['SEARCH BOX'])
    #         search_button = self.browser.find_element_by_css_selector(self.css_selectors['SEARCH BUTTON'])
    #         # SEARCH CITY TO ORIENT MAP
    #         search_box.send_keys(city + ', ' + state_code)
    #         search_button.click()
    #     except (NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException) as e:
    #         self.browser.save_screenshot(
    #             path_save_errors + f"{city}, {state_code} search_maps search_box_button failure.png")
    #         logging.error("SEARCH BOX / BUTTON failed", exc_info=True)
    #         self.browser.get("https://www.google.com/maps")
    #         sleep(8)
    #     else:
    #         try:  # TO WAIT TILL PAGE IS FULLY LOADED
    #             WebDriverWait(driver=self.browser, timeout=default_timeout) \
    #                 .until(expected_conditions
    #                        .presence_of_element_located((By.CSS_SELECTOR, self.css_selectors['WIDGET & MAP'])))
    #             WebDriverWait(driver=self.browser, timeout=default_timeout) \
    #                 .until(expected_conditions
    #                        .presence_of_element_located((By.CSS_SELECTOR, self.css_selectors['CLEAR SEARCH'])))
    #         except TimeoutException as e:
    #             self.browser.save_screenshot(path_save_errors + f"{city}, {state_code} search_maps city WIDGET & MAP "
    #                                                        f"CLEAR_SEARCH timeout.png")
    #             logging.error("WIDGET & MAP / CLEAR SEARCH timeout", exc_info=False)
    #             self.browser.get("https://www.google.com/maps")
    #             sleep(8)
    #         else:  # CLEAR SEARCH BOX (APPEARS AFTER SEARCH BUTTON HAS BEEN PRESSED) & SEARCH SUBJECT
    #             self.browser.find_element_by_css_selector(self.css_selectors['CLEAR SEARCH']).click()
    #             search_box.send_keys(subject + ' near ' + city + ' ' + state_code)
    #             search_button.click()
    #             try:  # TO WAIT FOR MAP TO FULLY LOAD
    #                 WebDriverWait(driver=self.browser, timeout=default_timeout) \
    #                     .until(expected_conditions
    #                            .presence_of_element_located((By.CSS_SELECTOR, self.css_selectors['WIDGET & MAP'])))
    #             except TimeoutException as e:
    #                 self.browser.save_screenshot(path_save_errors + f"{city}, {state_code} search_maps subject WIDGET & MAP "
    #                                                            f"timeout.png")
    #                 logging.error("WIDGET & MAP timeout", exc_info=False)
    #                 self.browser.get("https://www.google.com/maps")
    #                 sleep(8)
    #             else:
    #                 try:  # TO WAIT FOR RESULTS TO FULLY LOAD
    #                     WebDriverWait(driver=self.browser, timeout=default_timeout) \
    #                         .until(expected_conditions
    #                                .presence_of_element_located((By.CSS_SELECTOR, self.css_selectors['RESULTS'])))
    #                 except TimeoutException:
    #                     self.browser.save_screenshot(
    #                         path_save_errors + f"{city}, {state_code} search_maps RESULTS timeout.png")
    #                     logging.error('RESULTS timeout', exc_info=False)
    #                 else:
    #                     while 1:  # RESET results VARIABLE BC OF ELEMENT STALENESS
    #                         results = self.browser.find_elements_by_css_selector(self.css_selectors['RESULTS'])
    #                         if results:
    #                             self.page_count += 1
    #                             businesses += self.iterate_businesses(city=city,
    #                                                                   state_code=state_code,
    #                                                                   businesses=results)
    #                             if self.page_count >= 25:
    #                                 sleep(60 * 60 * 4)  # SLEEP FOR 4 HRS AFTER COLLECTING 25 PAGES OF RESULTS
    #                                 self.page_count = 0
    #                         else:
    #                             break
    #                         try:
    #                             next_button = self.browser.find_element_by_css_selector(
    #                                 self.css_selectors['NEXT RESULTS PAGE'])
    #                         except (NoSuchElementException, ElementClickInterceptedException,
    #                                 ElementNotInteractableException):
    #                             break
    #                         else:
    #                             try:  # TO GO TO NEXT RESULTS PAGE IF IT EXISTS
    #                                 next_button.click()
    #                                 sleep(10)
    #                             except (NoSuchElementException, ElementClickInterceptedException,
    #                                     ElementNotInteractableException):
    #                                 break
    #     return businesses

    def search_subject(self, city: str, state_code: str, subject: str):
        """
        Search maps for 'subject' in 'city', 'state_code'.
        Save results to table.

        Args:
            city: str
                to search in
            state_code: str
                to search in
            subject: str
                to search for

        Returns: boolean
            if successful
        """
        businesses = []
        page_count = 0
        self.browser.get("https://www.google.com/maps")
        self.orient_map(city + ' ' + state_code)
        self.wait_for(key='WIDGET & MAP')

        if self.can_click(key='CLEAR SEARCH'):
            self.browser.find_element_by_css_selector(self.css_selectors['CLEAR SEARCH']).click()
            self.orient_map(subject + ' near ' + city + ' ' + state_code)
            self.wait_for('WIDGET & MAP')
            self.wait_for('RESULTS')
            results = self.browser.find_elements_by_css_selector(self.css_selectors['RESULTS'])

            while results:  # RESET results VARIABLE BC OF ELEMENT STALENESS
                page_count += 1
                businesses += self.iterate_businesses(city=city, state_code=state_code, businesses=results)

                if page_count >= 25:
                    sleep(60 * 60 * 4)  # SLEEP FOR 4 HRS AFTER COLLECTING 25 PAGES OF RESULTS
                    page_count = 0

                if self.can_click('NEXT RESULTS PAGE'):
                    self.next_page('NEXT RESULTS PAGE')
                    if self.wait_for('RESULTS'):
                        results = self.browser.find_elements_by_css_selector(self.css_selectors['RESULTS'])
                    else:
                        break
                else:
                    break

        return businesses

    def next_page(self, key: str):
        """
        go to next page of results.

        Args:
            key: str
                CSS Selector key of next element

        Returns: bool
            if next page was clicked
        """
        try:  # TO GO TO NEXT RESULTS PAGE IF IT EXISTS
            self.browser.find_element_by_css_selector(self.css_selectors[key]).click()
        except (NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException):
            return False
        return True

    def orient_map(self, location: str):
        """
        orient the map to the location ('city, state' or 'subject near city, state')

        Args:
            location: str
                to orient map

        Returns: boolean
            if successful
        """
        try:  # TO FIND SEARCH BOX & BUTTON
            search_box = self.browser.find_element_by_css_selector(self.css_selectors['SEARCH BOX'])
            search_button = self.browser.find_element_by_css_selector(self.css_selectors['SEARCH BUTTON'])
        except NoSuchElementException as e:
            self.browser.save_screenshot(path_save_errors + f"orient_map no such element error.png")
            logging.error("Failed to find search box/button", exc_info=False)
            return False

        try:  # TO SEARCH CITY TO ORIENT MAP
            search_box.send_keys(location)
            search_button.click()
        except (ElementClickInterceptedException, ElementNotInteractableException):
            self.browser.save_screenshot(path_save_errors + f"orient_map click error.png")
            logging.error("Failed to click search button", exc_info=False)
            return False
        return True

    # def iterate_businesses(self, city: str, state_code: str, businesses: [webelement, ...]):
    #     """
    #     iterate business entries and aggregate info
    #
    #     Args:
    #         city: str
    #         state_code: str
    #         businesses: [ webelement, ... ]
    #             google maps search results
    #     Returns: [(name, phone, url, city, state code), ...]
    #         business info list
    #     """
    #     results = []
    #
    #     for i in range(len(businesses)):
    #         biz = businesses.pop(i)
    #         if not biz.is_displayed() and i < 6:
    #             biz.location_once_scrolled_into_view
    #
    #         # IF AD THEN SKIP
    #         try:
    #             ad = biz.find_element_by_css_selector(self.css_selectors['AD'])
    #             if ad.is_displayed() and ad.is_enabled():
    #                 continue
    #             else:
    #                 raise NoSuchElementException()
    #         except NoSuchElementException:
    #             try:  # TO PROCESS BUSINESS SINCE IT WASN'T AN AD
    #                 biz.click()
    #                 sleep(2)
    #             except (ElementClickInterceptedException, ElementNotInteractableException, NoSuchElementException):
    #                 self.browser.save_screenshot(path_save_errors + f"{city}, {state_code} iterate_businesses biz_click.png")
    #                 logging.error('iterate_businesses -> biz.click() failed', exc_info=False)
    #                 continue
    #             else:
    #                 try:  # TO WAIT TILL BIZ PAGE IS FULLY LOADED
    #                     WebDriverWait(driver=self.browser, timeout=default_timeout) \
    #                         .until(expected_conditions
    #                                .presence_of_element_located((By.CSS_SELECTOR,
    #                                                              self.css_selectors['BUSINESS IMAGE'])))
    #                 except TimeoutException:  # HANDLE BIZ IMAGE LOADING TIMEOUT
    #                     self.browser.save_screenshot(
    #                         path_save_errors + f"{city}, {state_code}_iterate_businesses bizimg.png")
    #                     logging.error('BUSINESS IMAGE timed out', exc_info=False)
    #                     try:  # TO CLICK BACK BUTTON AFTER TIMEOUT ERROR
    #                         self.browser.find_element_by_css_selector(self.css_selectors['BACK TO RESULTS']).click()
    #                         sleep(3)
    #                     except (ElementClickInterceptedException, ElementNotInteractableException,
    #                             NoSuchElementException):
    #                         self.browser.save_screenshot(path_save_errors + f"{city}, {state_code} iterate_businesses "
    #                                                      f"back_button_click after biz img timeout.png")
    #                         logging.error('BACK TO RESULTS failed after BIZ IMAGE timeout', exc_info=False)
    #                         break
    #
    #                 # COLLECT BUSINESS INFO & ADD TO RESULTS
    #                 name = self.get_name()
    #                 url, phone = self.get_url_phone()
    #                 if name:
    #                     results.append((name, url, phone, city, state_code))
    #
    #                 try:  # TO GO BACK TO RESULTS
    #                     element = self.browser.find_element_by_css_selector(self.css_selectors['BACK TO RESULTS'])
    #                     actions = ActionChains(self.browser)
    #                     actions.move_to_element(element)
    #                     actions.click(element)
    #                     actions.perform()
    #                     sleep(3)
    #                 except (NoSuchElementException, ElementNotInteractableException,
    #                         ElementClickInterceptedException) as e:
    #                     self.browser.save_screenshot(path_save_errors + f"{city}, {state_code} iterate_businesses "
    #                                                                f"back_button_click.png")
    #                     logging.error('BACK TO RESULTS failed after gathering biz info', exc_info=False)
    #                     break
    #                 else:
    #                     try:  # TO RELOAD RESULTS LIST BC OF STALENESS
    #                         WebDriverWait(driver=self.browser, timeout=default_timeout) \
    #                             .until(expected_conditions
    #                                    .presence_of_element_located((By.CSS_SELECTOR, self.css_selectors['RESULTS'])))
    #                         businesses = self.browser.find_elements_by_css_selector(self.css_selectors['RESULTS'])
    #                     except TimeoutException:
    #                         self.browser.save_screenshot(path_save_errors + f"{city}, {state_code} iterate_businesses "
    #                                                                    f"RELOAD RESULTS timeout.png")
    #                         logging.error('RESULTS REFRESH timed-out')
    #                         break
    #     return results

    def iterate_businesses(self, city, state_code, businesses):
        results = []

        for i in range(len(businesses)):
            biz = businesses.pop(i)

            if not biz.is_displayed():
                biz.location_once_scrolled_into_view

            if self.ad_check(biz):
                continue

            count = 1
            while not biz.is_enabled():
                sleep(5)
                logging.info('while iterating businesses, waiting for biz to be enabled')
                count += 1
                if count > 11:
                    logging.error('biz was never enabled', exc_info=False)
                    break

            try:
                biz.click()
            except (ElementClickInterceptedException, ElementNotInteractableException, NoSuchElementException):
                self.browser.save_screenshot(path_save_errors + f"iterate_businesses biz_click.png")
                logging.error('iterate_businesses -> biz.click() failed', exc_info=False)
                continue

            img_loaded = self.wait_for('BUSINESS IMAGE')

            if not img_loaded:  # GO BACK TO RESULTS
                logging.error('BUSINESS IMAGE timed out', exc_info=False)
                # TODO : CREATE LOGIC FOR HANDLING A BUSINESS IMAGE LOADING DELAY / FAIL
                self.browser.execute_script("window.history.go(-1)")

            # COLLECT BUSINESS INFO & ADD TO RESULTS
            name = self.get_name()
            url, phone = self.get_url_phone()
            if name:
                results.append((name, url, phone, city, state_code))

            self.browser.execute_script("window.history.go(-1)")
            results_loaded = self.wait_for('RESULTS')
            if not results_loaded:
                logging.error('RESULTS REFRESH timed-out')
                self.browser.save_screenshot(path_save_errors +
                                             f"{city}, {state_code} iterate_businesses RELOAD RESULTS timeout.png")
                break

            businesses = self.browser.find_elements_by_css_selector(self.css_selectors['RESULTS'])

    def ad_check(self, listing: webelement):
        """
        Check if listing is an ad

        Args:
            listing: webelement
                that you want to check

        Returns: boolean
        """
        try:
            ad = listing.find_element_by_css_selector(self.css_selectors['AD'])
        except NoSuchElementException:
            return False

        if ad.is_displayed() and ad.is_enabled():
            return True
        else:
            return False

    def get_name(self):
        """ grab a business's name """
        name = None
        try:
            name_list = self.browser.find_element_by_css_selector(
                self.css_selectors['NAME']).get_property('innerText').split('-')
        except NoSuchElementException:
            logging.error("get_name()", exc_info=False)
        else:
            if len(name_list) >= 2:
                name_list.pop(-1)
            for i in name_list:
                if not name:
                    name = i.strip()
                else:
                    name = name + ' - ' + i.strip()
                    name.encode('utf8')

        return name

    def get_url_phone(self):
        """ grab a business's URL and Phone Number """
        phone = None
        url = None
        try:
            contact_info = self.browser.find_elements_by_css_selector("span.widget-pane-link")
        except NoSuchElementException:
            logging.error("business_info() contact_info failed", exc_info=False)
        else:
            # FIND PHONE NUMBER & URL IF EXISTS
            for e in contact_info:
                attr = e.get_property('innerText')
                if not url and '.com' in attr:
                    url = attr.strip()
                    url.encode('utf8')
                if not phone:
                    phone = re.search(r"^\(\d\d\d\) \d\d\d-\d\d\d\d", attr)
                    if phone:
                        phone = phone[0].strip()
                        phone.encode('utf8')

        return url, phone
