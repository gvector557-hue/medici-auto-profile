import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ログインページ
LOGIN_URL = "https://medicihiroba.com/private_teacher/teacher/teacherNin4.php"
# 年齢変更ページ
CHANGE_URL = "https://medicihiroba.com/private_teacher/teacher/t_change.php"


def main():
    # ← GitHub Secrets に入れた値を読む
    username = os.environ["MEDICI_USER"]
    password = os.environ["MEDICI_PASSWORD"]

    # ヘッドレスChromeの設定（Actions用）
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    wait = WebDriverWait(driver, 15)

    try:
        # ❶ ログインページへ
        driver.get(LOGIN_URL)

        # メール欄が出るまで待つ
        wait.until(EC.presence_of_element_located((By.NAME, "emailaddress_teacherlogin")))

        # ❷ ログイン情報を入力
        driver.find_element(By.NAME, "emailaddress_teacherlogin").send_keys(username)
        driver.find_element(By.NAME, "password_teacherlogin").send_keys(password)
        driver.find_element(By.NAME, "Submit").click()

        # ログイン処理待ち
        time.sleep(2)

        # ❸ 年齢変更ページへ
        driver.get(CHANGE_URL)

        # ページ読み込み待ち
        wait.until(EC.presence_of_element_located((By.NAME, "submit")))
        # 多分このページは「確認」みたいなのがあって submit を1回押すっぽいので押す
        driver.find_element(By.NAME, "submit").click()

        # ❹ 年齢のselectが出るまで待つ
        wait.until(EC.presence_of_element_located((By.NAME, "age")))

        age_select_el = driver.find_element(By.NAME, "age")
        select_age = Select(age_select_el)

        # 今の選択値を読む
        current_age = select_age.first_selected_option.get_attribute("value")

        # 20 ↔ 21 でトグル
        next_age = "21" if current_age == "20" else "20"

        # ❺ 年齢を変更して送信
        select_age.select_by_value(next_age)
        driver.find_element(By.NAME, "submit").click()

        print(f"✅ 年齢を {current_age} → {next_age} に変更しました")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
