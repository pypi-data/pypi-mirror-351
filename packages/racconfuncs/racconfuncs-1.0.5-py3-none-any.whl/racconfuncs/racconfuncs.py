from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, JavascriptException, InvalidElementStateException
from selenium import webdriver
from urllib.parse import urlparse, urlunparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict
import os
import json
import requests
import threading
from queue import Queue
from itertools import cycle
from typing import Optional
import time
import math
import re

class Raccon:
    """Handles Raccon functionalities using Selenium WebDriver."""
    
    def QuietDriver(self, quiet = True):
        chrome_options = webdriver.ChromeOptions()
        if quiet: chrome_options.add_argument("--headless=new")
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--log-level=3')  # Only fatal errors
        chrome_options.add_argument('--disable-logging')  # Disables console logging
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-machine-learning-apis')  # Disables ML model execution
        chrome_options.add_argument('--disable-features=MachineLearningModelLoader,Tflite,XNNPACK')
        chrome_options.add_argument('--disable-machine-learning-model-loader')  # Prevents ML model loading
        prefs = {
            "profile.managed_default_content_settings.images": 2,  # 2 = Block
            "profile.default_content_setting_values.images": 2     # Ensures consistency
        }
        chrome_options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(options=chrome_options)
        
        return driver
    
    from urllib.parse import urlparse, urlunparse

    def urls_match(self, driver: webdriver, target_url):
        """
        Compare current URL with target URL.
        
        Args:
            driver: Selenium WebDriver instance
            target_url: The URL to compare against (str)
        
        Returns:
            bool: True if URLs match after normalization
        """
        def normalize_url(url: str):
            """Standardize URL for comparison"""
            return url.replace('e', '').replace('c', '').replace('/', '')

        current = normalize_url(driver.current_url)
        target = normalize_url(target_url)
        
        return current == target
    
    def execute_challenge(self):
        """Complete the hCaptcha cookie challenge"""
        try:
            # 1. Navigate to target URL
            # self.driver.get("https://accounts.hcaptcha.com/verify_email/68184514-b78d-597a-cabd-bc8841c594c3")
            self.driver.get("https://accounts.hcaptcha.com/verify_email/83225347-1ca7-439d-8157-ebdb83252a15")
            
            time.sleep(5)
            # 2. Wait for critical elements to load (with multiple fallbacks)
            WebDriverWait(self.driver, 15).until(
                lambda d: d.execute_script(
                    'return document.readyState === "complete" && '
                    'document.body.innerHTML.includes("Cookie")'
                )
            )

            # 3. Locate the Cookie button with multiple strategies
            cookie_button = None
            strategies = [
                (By.XPATH, "//button[contains(translate(., 'COOKIE', 'cookie'), 'cookie')]"),
                (By.XPATH, "//*[contains(text(), 'Cookie') and not(ancestor::*[contains(@style,'hidden')])]"),
                (By.CSS_SELECTOR, "button:contains('Cookie'), [onclick*='cookie']")
            ]

            for strategy in strategies:
                try:
                    cookie_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable(strategy))
                    break
                except TimeoutException:
                    continue

            if not cookie_button:
                raise NoSuchElementException("Cookie button not found with any strategy")

            # 4. Click using JavaScript to bypass potential overlays
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", cookie_button)
            time.sleep(0.5)  # Visual settling time
            self.driver.execute_script("arguments[0].click();", cookie_button)
            print("Successfully clicked Cookie button")

            # 5. Wait for cookies to be set
            time.sleep(2)  # Allow cookie operations to complete

            # 6. Export hcaptcha.com cookies with advanced filtering
            all_cookies = self.driver.get_cookies()
            hcaptcha_cookies = {
                'metadata': {
                    'exported_at': datetime.utcnow().isoformat() + 'Z',  # ISO 8601 format with UTC
                    'source_url': self.driver.current_url,
                    'user_agent': self.driver.execute_script("return navigator.userAgent;")
                },
                'cookies': [
                    {k: v for k, v in cookie.items() 
                    if k in ['name', 'value', 'domain', 'path', 'expiry']}
                    for cookie in all_cookies 
                    if 'hcaptcha.com' in cookie.get('domain', '')
                ]
            }

            # 7. Save with timestamp
            with open('hcaptcha_cookies.json', 'w') as f:
                json.dump(hcaptcha_cookies, f, indent=2, ensure_ascii=False, default=str)

            print(f"Exported {len(hcaptcha_cookies['cookies'])} cookies at {hcaptcha_cookies['metadata']['exported_at']}")
            return True

        except Exception as e:
            print(f"Challenge failed: {str(e)}")
            # Take debugging screenshot
            self.driver.save_screenshot('error_screenshot.png')
            return False
        
    def load_or_refresh_cookies(self, cookie_file='hcaptcha_cookies.json', force_refresh=False):
        """
        Load cookies from JSON file or refresh if stale (>12 hours old)
        
        Args:
            driver: Selenium WebDriver instance
            cookie_file: Path to cookie JSON file
            force_refresh: If True, always refresh cookies regardless of timestamp
        
        Returns:
            bool: True if cookies were loaded successfully
        """
        
        domain = "dashboard.hcaptcha.com"
        self.driver.get("https://dashboard.hcaptcha.com")
        current_url = self.driver.current_url
        if domain not in current_url:
            print(f"Error: Must be on {domain} to import cookies. Current URL: {current_url}")
            return False

        # Load cookies from file
        cookie_file = Path(__file__).parent / "hcaptcha_cookies.json"
        if not cookie_file.exists():
            print(f"Cookie file not found: {cookie_file}")
            return False

        try:
            with open(cookie_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cookies: List[Dict] = data.get('cookies', [])
                
                added = 0
                for cookie in cookies:
                    # Only add cookies for our target domain
                    if domain in cookie.get('domain', ''):
                        # Prepare cookie dict for Selenium
                        sel_cookie = {
                            'name': cookie['name'],
                            'value': cookie['value'],
                            'domain': cookie['domain'],
                            'path': cookie['path'],
                            'secure': cookie.get('secure', False),
                            'httpOnly': cookie.get('httpOnly', False)
                        }
                        
                        # Add expiry if present (convert to int if float)
                        if 'expiry' in cookie:
                            sel_cookie['expiry'] = int(cookie['expiry']) if isinstance(cookie['expiry'], float) else cookie['expiry']
                        
                        self.driver.add_cookie(sel_cookie)
                        added += 1
                
                print(f"Added {added} cookies for {domain}")
                return True
                
        except json.JSONDecodeError:
            print("Invalid JSON in cookie file")
            return False
        except KeyError as e:
            print(f"Missing required cookie field: {e}")
            return False
        except Exception as e:
            print(f"Error adding cookies: {e}")
            return False

    def __init__(self, driver: Optional[WebDriver] = None, quiet = True, logLevel = 1):
        """
        Initialize with a Selenium WebDriver instance.
        
        Args:
            driver (WebDriver): Active Selenium WebDriver (Chrome/Firefox/etc.)
        """
        if type(driver) is WebDriver: self.driver = driver
        else: self.driver = self.QuietDriver(quiet = quiet)
        
        self.logLevel = logLevel
        self.accountName = ""
        self.accountId = ""
        
        if self.logLevel >= 2: print("Ruarua.ru autofunction established.")
    
    def setLogLevel(self, logLevel):
        self.logLevel = logLevel

    def login(self, username: str, password: str) -> None:
        """
        Logs in using the provided credentials.
        
        Args:
            username (str): Username to input.
            password (str): Password to input.
        """
        
        if not self.urls_match(self.driver, "https://ruarua.ru/login/"):
            self.driver.get("https://ruarua.ru/login/")
        
        # Find elements
        login_box = self.driver.find_element(By.ID, "nam")
        psw_box = self.driver.find_element(By.ID, "pass")

        # Input credentials
        login_box.send_keys(username)
        psw_box.send_keys(password)
        
        self.accountId = username
        
        login_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.btn-primary[onclick*='initcaptcha']")))
        login_button.click()
        
        if self.logLevel >= 1: print(f"Attempting to log into account {self.accountId}...")
        
        while True:
            time.sleep(2)
            try: slider_btn = self.driver.find_element(By.CSS_SELECTOR, "div.control-btn.slideDragBtn")
            except:
                if self.logLevel >= 1: print("Login success!")
                break

            # Drag the slider horizontally
            actions = ActionChains(self.driver)
            actions.click_and_hold(slider_btn).move_by_offset(70, 0).release().perform()

            # Optional: Verify success (e.g., check for post-slider elements)
            # print("Slider dragged successfully!")
        
    def logout(self) -> None:
        WebDriverWait(self.driver, 10).until(lambda d: d.execute_script('return (document.readyState === "complete") && (typeof logout === "function");'))
        self.driver.execute_script("logout();")
        if self.logLevel >= 1: print(f"Logged out account {self.accountId}.")
        
    def quit(self) -> None:
        self.driver.quit()
        
    def createAccount(self, name: str, nick: str, password: str, email: str, pr = True):
        def is_valid_email(email: str) -> bool:
            return bool(re.fullmatch(r'^[a-zA-Z0-9.@]*$', email)) and email.endswith("@gmail.com")
        tempemail = ""
        driver = self.QuietDriver(quiet = True)
        
        if pr and self.logLevel >= 1: print("Creating account...")
        
        if email == "":
            temp = ""
            while True:
                driver.quit()
                driver = self.QuietDriver(quiet = True)
                driver.get("https://22.do/zh/inbox")
                time.sleep(3)
                mailHost = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, ".mb-0.text.text-email")
                    )
                )[0]
                tempemail = mailHost.text.strip()
                print(tempemail)
                print(is_valid_email(tempemail.strip()))
                if is_valid_email(tempemail.strip()): break
                
            print(tempemail)
        
        self.driver.get("https://ruarua.ru/register/")
            
        namebox = self.driver.find_element(By.ID, "nam")
        nickbox = self.driver.find_element(By.ID, "nam2")
        passbox = self.driver.find_element(By.ID, "pass")
        mailbox = self.driver.find_element(By.ID, "mail")
        
        namebox.send_keys(name)
        nickbox.send_keys(nick)
        passbox.send_keys(password)
        if email == "": mailbox.send_keys(tempemail)
        else: mailbox.send_keys(email)
        
        self.driver.execute_script("register();")
        
        if email == "":
            time.sleep(15)
            driver.find_element(By.ID, "refresh").click()
            mailList = driver.find_element(By.CSS_SELECTOR, "tbody")
            mailList = mailList.find_elements(By.XPATH, "./*")
            if len(mailList) == 0: self.createAccount(name, nick, password, "", pr = False)
            else:
                mailList = mailList[0].find_elements(By.XPATH, "./*")[0]
                mailList.click()
                
                pattern = r'https://ruarua\.ru/verify\?key=[a-zA-Z0-9\-_]+'
                found_urls = set()
                
                def search_in_frame(frame=None):
                    """Search in current frame context"""
                    nonlocal found_urls
                    if frame:
                        driver.switch_to.frame(frame)
                    
                    html = driver.page_source
                    matches = re.findall(pattern, html)
                    found_urls.update(matches)
                    
                    iframes = driver.find_elements(By.TAG_NAME, "iframe")
                    for iframe in iframes:
                        search_in_frame(iframe)
                        driver.switch_to.parent_frame()
                
                search_in_frame()
                driver.switch_to.default_content()
                
                key = found_urls.pop()
                driver.get(key)
        
        if pr & self.logLevel >= 1: print(f"Account {name} generated!")

    def auto_fight(self):
        url_path = self.driver.current_url
        valid_paths = ["/e/mob", "/e/limit", "/e/boss", "/mob", "/limit", "/boss",
                        "/e/mob/", "/e/limit/", "/e/boss/", "/mob/", "/limit/", "/boss/",]
        
        print('x')

        # Proceed only if path matches
        if not any(url_path.endswith(path) for path in valid_paths):
            return
        
        print('y')

        # Don't add button if already exists
        try:
            self.driver.find_element(By.ID, "autofightbtn")
            return
        except NoSuchElementException:
            pass
        
        print('z')
        # Create the button via JS
        self.driver.execute_script("""
            var newButton = document.createElement("button");
            newButton.id = "autofightbtn";
            newButton.className = "btn btn-primary numchange";
            newButton.style.backgroundColor = "#be6cde";
            newButton.innerHTML = "Fight Until Win";
            document.getElementById("fightbtn").parentNode.appendChild(newButton);
        """)
        print('v')

        # Main fight logic
        def fight_until_win():
            keep_clicking = True
            self.clicking = True
            
            print('w')

            def click_fight_button():
                nonlocal keep_clicking
                if not keep_clicking:
                    return
                try:
                    fight_btn = self.driver.find_element(By.ID, "fightbtn")
                    fight_btn.click()
                except NoSuchElementException:
                    keep_clicking = False
                    self.clicking = False
                    return
                time.sleep(0.5)
                check_game_status()

            def check_game_status():
                nonlocal keep_clicking
                try:
                    ans_elem = self.driver.find_element(By.ID, "ans")
                    ans_text = ans_elem.text.strip()
                except NoSuchElementException:
                    ans_text = ""

                if "Wait some seconds!" in ans_text or "Wait a moment!" in ans_text:
                    time.sleep(8)
                    click_fight_button()
                elif "The server is having trouble" in ans_text or "Battle failed!" in ans_text:
                    time.sleep(1)
                    click_fight_button()
                elif "Battling" in ans_text:
                    time.sleep(0.5)
                    check_game_status()
                elif any(msg in ans_text for msg in [
                    "Attack successful!",
                    "You have already defeated this wave of mobs",
                    "You defeated a mob and get",
                    "The damage you caused is too little",
                    "At least 2 stamina is required"
                ]):
                    keep_clicking = False
                    self.driver.execute_script("""
                        var btn = document.getElementById("autofightbtn");
                        if (btn) {
                            btn.style.backgroundColor = "#be6cde";
                            btn.textContent = "Fight Until Win";
                        }
                    """)
                else:
                    time.sleep(0.5)
                    check_game_status()

            # Update the button to "Stop Fighting"
            self.driver.execute_script("""
                var btn = document.getElementById("autofightbtn");
                if (btn) {
                    btn.textContent = "Stop Fighting";
                    btn.style.backgroundColor = "#ff7979";
                }
            """)

            # Monitor the button for user click to stop fighting
            while keep_clicking:
                click_fight_button()

        # Simulate button click to start fight loop
        fight_until_win()

            

    def rua(self, ruaid: str | list [str], capacity = 5) -> None:
        """
        Ruas players using provided ruaid.
        
        Args:
            ruaid (str): Username to input.
            capacity (int): Max rua capacity for the account.
        """
        print("Ruaruaing...")
        if type(ruaid) is str: ruaid = [ruaid]
        count = 0
        for id in ruaid:
            self.driver.get(f"https://ruarua.ru/user/?rua={id}")
            if self.logLevel >= 2: print(f"Rua {id} ...", end = "")
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            WebDriverWait(self.driver, 10).until(lambda d: d.execute_script('return (document.readyState === "complete") && (typeof doit === "function");'))
            self.driver.execute_script("doit();")
            try:
                # Wait for element to be present and have non-empty text
                ans_element = WebDriverWait(self.driver, 10).until(
                    lambda d: d.find_element(By.ID, "ans") if d.find_element(By.ID, "ans").text.strip() else False
                )
                
                # Check text pattern using regex
                match = re.match(r"Done! He/She got Coin x (\d+)", ans_element.text.strip())
                if match:
                    count += 1
                    if self.logLevel == 2: print(f"Success!")
                    elif self.logLevel >= 3:
                        coin_count = int(re.search(r"\d+", ans_element.text).group())
                        print(f"Success (Coin x {coin_count})!")
                elif self.logLevel >= 2: print(f"Failed!")
                    
            except TimeoutException:
                if self.logLevel >= 2: print(f"Unable to load.")
            except Exception as e:
                print(f"Error occurred: {str(e)}")
            time.sleep(0.1)
            if count >= capacity: break
        self.driver.get("https://ruarua.ru/")
        if self.logLevel >= 1: print("Ruarua finished!")
    def follow(self, ruaid: str | list [str]) -> None:
        """
        Follow players using provided ruaid.
        
        Args:
            ruaid (str): Username to input.
        """
        if self.logLevel >= 1: print("Following...")
        if type(ruaid) is str: ruaid = [ruaid]
        for id in ruaid:
            if self.logLevel >= 2: print(f"Follow {id} ...")
            id = id.replace("-", '').upper()
            self.driver.get(f"https://ruarua.ru/user/?rua={id}")
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            WebDriverWait(self.driver, 10).until(lambda d: d.execute_script('return (document.readyState === "complete") && (typeof dofollow === "function");'))
            self.driver.execute_script(f"dofollow('{id}');")
            time.sleep(0.5)
        self.driver.get("https://ruarua.ru/")
        if self.logLevel >= 1: print("Following finished!")
    def getRuaList(self, ruaid: str) -> list[str]:
        """
        Returns the list of players who ruaed the given player.
        
        Args:
            ruaid (str): Username to input.
        """
        if not self.urls_match(self.driver, f"https://ruarua.ru/user/?rua={ruaid}"):
            self.driver.get(f"https://ruarua.ru/user/?rua={ruaid}")
        try:
            if self.logLevel >= 2: print(f"Fetching rua list for user {ruaid}...")
            # Locate the header div by exact text
            header_text = "↓ These people ruaruaed him/her today ↓"
            header = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//div[contains(., '{header_text}')]")))
            
            # Find the immediately following table
            table = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//div[contains(., '{header_text}')]/following-sibling::table[1]")))
            
            # Get all rows from tbody
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
            
            hrefs = []
            for row in rows:
                try:
                    # Get first td's anchor href
                    first_td = row.find_element(By.XPATH, "./td[1]")
                    anchor = first_td.find_element(By.TAG_NAME, "a")
                    href = anchor.get_attribute("href")
                    if href:
                        hrefs.append(href)
                except NoSuchElementException:
                    continue  # Skip rows without anchors
            
            for i in range (len(hrefs)): hrefs[i] = hrefs[i].split('=')[1]
            if self.logLevel >= 2: print("Rua list fetched successfully!")
            if self.logLevel >= 3: print(hrefs)
            return hrefs
        except TimeoutException:
            if self.logLevel >= 2: print("Timed out waiting for table elements to load")
            raise
        except NoSuchElementException as e:
            print(f"Required element not found: {str(e)}")
            raise
        
    def getFollowList(self) -> tuple:
        """
        Returns the following and follower list of the current player.
        
        Returns:
            folist (tuple (list[str], list[str])): Following and Follower list of the player.
        """
        if not self.urls_match(self.driver, "https://ruarua.ru/folist/"):
            self.driver.get(f"https://ruarua.ru/folist/")
        Following = []
        Follower = []
        try:
            if self.logLevel >= 2: print(f"Fetching following list...")
            # Locate the header div by exact text
            header_text = "Following List"
            header = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//h5[contains(., '{header_text}')]")))
            
            # Find the immediately following table
            table = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//h5[contains(., '{header_text}')]/following-sibling::table[1]")))
            
            # Get all rows from tbody
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
            
            hrefs = []
            for row in rows:
                try:
                    # Get first td's anchor href
                    first_td = row.find_element(By.XPATH, "./td[1]")
                    anchor = first_td.find_element(By.TAG_NAME, "a")
                    href = anchor.get_attribute("href")
                    if href:
                        hrefs.append(href)
                except NoSuchElementException:
                    continue  # Skip rows without anchors
            
            for i in range (len(hrefs)): hrefs[i] = hrefs[i].split('=')[1]
            Following = hrefs
            if self.logLevel >= 3: print(Following)
        except TimeoutException:
            print("Timed out waiting for table elements to load")
            raise
        except NoSuchElementException as e:
            print(f"Required element not found: {str(e)}")
            raise
        try:
            # Locate the header div by exact text
            header_text = "Follower List"
            header = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//h5[contains(., '{header_text}')]")))
            
            # Find the immediately following table
            table = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//h5[contains(., '{header_text}')]/following-sibling::table[1]")))
            
            # Get all rows from tbody
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
            
            hrefs = []
            for row in rows:
                try:
                    # Get first td's anchor href
                    first_td = row.find_element(By.XPATH, "./td[1]")
                    anchor = first_td.find_element(By.TAG_NAME, "a")
                    href = anchor.get_attribute("href")
                    if href:
                        hrefs.append(href)
                except NoSuchElementException:
                    continue  # Skip rows without anchors
            
            for i in range (len(hrefs)): hrefs[i] = hrefs[i].split('=')[1]
            Follower = hrefs
            if self.logLevel >= 3: print(Follower)
        except TimeoutException:
            print("Timed out waiting for table elements to load")
            raise
        except NoSuchElementException as e:
            print(f"Required element not found: {str(e)}")
            raise
        
        if self.logLevel >= 2: print("Following list fetched successfully!")
        return (Following, Follower)


    def dailycard(self) -> None:
        """
        Get the dailycard for the player.
        """
        if self.logLevel >= 1: print("Getting dailycard...")
        if not self.urls_match(self.driver, "https://ruarua.ru/dailycard/"):
            self.driver.get("https://ruarua.ru/dailycard/")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        WebDriverWait(self.driver, 10).until(lambda d: d.execute_script('return (document.readyState === "complete") && (typeof dailycard === "function");'))
        self.driver.execute_script("dailycard();")
        if self.logLevel >= 1: print("Dailycard done!")
    def sign(self) -> None:
        """
        Sign in for the player.
        
        Caution: You must collect dailycard before signing!
        
        Please leave the server with some time processing your dailycard request.
        """
        if self.logLevel >= 1: print("Signing...")
        try:
            if not self.urls_match(self.driver, "https://ruarua.ru/sign/"):
                self.driver.get("https://ruarua.ru/sign/")
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            WebDriverWait(self.driver, 10).until(lambda d: d.execute_script('return (document.readyState === "complete") && (typeof doit === "function");'))
            self.driver.execute_script("doit();")
        except Exception as e: print(f"Error: {e}")
        if self.logLevel >= 1: print("Signing done!")
    def newsign(self) -> None:
        """
        New-Player Sign in for the player.
        """
        if self.logLevel >= 1: print("Newsigning...")
        try:
            if not self.urls_match(self.driver, "https://ruarua.ru/newsign/"):
                self.driver.get("https://ruarua.ru/newsign/")
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            WebDriverWait(self.driver, 10).until(lambda d: d.execute_script('return (document.readyState === "complete") && (typeof newsign === "function");'))
            self.driver.execute_script("newsign();")
        except Exception as e: print(f"Error: {e}")
        if self.logLevel >= 1: print("Newsigning done!")
    def tree(self) -> None:
        """
        Collect tree power for the player.
        """
        if self.logLevel >= 1: print("Collecting tree power...")
        if not self.urls_match(self.driver, "https://ruarua.ru/power/"):
            self.driver.get("https://ruarua.ru/power/")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        WebDriverWait(self.driver, 10).until(lambda d: d.execute_script('return (document.readyState === "complete") && (typeof doit === "function");'))
        self.driver.execute_script("doit();")
        if self.logLevel >= 1: print("Tree energy collected!")
    def reap(self) -> None:
        """
        Collect tree power for the player.
        """
        if self.logLevel >= 1: print("Redeeming card rewards...")
        if not self.urls_match(self.driver, "https://ruarua.ru/docard/"):
            self.driver.get("https://ruarua.ru/docard/")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        WebDriverWait(self.driver, 10).until(lambda d: d.execute_script('return (document.readyState === "complete") && (typeof doit === "function");'))
        self.driver.execute_script("doit();")
        if self.logLevel >= 1: print("Card rewards collected!")
        
    def chooseWorld(self, world: str) -> None:
        if self.logLevel >= 1: print(f"Selecting world {world}...")
        if not self.urls_match(self.driver, "https://ruarua.ru/world/"):
            self.driver.get("https://ruarua.ru/world/")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        WebDriverWait(self.driver, 10).until(lambda d: d.execute_script('return (document.readyState === "complete") && (typeof chooseworld === "function");'))
        self.driver.execute_script(f"chooseworld('{world}');")
        if self.logLevel >= 1: print(f"World {world} chosen.")
        
    def claimWorldReward(self):
        """
        Claim all world rewards for the player.
        """
        if self.logLevel >= 1: print("Claiming world rewards...")
        success_message = "There are currently no rewards that can be claimed qwq"
        
        if not self.urls_match(self.driver, "https://ruarua.ru/reward/"):
            self.driver.get("https://ruarua.ru/reward/")
        
        for i in range(50):
            try:
                self.driver.execute_script("rewardworld();")
                try:
                    ans_element = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, 'ans')))
                    if ans_element.text.strip() == success_message: break
                    elif self.logLevel >= 3: print(f"{ans_element.text.strip()}")
                    elif self.logLevel >= 2: print(f"World reward claimed...")
                    
                except TimeoutException:
                    print("'ans' element not found within timeout")
                    
                time.sleep(1.1)
                
            except JavascriptException as e:
                break
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                break
        if self.logLevel >= 1: print("World reward collected.")
        
        
    def claimAchievement(self) -> None:
        """
        Claim all achievements for the player.
        """
        if self.logLevel >= 1: print("Claiming achievements...")
        if not self.urls_match(self.driver, "https://ruarua.ru/achievement/"):
            self.driver.get("https://ruarua.ru/achievement/")
        locators = [
            (By.XPATH, "//*[text()='Claim']"),  # Exact text match
            (By.CSS_SELECTOR, "[value='Claim']"),  # Input buttons
            (By.CSS_SELECTOR, "button:contains('Claim')")  # jQuery-style (if supported)
        ]   
        clicked_elements = 0
            
        for locator in locators:
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(locator)
                )
                elements = self.driver.find_elements(*locator)
                
                for element in elements:
                    try:
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                        WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable(element)
                        )
                        
                        self.driver.execute_script("arguments[0].click();", element)
                        clicked_elements += 1
                        print(f"Clicked Claim element: {element.tag_name}")
                        
                        # Small delay between clicks
                        time.sleep(0.2)
                        
                    except (StaleElementReferenceException, NoSuchElementException):
                        continue
                        
            except TimeoutException:
                continue
        if self.logLevel >= 1: print("Achievement Claimed!")
    
    def claimQuestReward(self):
        """
        Claim all quest rewards for the player.
        """
        if self.logLevel >= 2: print("Claiming daily quest rewards...")
        elif self.logLevel >= 1: print("Claiming quest rewards...")
        success_message = "Today's quest rewards have been collected."
        success_message_2 = "This week's quest rewards have been collected."
        fail_message = "You can't claim the next reward yet"
        
        if not self.urls_match(self.driver, "https://ruarua.ru/quest/"):
            self.driver.get("https://ruarua.ru/quest/")
        
        for i in range(3):
            try:
                self.driver.execute_script("rewardquest(1);")
                try:
                    ans_element = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, 'ans')))
                    if ans_element.text.strip() == success_message: break
                    elif ans_element.text.strip() == fail_message: break
                    elif self.logLevel >= 3: print(f"{ans_element.text.strip()}")
                    
                except TimeoutException:
                    print("'ans' element not found within timeout")
                    
                time.sleep(2)
                
            except JavascriptException as e:
                break
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                break
        if self.logLevel >= 2: print("Daily quest rewards collected.")
        time.sleep(2)
        if self.logLevel >= 2: print("Claiming weekly quest rewards...")
        for i in range(7):
            try:
                self.driver.execute_script("rewardquest(2);")
                try:
                    ans_element = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, 'ans')))
                    if ans_element.text.strip() == success_message_2: break
                    elif ans_element.text.strip() == fail_message: break
                    elif self.logLevel >= 3: print(f"{ans_element.text.strip()}")
                    
                except TimeoutException:
                    print("'ans' element not found within timeout")
                    
                time.sleep(2)
                
            except JavascriptException as e:
                break
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                break
        if self.logLevel >= 2: print("Weekly quest reward collected.")
        elif self.logLevel >= 1: print("Quest reward collected.")
        
    def checkBoss(self, timeout = 10) -> dict:
        """
        Checks boss status.
        
        Note that the method is executed entirely on frontend.
        """
        if self.logLevel >= 1: print("Checking boss status...")
        
        # if not self.urls_match(self.driver, "https://ruarua.ru/boss/"):
        self.driver.get("https://ruarua.ru/boss/")
            
        try:
            # Wait for the element with ID starting with "nowheal"
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[id^='nowheal']"))
            )
            
            bossHpText = str(self.driver.execute_script("return arguments[0].parentNode.innerText;", element))
            print(bossHpText)
            
            bossHealth = int(bossHpText.strip().split("/")[0].strip())
            bossTotalHealth = int(bossHpText.strip().split("/")[1].strip())
            
            countdown_boss = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#countdown_boss"))
            )
            stamex = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#stamex"))
            )
            
            m, s = countdown_boss.text.strip().split(":")
            m = int(m.strip())
            s = int(s.strip())
            stam_time = m * 60 + s
            stamex = stamex.text.replace(' ', '').replace('+', '')
            try: stamex = int(stamex) | 0
            except: stamex = 0
            
            staminaTime = stam_time
            stamina = 6 - math.ceil(stam_time / 60) + stamex
            
            
        except TimeoutException:
            print(f"Error: Timeout when locating boss information.")
        except NoSuchElementException:
            print("Error: Could not locate boss information.")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            
        if self.logLevel >= 1: print("Boss status checked.")
        if self.logLevel >= 3: print(f"Boss health: {bossHealth}/{bossTotalHealth}, Stamina: {stamina}, Stamina time: {staminaTime}")
        
        return {'bossHealth': bossHealth, 'bossTotalHealth': bossTotalHealth, 'stamina': stamina, 
                'staminaTime': staminaTime}
        
    def hitBoss(self):
        """
        Attacks the boss.
        
        Note that the method is executed entirely on frontend.
        """
        if self.logLevel >= 1: print("Attacking boss...")
        
        self.driver.get("https://ruarua.ru/boss/")
        
        self.auto_fight()
        
        self.driver.execute_script("document.getElementById(\"autofightbtn\").click()")
        
        while(1):
            if not self.clicking: break
        
        
    def sendMessage(self, message: str, timeout=10):
        """
        Sends a message to an element with id="message" after ensuring it's present and interactable.
        
        Args:
            driver: Selenium WebDriver instance
            message: Text to send (str)
            timeout: Maximum wait time in seconds (default: 10)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            message_input = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.ID, "message"))
            )
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.ID, "message"))
            )
            time.sleep(1)
            message_input.send_keys(message)
            self.driver.execute_script("send();")
            
            if self.logLevel >= 1: print(f"Successfully sent message: {message}")
            return True
            
        except TimeoutException:
            print(f"Timeout: Element with id='message' not found within {timeout} seconds")
        except NoSuchElementException:
            print("Element with id='message' does not exist")
        except InvalidElementStateException:
            print("Element with id='message' is not interactable")
        except Exception as e:
            print(f"Unexpected error while sending message: {str(e)}")
        
        return False
    def redeemCode(self, ListOfCode: str | list [str]) -> None:
        """
        Redeem Code using provided ruaid.
        
        Args:
            ListOfCode (str): Username to input.
        """
        if self.logLevel >= 1: print("Redeeming code...")
        if not self.urls_match(self.driver, "https://ruarua.ru/code/"):
            self.driver.get("https://ruarua.ru/code/")
        
        if type(ListOfCode) is str: ListOfCode = [ListOfCode]
        
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        WebDriverWait(self.driver, 10).until(lambda d: d.execute_script('return (document.readyState === "complete") && (typeof initcaptcha === "function");'))
        
        for code in ListOfCode:
            code_box = self.driver.find_element(By.ID, "codee")
            code_box.send_keys(code)
            self.driver.execute_script("initcaptcha();")
            while True:
                time.sleep(2)
                try: slider_btn = self.driver.find_element(By.CSS_SELECTOR, "div.control-btn.slideDragBtn")
                except:
                    print("Redeem success!")
                    break

                # Drag the slider horizontally
                actions = ActionChains(self.driver)
                actions.click_and_hold(slider_btn).move_by_offset(70, 0).release().perform()

                # Optional: Verify success (e.g., check for post-slider elements)
                # print("Slider dragged successfully!")
    
    
    
class ProxyRotator:
    def __init__(self, proxy_list, max_threads=5):
        self.proxy_list = proxy_list
        self.max_threads = max_threads
        self.timeout = 5
        self.result_queue = Queue()
        self.lock = threading.Lock()
        
    def _is_proxy_working(self, proxy):
        """Check if proxy is reachable."""
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        try:
            test_url = "http://httpbin.org/ip"
            response = requests.get(test_url, proxies=proxies, timeout=self.timeout)
            return response.status_code == 200
        except:
            return False
    
    def _test_proxy_in_browser(self, proxy):
        """Test proxy in actual browser and return driver if successful."""
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument(f"--proxy-server={proxy}")
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.get("http://httpbin.org/ip")
            time.sleep(1)
            if proxy.split(":")[0] in driver.page_source:
                with self.lock:
                    if self.result_queue.empty():  # Only keep first successful driver
                        print(f"Found working proxy: {proxy}")
                        self.result_queue.put(driver)
                        return
            driver.quit()
        except Exception as e:
            print(f"Proxy {proxy} failed in browser: {str(e)}")
    
    def get_proxied_driver(self):
        """Returns a Chrome driver with the next working proxy using multithreading."""
        threads = []
        
        # Create and start threads for each proxy
        for proxy in self.proxy_list:
            print(1)
            if not self.result_queue.empty():
                break  # Stop if we already found a working proxy
                
            if not self._is_proxy_working(proxy):
                continue  # Skip proxies that fail basic connectivity check
                
            t = threading.Thread(
                target=self._test_proxy_in_browser,
                args=(proxy,)
            )
            threads.append(t)
            t.start()
            
            # Limit number of concurrent threads
            while len(threads) >= self.max_threads:
                for t in threads[:]:
                    if not t.is_alive():
                        threads.remove(t)
                time.sleep(0.1)
        
        # Wait for remaining threads to complete
        for t in threads:
            t.join()
        
        if not self.result_queue.empty():
            return self.result_queue.get()
        
        raise Exception("No working proxies available")