import pickle
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# ChromeプロファイルやCookie経由でログイン状態を復元する
def load_cookies(driver, cookie_path):
    with open(cookie_path, "rb") as f:
        cookies = pickle.load(f)
    for cookie in cookies:
        # Selenium 4.6以降は'domain'キー不要
        cookie.pop('sameSite', None)
        try:
            driver.add_cookie(cookie)
        except Exception:
            pass

def main():
    url = "https://app.plaud.ai/"
    cookie_path = "plaudai_cookies.pkl"
    html_save_path = "plaudai_dashboard.html"

    options = Options()
    # options.add_argument('--headless')  # headlessではcookie認証に失敗する場合があるためOFF
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    time.sleep(3)

    # Cookieをセットしてリロード
    load_cookies(driver, cookie_path)
    driver.refresh()
    time.sleep(5)

    # 適切なタイミングでダッシュボードに遷移しているか確認
    # 必要に応じて遷移待ちや追加クリックを実装
    
    # ページソース保存
    with open(html_save_path, "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print(f"ダッシュボードHTMLを {html_save_path} に保存しました。")

    driver.quit()

if __name__ == "__main__":
    main()