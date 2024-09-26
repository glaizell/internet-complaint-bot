from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
import time

load_dotenv()

X_TWITTER_EMAIL = os.getenv("X_TWITTER_EMAIL")
X_TWITTER_PASSWORD = os.getenv("X_TWITTER_PASSWORD")
DOWNLOAD = int(os.getenv("DOWNLOAD"))
UPLOAD = int(os.getenv("UPLOAD"))
NUMBER = os.getenv("NUMBER")


class InternetSpeedTwitterBot:
    def __init__(self):
        self.options = Options()
        self.options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        self.wait = WebDriverWait(self.driver, 10, poll_frequency=2)
        self.up = 0
        self.down = 0

    def get_internet_speed(self):
        self.driver.get("https://www.speedtest.net/")

        go_button = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//a[@role='button' and contains(@class, 'js-start-test')]"))
        )
        go_button.click()

        timeout = 120
        start_time = time.time()

        while True:
            try:

                self.down = self.wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".result-item-download .result-data-value.download-speed"))
                )
                self.up = self.wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".result-item-upload .result-data-value.upload-speed"))
                )

                if self.down.text and self.down.text != '—' and self.up.text and self.up.text != '—':
                    self.down = int(float(self.down.text))
                    self.up = int(float(self.up.text))
                    break

            except ValueError as ve:
                print(f"Could not convert speed to float: {ve}")

            except Exception as e:
                print(f"An error occurred while retrieving speeds: {e}")

            if time.time() - start_time > timeout:
                print("Timed out waiting for speed test results.")
                self.down, self.up = 0, 0
                break

        print(f"Download Speed: {self.down} Mbps")
        print(f"Upload Speed: {self.up} Mbps")

    def tweet_at_provider(self):
        self.driver.get("https://x.com/i/flow/login")

        input_element = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='text']")))
        input_element.send_keys(X_TWITTER_EMAIL)

        time.sleep(1)

        next_button = self.driver.find_element(By.XPATH, "//button[.//span[text()='Next']]")
        next_button.click()

        try:
            num_input_element = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[type='text'][name='text'][data-testid='ocfEnterTextTextInput']"))
            )
            if num_input_element:
                num_input_element.send_keys(NUMBER)

                next_button_element = self.wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "button[data-testid='ocfEnterTextNextButton'][type='button']"))
                )
                next_button_element.click()
        except Exception as e:
            print(f"Number input element not found or another issue occurred: {e}")

        password_input = self.wait.until(
            EC.presence_of_element_located((By.NAME, "password")))
        password_input.send_keys(X_TWITTER_PASSWORD)

        time.sleep(1)

        login_button = self.driver.find_element(By.CSS_SELECTOR, "button[data-testid='LoginForm_Login_Button']")
        login_button.click()

        if self.up < UPLOAD or self.down < DOWNLOAD:
            print(
                f"Conditions met for complaint: UPLOAD={UPLOAD}, self.up={self.up}, DOWNLOAD={DOWNLOAD}, self.down={self.down}")
            try:
                tweet_textarea = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='tweetTextarea_0']"))
                )
                tweet_textarea.send_keys(
                    f"Hey Internet Provider, I just ran a speed test, and I’m seeing {self.down} Mbps down and {self.up} Mbps up. That’s lower than the {DOWNLOAD} Mbps down and {UPLOAD} Mbps up that I’m paying for. Can you help me understand why?")

                time.sleep(1)

                tweet_button = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='tweetButtonInline']"))
                )
                tweet_button.click()
            except Exception as e:
                print(f"Error during tweeting: {e}")
        else:
            print(
                f"Conditions met for confirmation: UPLOAD={UPLOAD}, self.up={self.up}, DOWNLOAD={DOWNLOAD}, self.down={self.down}")
            try:
                tweet_textarea = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='tweetTextarea_0']"))
                )
                tweet_textarea.send_keys(
                    f"Hey Internet Provider, I just ran a speed test, and I’m seeing {self.down} Mbps down and {self.up} Mbps up. Everything seems fine, but I just want to confirm that I'm getting the service I'm paying for: {DOWNLOAD} Mbps down and {UPLOAD} Mbps up.")

                time.sleep(1)

                tweet_button = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='tweetButtonInline']"))
                )
                tweet_button.click()
            except Exception as e:
                print(f"Error during tweeting: {e}")

    def close_browser(self):
        self.driver.quit()


bot = InternetSpeedTwitterBot()
bot.get_internet_speed()
bot.tweet_at_provider()
bot.close_browser()
