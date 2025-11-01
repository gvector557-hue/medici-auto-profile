import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

LOGIN_URL = "https://medicihiroba.com/private_teacher/teacher/teacher.php"

def main():
    user = os.environ["MEDICI_USER"]
    password = os.environ["MEDICI_PASSWORD"]

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    try:
        driver.get(LOGIN_URL)
        time.sleep(2)

        # ① ログイン
        driver.find_element(By.NAME, "login_id").send_keys(user)
        driver.find_element(By.NAME, "login_pass").send_keys(password)
        driver.find_element(By.NAME, "login_submit").click()
        time.sleep(2)

        # ② 年齢を読む
        age_input = driver.find_element(By.NAME, "age")
        current_age = age_input.get_attribute("value")

        # ③ 20 ↔ 21 をトグル
        next_age = "21" if current_age == "20" else "20"
        age_input.clear()
        age_input.send_keys(next_age)

        # ④ 保存ボタン
        driver.find_element(By.NAME, "save").click()
        time.sleep(2)

        print(f"[OK] 年齢を {current_age} → {next_age} に変更しました。")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
