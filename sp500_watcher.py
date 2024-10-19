import requests
from bs4 import BeautifulSoup
import datetime
import json
from plyer import notification
import os

# S&P500データを取得する関数
def get_sp500_data():
    url = "https://finance.yahoo.com/quote/%5EGSPC/history?p=%5EGSPC"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Yahoo FinanceからS&P 500の終値データをスクレイピング
    table_rows = soup.find_all('tr')
    for row in table_rows:
        cols = row.find_all('td')
        if len(cols) > 0:
            date = cols[0].text.strip()
            close_price = cols[5].text.strip().replace(',', '')
            try:
                close_price = float(close_price)
                return close_price
            except ValueError:
                continue
    return None

# 前週金曜日のデータをファイルに保存・読み込みする関数
def save_last_friday_data(close_price):
    with open('sp500_data.json', 'w') as file:
        json.dump({'last_friday_close': close_price}, file)

def load_last_friday_data():
    if os.path.exists('sp500_data.json'):
        with open('sp500_data.json', 'r') as file:
            data = json.load(file)
            return data.get('last_friday_close', None)
    return None

# 通知を送る関数
def send_notification():
    notification.notify(
        title="S&P 500 Alert",
        message="S&P 500 has dropped more than 5% this week!",
        app_name="SP500 Watcher",
    )

# メイン関数
def main():
    today = datetime.datetime.today()
    
    # 金曜日かどうかチェック
    if today.weekday() == 4:  # 0:月曜日, 4:金曜日
        this_friday_close = get_sp500_data()
        last_friday_close = load_last_friday_data()

        # 前週のデータが存在すれば、比較する
        if last_friday_close is not None and this_friday_close is not None:
            percentage_change = ((this_friday_close - last_friday_close) / last_friday_close) * 100
            print(f"S&P 500 Weekly Change: {percentage_change:.2f}%")
            
            # 5%以上の下落があれば通知
            if percentage_change <= -5:
                send_notification()

        # 今週のデータを保存
        if this_friday_close is not None:
            save_last_friday_data(this_friday_close)

# プログラムがPC起動時に自動的に立ち上がるようにするためのWindowsスタートアップ登録
def add_to_startup():
    # スクリプトのパスを取得
    script_path = os.path.realpath(__file__)
    
    # スタートアップフォルダにショートカットを作成
    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
    shortcut_path = os.path.join(startup_folder, 'sp500_watcher.bat')

    with open(shortcut_path, 'w') as shortcut:
        shortcut.write(f'python "{script_path}"')

if __name__ == "__main__":
    add_to_startup()  # スタートアップに登録
    main()  # メインプログラムを実行
