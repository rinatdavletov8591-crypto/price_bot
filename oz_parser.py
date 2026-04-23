# oz_parser.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import random
import re

def get_oz_price(query):
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        # Увеличиваем общий тайм-аут на загрузку страницы
        driver.set_page_load_timeout(60)
        
        search_url = f"https://www.ozon.ru/search/?text={query.replace(' ', '+')}&sorting=price_asc"
        driver.get(search_url)
        
        time.sleep(random.uniform(3, 5))
        
        # Увеличиваем время ожидания до 30 секунд
        wait = WebDriverWait(driver, 30)
        price_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-testid='price']")))
        
        price_text = price_element.text
        price = int(re.sub(r'[^\d]', '', price_text))
        return price

    except Exception as e:
        print(f"Ошибка при парсинге Ozon: {e}")
        return None

    finally:
        if driver:
            driver.quit()