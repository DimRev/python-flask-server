import os
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
    _lock = threading.Lock()

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        chromedriver_path = os.path.expanduser(
            "~/chromedriver/chromedriver-linux64/chromedriver"
        )
        if not os.path.exists(chromedriver_path):
            crawler_logger.error(
                f"ChromeDriver not found at {chromedriver_path}",
                sub_identifier="Default",
            )
            raise FileNotFoundError(f"ChromeDriver not found at {chromedriver_path}")

        self.service = Service(
            executable_path=chromedriver_path, log_path="./chromedriver.log"
        )

        for attempt in range(3):
            try:
                self.driver = webdriver.Chrome(
                    service=self.service, options=chrome_options
                )
                crawler_logger.info(
                    "WebDriver started successfully", sub_identifier="Default"
                )
                break
            except Exception as e:
                crawler_logger.warning(
                    f"Retry {attempt + 1}: Failed to start WebDriver: {e}",
                    sub_identifier="Default",
                )
                time.sleep(2)
        else:
            crawler_logger.error(
                "Failed to start WebDriver after 3 retries", sub_identifier="Default"
            )
            raise RuntimeError("WebDriver initialization failed")

    def get_driver(self):
        return self.driver

    def close(self):
        if hasattr(self, "driver") and self.driver:
            self.driver.quit()
            self.driver = None  # Prevent reuse
            crawler_logger.info(
                "WebDriver closed successfully", sub_identifier="Default"
            )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class RequestProcessor:
    def __init__(self):
        self.stock_symbols_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.results = []
        self.results_lock = threading.Lock()
        self.thread = None  # Thread will be created when starting the process

    def start(self):
        if self.thread and self.thread.is_alive():
            logger.warning("Crawler process is already running.")
            return

        logger.info(
            f"Starting crawler process with {self.stock_symbols_queue.qsize()} requests."
        )
        self.stop_event.clear()
        self.results.clear()
        self.thread = threading.Thread(target=self._process_requests, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        # Wait for the queue to be emptied
        self.stock_symbols_queue.join()

        if self.thread:
            self.thread.join(timeout=5)
            if self.thread.is_alive():
                logger.warning("Crawler process did not shut down cleanly.")
            else:
                logger.info("Crawler process stopped.")
            self.thread = None  # Reset thread after stopping

    def add_request(self, symbol):
        self.stock_symbols_queue.put(symbol)

    def add_result(self, result):
        with self.results_lock:
            self.results.append(result)

    def get_results(self):
        with self.results_lock:
            return list(self.results)

    def _process_requests(self):
        while not self.stop_event.is_set() or not self.stock_symbols_queue.empty():
            try:
                symbol = self.stock_symbols_queue.get(timeout=1)
                result = self._fetch_stock_price(symbol, time.time())
                if result:
                    self.add_result(result)
                self.stock_symbols_queue.task_done()
            except queue.Empty:
                time.sleep(0.1)

    def _fetch_stock_price(self, symbol, start_time, retries=3):
        for attempt in range(retries):
            try:
                with SeleniumService() as selenium_service:
                    driver = selenium_service.get_driver()
                    crawler_logger.info(
                        f"Fetching URL: https://www.google.com/finance/quote/{symbol}",
                        sub_identifier="Default",
                    )
                    driver.get(f"https://www.google.com/finance/quote/{symbol}")
                    price_element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//*[@class="YMlKec fxKbKc"]')
                        )
                    )
                    stock_price = price_element.text
                    diff = round(time.time() - start_time, 2)
                    crawler_logger.info(
                        f"Fetched {symbol}: {stock_price} in {diff}s",
                        sub_identifier=symbol,
                    )
                    return {
                        "symbol": symbol,
                        "price": stock_price,
                        "timestamp": datetime.now(timezone.utc),
                    }
            except (TimeoutException, NoSuchElementException) as e:
                crawler_logger.warning(
                    f"Retry {attempt + 1} failed for {symbol}: {e}",
                    sub_identifier=symbol,
                )
                if attempt == retries - 1:
                    crawler_logger.error(
                        f"Failed to fetch {symbol} after {retries} retries.",
                        sub_identifier=symbol,
                    )
                    return None
            except Exception as e:
                crawler_logger.error(f"Unexpected error: {e}", sub_identifier=symbol)
                return None
