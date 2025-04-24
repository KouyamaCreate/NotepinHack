from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from dotenv import load_dotenv
import pickle
import time

# Chromeのオプション設定（必要に応じて変更）
load_dotenv()
options = Options()
# options.add_argument("--headless")  # GUIで操作するためコメントアウト
chrome_user_data_dir = os.environ.get("CHROME_USER_DATA_DIR")
chrome_profile_directory = os.environ.get("CHROME_PROFILE_DIRECTORY")
if chrome_user_data_dir:
    options.add_argument(f'--user-data-dir={chrome_user_data_dir}')
if chrome_profile_directory:
    options.add_argument(f'--profile-directory={chrome_profile_directory}')

# WebDriverのパスが必要な場合は明示的に指定
# driver = webdriver.Chrome(executable_path='chromedriverのパス', options=options)
driver = webdriver.Chrome(options=options)

# Plaud.aiのログインページを開く
driver.get("https://app.plaud.ai/")

print("Googleログインが完了するまで手動で操作してください。")
input("ログイン後、Enterキーを押してください...")

# Cookieを取得して保存
cookies = driver.get_cookies()
with open("plaudai_cookies.pkl", "wb") as f:
    pickle.dump(cookies, f)

print("Cookieをplaudai_cookies.pklに保存しました。")

driver.quit()