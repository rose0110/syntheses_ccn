from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import logging

logger = logging.getLogger(__name__)


class ElnetConnector:
    def __init__(self, username: str, password: str, headless: bool = True):
        self.username = username
        self.password = password
        self.headless = headless
        self.driver = None
        self.login_url = "https://www.elnet.fr/authentication"
    
    def setup_driver(self):
        """Configure le driver Chrome"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless=new')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Utiliser Chromium si Chrome n'est pas disponible (Docker)
        import shutil
        if shutil.which('chromium'):
            chrome_options.binary_location = '/usr/bin/chromium'
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        
        logger.info("Chrome driver initialized")
    
    def login(self) -> bool:
        try:
            logger.info("=== ÉTAPE 1: Page login ===")
            self.driver.get(self.login_url)
            time.sleep(3)
            
            # Screenshot étape 1
            self.driver.save_screenshot("debug_step1_login.png")
            logger.info("Screenshot: debug_step1_login.png")
            
            # ÉTAPE 1: Entrer le login et valider
            username_field = None
            username_selectors = [
                (By.NAME, "username"),
                (By.ID, "username"),
                (By.CSS_SELECTOR, "input[type='text']"),
                (By.CSS_SELECTOR, "input[type='email']")
            ]
            
            for by, selector in username_selectors:
                try:
                    username_field = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    logger.info(f"✓ Username field found: {by}={selector}")
                    break
                except:
                    continue
            
            if not username_field:
                logger.error("✗ Could not find username field")
                return False
            
            username_field.clear()
            username_field.send_keys(self.username)
            logger.info(f"✓ Username entered: {self.username}")
            time.sleep(1)
            
            # Cliquer sur "Valider" - essayer plusieurs méthodes
            validate_button = None
            validate_selectors = [
                (By.XPATH, "//button[contains(text(), 'Valider')]"),
                (By.XPATH, "//button[text()='Valider']"),
                (By.XPATH, "//input[@value='Valider']"),
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.CSS_SELECTOR, "button.btn-primary"),
                (By.XPATH, "//*[contains(@class, 'btn') and contains(text(), 'Valider')]"),
                (By.TAG_NAME, "button")  # Dernier recours
            ]
            
            for by, selector in validate_selectors:
                try:
                    buttons = self.driver.find_elements(by, selector)
                    for btn in buttons:
                        if 'valider' in btn.text.lower() or by == By.TAG_NAME:
                            validate_button = btn
                            logger.info(f"✓ Validate button found: {by}={selector}")
                            break
                    if validate_button:
                        break
                except:
                    continue
            
            if validate_button:
                validate_button.click()
                logger.info("✓ Clicked 'Valider'")
            else:
                # Fallback: appuyer sur Entrée
                logger.warning("Validate button not found, trying Enter key")
                from selenium.webdriver.common.keys import Keys
                username_field.send_keys(Keys.RETURN)
                logger.info("✓ Pressed Enter on username field")
            
            time.sleep(3)
            
            # Screenshot étape 2
            self.driver.save_screenshot("debug_step2_password.png")
            logger.info("Screenshot: debug_step2_password.png")
            
            logger.info("=== ÉTAPE 2: Page mot de passe ===")
            
            # ÉTAPE 2: Entrer le mot de passe
            password_field = None
            password_selectors = [
                (By.NAME, "password"),
                (By.ID, "password"),
                (By.CSS_SELECTOR, "input[type='password']"),
                (By.XPATH, "//input[@type='password']")
            ]
            
            for by, selector in password_selectors:
                try:
                    password_field = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    logger.info(f"✓ Password field found: {by}={selector}")
                    break
                except:
                    continue
            
            if not password_field:
                logger.error("✗ Could not find password field")
                return False
            
            password_field.clear()
            password_field.send_keys(self.password)
            logger.info("✓ Password entered")
            time.sleep(1)
            
            # Cliquer sur "Se connecter"
            login_button = None
            login_selectors = [
                (By.XPATH, "//button[contains(text(), 'Se connecter')]"),
                (By.XPATH, "//button[contains(text(), 'Connexion')]"),
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.CSS_SELECTOR, "button.btn-primary"),
                (By.XPATH, "//input[@value='Se connecter']")
            ]
            
            for by, selector in login_selectors:
                try:
                    login_button = self.driver.find_element(by, selector)
                    logger.info(f"✓ Login button found: {by}={selector}")
                    break
                except:
                    continue
            
            if not login_button:
                logger.error("✗ Could not find login button")
                return False
            
            login_button.click()
            logger.info("✓ Clicked 'Se connecter'")
            time.sleep(5)
            
            # Vérifier succès
            current_url = self.driver.current_url
            logger.info(f"Current URL: {current_url}")
            
            if "authentication" not in current_url and "login" not in current_url:
                logger.info("✓✓✓ Login successful!")
                return True
            else:
                logger.error("✗ Login failed - still on auth page")
                self.driver.save_screenshot("debug_login_failed.png")
                return False
                
        except Exception as e:
            logger.error(f"✗ Login error: {e}")
            try:
                self.driver.save_screenshot("debug_login_error.png")
            except:
                pass
            return False
    
    def get_page(self, url: str) -> str:
        try:
            self.driver.get(url)
            time.sleep(2)
            return self.driver.page_source
        except Exception as e:
            logger.error(f"Failed to get page {url}: {e}")
            return None
    
    def close(self):
        if self.driver:
            self.driver.quit()
            logger.info("Driver closed")
