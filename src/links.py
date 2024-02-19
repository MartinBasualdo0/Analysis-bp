from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
import time

class Scraper:
    def __init__(self, headless=True):
        self.driver = None
        self.headless = headless

    def start_driver(self, link: str):
        if self.driver is None:
            service = Service(ChromeDriverManager().install())
            download_folder = os.path.join(os.getcwd(), "data")
            prefs = {
                'download.default_directory': download_folder,
                "directory_upgrade": True
            }
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_experimental_option("prefs", prefs)
            if self.headless:
                chrome_options.add_argument("--headless")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.maximize_window()

        self.driver.get(link)
        return self.driver

    def wait_for_downloads_to_complete(self, timeout: int):
        start_time = time.time()
        while not self.every_downloads_chrome():
            if time.time() - start_time > timeout:
                print('Timeout elapsed, stopping downloads')
                break
            time.sleep(1)

    def every_downloads_chrome(self):
        download_folder = os.path.join(os.getcwd(), "data")
        incomplete_downloads = [name for name in os.listdir(download_folder) if name.endswith('.tmp')]
        return not incomplete_downloads



def scrape_links_bp(scraper: Scraper):
    scraper.start_driver("https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-35-45")
    xlsx_div = WebDriverWait(scraper.driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'a-color2'))
    )
    hrefs = []
    for element in xlsx_div:
        href = element.get_attribute('href')
        if href is not None and href.endswith("xls"):
            hrefs.append(href)

    scraper.driver.quit()
    return hrefs
