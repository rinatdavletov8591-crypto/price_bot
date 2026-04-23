# wb_parser.py
import requests
from bs4 import BeautifulSoup
import time

def get_wb_price(url, retries=2, delay=2):
    """
    Получает цену товара на Wildberries по прямой ссылке с повторными попытками.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    for attempt in range(retries):
        try:
            # Устанавливаем connect_timeout и read_timeout
            response = requests.get(url, headers=headers, timeout=(5, 15))
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Более надежный поиск цены
            price_element = soup.find('span', class_='price-block__final-price')
            if not price_element:
                price_element = soup.find('ins', class_='price-block__final-price')
            if not price_element:
                price_element = soup.find('span', {'data-tag': 'salePrice'})
            
            if price_element:
                price_text = price_element.get_text(strip=True)
                price = int(''.join(filter(str.isdigit, price_text)))
                return price
            else:
                print(f"Не удалось найти цену на Wildberries (попытка {attempt+1}/{retries})")
                
        except requests.exceptions.Timeout:
            print(f"Тайм-аут при запросе к Wildberries (попытка {attempt+1}/{retries})")
        except Exception as e:
            print(f"Ошибка при парсинге Wildberries: {e}")
            
        if attempt < retries - 1:
            time.sleep(delay)
            
    return None