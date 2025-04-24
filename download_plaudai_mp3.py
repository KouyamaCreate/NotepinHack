import os
from dotenv import load_dotenv
import pickle
import time
import requests
import datetime
import re
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.common.exceptions import NoSuchElementException, TimeoutException
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# --- 設定 ---
LOGIN_URL = "https://app.plaud.ai/"
RECORD_LIST_API_URL = "https://api.plaud.ai/file/simple/web?skip=0&limit=99999&is_trash=2&sort_by=start_time&is_desc=true"
DOWNLOAD_URL_API_BASE = "https://api.plaud.ai/file/temp-url/"
DOWNLOAD_DIR = "plaud_downloads" # ダウンロード先ディレクトリ名
# -------------

def sanitize_filename(filename):
    """ファイル名として無効な文字を除去または置換する"""
    # WindowsとmacOS/Linuxで一般的に無効な文字を除去
    sanitized = re.sub(r'[\\/*?:"<>|]', '_', filename)
    # 長すぎるファイル名を切り詰める（オプション）
    # max_len = 200
    # if len(sanitized) > max_len:
    #     name, ext = os.path.splitext(sanitized)
    #     sanitized = name[:max_len - len(ext)] + ext
    return sanitized

def download_file(url, save_path):
    """指定されたURLからファイルをダウンロードして保存する"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status() # HTTPエラーがあれば例外を発生させる
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"  ダウンロード完了: {os.path.basename(save_path)}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"  ダウンロードエラー: {e}")
        return False
    except Exception as e:
        print(f"  ファイル保存エラー: {e}")
        return False

def main():
    load_dotenv()
    # 認証トークン（tokenstr）をファイルから読み込む
    tokenstr_path = "plaudai_tokenstr.txt"
    if not os.path.exists(tokenstr_path):
        print(f"エラー: {tokenstr_path} が存在しません。まずsave_plaudai_cookies.pyで取得してください。")
        return

    with open(tokenstr_path, "r", encoding="utf-8") as f:
        token_str = f.read().strip()

    if not token_str or not token_str.startswith("bearer "):
        print("エラー: ファイルから有効な認証トークンを取得できませんでした。")
        print("ログイン状態を確認し、再度cookie/tokenを取得してください。")
        return

    auth_token = token_str # "bearer <トークン>" の形式
    print("認証トークンをファイルから取得しました。")

    # --- 録音リストを取得 ---
    print("\n録音リストを取得中...")
    headers = {
        "Authorization": auth_token,
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36" # User-Agentは適宜調整
    }
    try:
        response = requests.get(RECORD_LIST_API_URL, headers=headers)
        response.raise_for_status()
        record_data = response.json()

        if record_data.get("status") != 0 or "data_file_list" not in record_data:
            print(f"エラー: 録音リストの取得に失敗しました。 APIレスポンス: {record_data}")
            return

        record_list = record_data["data_file_list"]
        print(f"{len(record_list)} 件の録音が見つかりました。")

    except requests.exceptions.RequestException as e:
        print(f"エラー: 録音リストAPIへのリクエスト中にエラーが発生しました: {e}")
        return
    except ValueError:
        print("エラー: 録音リストAPIのレスポンスがJSON形式ではありません。")
        print(f"レスポンス内容: {response.text}")
        return

    # --- 今日の日付を取得 ---
    today = datetime.date.today()
    # start_time はミリ秒単位のUnixタイムスタンプのようなので、秒単位に変換して比較
    start_of_today_ts = time.mktime(today.timetuple())

    # --- ダウンロード対象をフィルタリング ---
    today_records = []
    for record in record_list:
        start_time_ms = record.get("start_time")
        if start_time_ms:
            try:
                # ミリ秒を秒に変換
                start_time_sec = start_time_ms / 1000
                record_date = datetime.date.fromtimestamp(start_time_sec)
                if record_date == today:
                    today_records.append(record)
            except Exception as e:
                print(f"警告: 録音 {record.get('id')} の日付変換中にエラー: {e}")

    if not today_records:
        print("\n本日分の録音は見つかりませんでした。")
        return

    print(f"\n本日分の録音 {len(today_records)} 件をダウンロードします。")

    # --- ダウンロードディレクトリ作成 ---
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
        print(f"ダウンロードディレクトリを作成しました: {DOWNLOAD_DIR}")

    # --- MP3 (またはOpus) をダウンロード ---
    download_count = 0
    for record in today_records:
        record_id = record.get("id")
        filename_base = record.get("filename", f"recording_{record_id}")
        # fullname から拡張子を取得 (例: .opus) なければ .mp3 を仮定
        fullname = record.get("fullname", "")
        _, ext = os.path.splitext(fullname)
        if not ext or ext.lower() not in ['.mp3', '.opus', '.wav', '.m4a']: # 一般的な音声形式
            ext = ".mp3" # デフォルトはmp3とする

        sanitized_filename = sanitize_filename(filename_base) + ext
        save_path = os.path.join(DOWNLOAD_DIR, sanitized_filename)

        print(f"\n録音 '{filename_base}' (ID: {record_id}) のダウンロードURLを取得中...")

        # ダウンロードURL取得APIを呼び出す
        download_api_url = DOWNLOAD_URL_API_BASE + record_id
        try:
            dl_response = requests.get(download_api_url, headers=headers)
            dl_response.raise_for_status()
            dl_data = dl_response.json()

            if dl_data.get("status") != 0 or "temp_url" not in dl_data or not dl_data["temp_url"]:
                print(f"  エラー: ダウンロードURLの取得に失敗しました。 APIレスポンス: {dl_data}")
                continue

            download_url = dl_data["temp_url"]
            print(f"  ダウンロードURL取得成功。ダウンロードを開始します...")

            # ファイルをダウンロード
            if download_file(download_url, save_path):
                download_count += 1

        except requests.exceptions.RequestException as e:
            print(f"  エラー: ダウンロードURL取得APIへのリクエスト中にエラーが発生しました: {e}")
        except ValueError:
            print(f"  エラー: ダウンロードURL取得APIのレスポンスがJSON形式ではありません。")
            print(f"  レスポンス内容: {dl_response.text}")
        except Exception as e:
            print(f"  予期せぬエラーが発生しました: {e}")

    print(f"\nダウンロード処理完了。{download_count} / {len(today_records)} 件のファイルをダウンロードしました。")


if __name__ == "__main__":
    main()