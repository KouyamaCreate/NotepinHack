from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pickle
import time

# Chromeのオプション設定
options = Options()
# options.add_argument("--headless") # デバッグのためGUI表示推奨
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

# WebDriverの初期化
driver = webdriver.Chrome(options=options)

# Plaud.aiのログインページを開く
login_url = "https://app.plaud.ai/"
dashboard_url = "https://app.plaud.ai/#/home/allRecording" # ダッシュボードURL（仮、要確認）
html_save_path = "plaudai_dashboard.html"
cookie_save_path = "plaudai_cookies.pkl"

try:
    driver.get(login_url)

    print("Googleログインが完了し、ダッシュボードが表示されるまで手動で操作してください。")
    input("ダッシュボード画面が表示されたら、Enterキーを押してください...")

    # --- Cookieを保存（念のため） ---
    cookies = driver.get_cookies()
    with open(cookie_save_path, "wb") as f:
        pickle.dump(cookies, f)
    print(f"Cookieを {cookie_save_path} に保存しました。")

    # --- ダッシュボードのHTMLを取得 ---
    # ログイン後、目的のURLにいるか確認し、必要なら遷移
    # 例: もしログイン後に別のページにいるなら driver.get(dashboard_url)
    # 現在のURLがダッシュボードであることを確認
    print(f"現在のURL: {driver.current_url}")
    print("ダッシュボードの内容を取得します...")

    # 念のため、ダッシュボードの主要な要素が表示されるまで待機
    # 例: 録音リストのコンテナ要素など（実際の要素に合わせて変更が必要）
    # wait = WebDriverWait(driver, 10)
    # try:
    #     wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".your-dashboard-container-selector"))) # 要調査・変更
    #     print("ダッシュボード要素の読み込みを確認しました。")
    # except Exception as e:
    #     print(f"ダッシュボード要素の待機中にタイムアウトまたはエラー: {e}")
    #     print("現在のページのHTMLを保存します。")

    # 少し待機してからHTMLを取得
    time.sleep(5) # ネットワーク遅延などを考慮

    # ページソース保存
    with open(html_save_path, "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print(f"現在のページのHTMLを {html_save_path} に保存しました。")

    # HTMLの内容を確認（最初の500文字）
    with open(html_save_path, "r", encoding="utf-8") as f:
        print("\n保存されたHTMLの先頭:")
        print(f.read(500))
        print("...")

except Exception as e:
    print(f"エラーが発生しました: {e}")

finally:
    driver.quit()
    print("ブラウザを終了しました。")