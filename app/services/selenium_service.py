import threading
import queue
import time
from datetime import datetime, timezone

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from app.services.crawler_logger_service import CrawlerLogger
from app.services.logger_service import LoggerService

crawler_logger = CrawlerLogger("finance_crawler", identifier="finance")
logger = LoggerService()


class SeleniumService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.__init__()
        return cls._instance

    def __init__(self):
        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run Chrome in headless mode
        chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
        chrome_options.add_argument("--no-sandbox")  # Bypass OS security model

        # Initialize ChromeDriver service
        self.service = Service()  # Assumes chromedriver is in PATH

        # Create WebDriver instance
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)

    def get_driver(self):
        return self.driver

    def __del__(self):
        # Ensure the WebDriver is properly closed when the service is destroyed
        if hasattr(self, "driver") and self.driver:
            self.driver.quit()


class RequestProcessor:
    def __init__(self):
        self.stock_symbols_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.results = []  # To store the results from the requests
        self.thread = threading.Thread(target=self._process_requests, daemon=True)

    def start(self):
        logger.info(
            f"Starting crawler process, {self.stock_symbols_queue.qsize()} requests in queue.",
            route="INTERNAL/RequestProcessor",
        )
        self.stop_event.clear()
        self.results.clear()  # Clear previous results before starting
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.thread.join()  # Wait for the processing thread to complete
        logger.info(
            f"Stopping crawler process, {len(self.results)} results.",
            route="INTERNAL/RequestProcessor",
        )

    def add_request(self, symbol):
        self.stock_symbols_queue.put(symbol)

    def get_results(self):
        return self.results

    def _process_requests(self):
        while not self.stop_event.is_set() or not self.stock_symbols_queue.empty():
            try:
                start_time = time.time()
                symbol = self.stock_symbols_queue.get(timeout=1)
                resp = self._fetch_stock_price(symbol, start_time)
                if resp is not None:
                    stock_price, timestamp = resp
                    self.results.append(
                        {
                            "symbol": symbol,
                            "price": stock_price,
                            "timestamp": timestamp,
                        }
                    )
                self.stock_symbols_queue.task_done()
            except queue.Empty:
                continue

    def _fetch_stock_price(self, symbol, start_time):
        selenium_service = SeleniumService()
        driver = selenium_service.get_driver()
        url = f"https://www.google.com/finance/quote/{symbol}"
        driver.get(url)

        try:
            # Wait up to 5 seconds for the stock price element to be present
            price_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@class="YMlKec fxKbKc"]')
                )
            )
            stock_price = price_element.text
            diff = float(time.time() - start_time)
            diff = round(diff, 2)

            crawler_logger.info(
                f"{stock_price} - {diff}s ",
                sub_identifier=symbol,
            )
            return stock_price, datetime.now(timezone.utc)
        except TimeoutException:
            diff = float(time.time() - start_time)
            diff = round(diff, 2)
            crawler_logger.error(
                f"TimeoutException - {diff}s ",
                sub_identifier=symbol,
            )
        except NoSuchElementException:
            diff = float(time.time() - start_time)
            diff = round(diff, 2)
            crawler_logger.error(
                f"NoSuchElementException - {diff}s ",
                sub_identifier=symbol,
            )
        except Exception as e:
            diff = float(time.time() - start_time)
            diff = round(diff, 2)
            crawler_logger.error(
                f"{str(e)} - {diff}s ",
                sub_identifier=symbol,
            )
