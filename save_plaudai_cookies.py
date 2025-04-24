from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from dotenv import load_dotenv

def save_plaudai_tokenstr():
    # Chromeのオプション設定
    load_dotenv()
    options = Options()
    chrome_user_data_dir = os.environ.get("CHROME_USER_DATA_DIR")
    chrome_profile_directory = os.environ.get("CHROME_PROFILE_DIRECTORY")
    if chrome_user_data_dir:
        options.add_argument(f'--user-data-dir={chrome_user_data_dir}')
    if chrome_profile_directory:
        options.add_argument(f'--profile-directory={chrome_profile_directory}')

    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        # Plaud.aiのログインページを開く
        driver.get("https://app.plaud.ai/")
        print("Googleログインが完了するまで手動で操作してください。")
        input("ログイン後、Enterキーを押してください...")

        # localStorageからtokenstrを取得して保存
        tokenstr = driver.execute_script("return localStorage.getItem('tokenstr');")
        if tokenstr:
            with open("plaudai_tokenstr.txt", "w", encoding="utf-8") as f:
                f.write(tokenstr)
            print("tokenstrをplaudai_tokenstr.txtに保存しました。")
        else:
            print("localStorageからtokenstrが取得できませんでした。")

    except Exception as e:
        print(f"エラー: {e}")

    finally:
        if driver is not None:
            driver.quit()

if __name__ == "__main__":
    save_plaudai_tokenstr()