import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

LOGIN_URL = "https://medicihiroba.com/private_teacher/teacher/teacherNin4.php"
CHANGE_URL = "https://medicihiroba.com/private_teacher/teacher/t_change.php"

def find_first_that_exists(driver, candidates, timeout=12):
    """
    candidates: [(By.NAME, "xxx"), (By.ID, "yyy"), ...] のリスト
    最初に見つかった要素を返す。どれも無ければ TimeoutException を投げる
    """
    end = time.time() + timeout
    last_exc = None
    while time.time() < end:
        for how, what in candidates:
            try:
                el = driver.find_element(how, what)
                return el
            except Exception as e:
                last_exc = e
        time.sleep(0.5)
    raise last_exc or Exception("element not found")

def main():
    username = os.environ["MEDICI_USER"]
    password = os.environ["MEDICI_PASSWORD"]

    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    # 見えないブロックを避けるためにUser-Agentと画面サイズも指定
    opts.add_argument("--window-size=1280,720")
    opts.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    )

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    wait = WebDriverWait(driver, 15)

    try:
        # ① ログインページ
        driver.get(LOGIN_URL)
        time.sleep(2)

        # ② メール欄をいくつかの候補で探す
        try:
            email_input = find_first_that_exists(
                driver,
                [
                    (By.NAME, "emailaddress_teacherlogin"),
                    (By.NAME, "email_teacherlogin"),
                    (By.NAME, "email"),
                    (By.ID, "emailaddress_teacherlogin"),
                ],
                timeout=12,
            )
        except Exception:
            # 見つからなかったときはデバッグ用に上のほう1000文字を出す
            print("ページに想定のinputが見つかりませんでした。以下は取得したHTMLの先頭です。")
            print(driver.page_source[:1000])
            raise

        # ③ パスワード欄も複数候補で
        password_input = find_first_that_exists(
            driver,
            [
                (By.NAME, "password_teacherlogin"),
                (By.NAME, "password"),
                (By.ID, "password_teacherlogin"),
            ],
            timeout=8,
        )

        email_input.send_keys(username)
        password_input.send_keys(password)

        # 送信ボタンも複数候補で
        submit_btn = find_first_that_exists(
            driver,
            [
                (By.NAME, "Submit"),
                (By.NAME, "submit"),
                (By.CSS_SELECTOR, "input[type='submit']"),
                (By.CSS_SELECTOR, "button[type='submit']"),
            ],
            timeout=6,
        )
        submit_btn.click()

        time.sleep(2)

        # ④ 年齢変更ページへ
        driver.get(CHANGE_URL)
        time.sleep(2)

        # 1回目の「次へ」的なsubmit
        try:
            first_submit = find_first_that_exists(
                driver,
                [
                    (By.NAME, "submit"),
                    (By.CSS_SELECTOR, "input[type='submit']"),
                ],
                timeout=6,
            )
            first_submit.click()
            time.sleep(2)
        except Exception:
            # もしこのページが無くていきなりageがあるならスキップ
            pass

        # ⑤ age select
        wait.until(EC.presence_of_element_located((By.NAME, "age")))
        age_select_el = driver.find_element(By.NAME, "age")
        select_age = Select(age_select_el)

        current_age = select_age.first_selected_option.get_attribute("value")
        next_age = "21" if current_age == "20" else "20"
        select_age.select_by_value(next_age)

        # 保存
        submit2 = find_first_that_exists(
            driver,
            [
                (By.NAME, "submit"),
                (By.CSS_SELECTOR, "input[type='submit']"),
            ],
            timeout=6,
        )
        submit2.click()

        print(f"✅ 年齢を {current_age} → {next_age} に変更しました")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
