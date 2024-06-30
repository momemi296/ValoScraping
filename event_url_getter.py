"""
event_url_getter.py
The spile.ggから過去のイベントのresultページのURLを取得します。
取得したURLをevent_urls.txtに出力します。
"""

from selenium import webdriver
from selenium.webdriver import ChromeOptions as Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
import os

OUTPUT_DIR = 'output_files'
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'event_urls.txt')

url = 'https://www.thespike.gg/events/completed'

op = Options()
op.add_argument('--ignore-certificate-errors')
op.add_argument('--ignore-ssl-errors')
#op.add_argument('--headless')

urls = []

print("Connect remote browser...")
cService = webdriver.ChromeService(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=cService, options=op)

print('remote browser connected...')

driver.get(url)

print('get: ', url)
sleep(2)


# 画面下部のVIEW MOREボタンを押す動作を、すべての過去のイベントが表示されるまで繰り返す。
i = 0
limit_button_push_num = 100
while(True):
    
    # これ以上ボタンが押せなくなる状態でボタンを押そうとする際に発生するエラーを利用して、ループを終了させる。
    try:
        i += 1
        print(f'press button: {i}')
        sleep(1)
        # VIEW MOREボタンの取得
        view_more_button = driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/main/div[1]/div[2]/div/div/button')
        
        # クリックの実行
        driver.execute_script("arguments[0].click();", view_more_button)
        
        # ボタンのクリック回数上限に達したらループから抜け出す。
        if i > limit_button_push_num:
            break
    except:
        break

# URL要素の取得
events = driver.find_element(By.CLASS_NAME, "events_columnBody___oBi4")
elem_a_list = events.find_elements(By.TAG_NAME, "a")

# URLの取得
for elem_a in elem_a_list:
    tartget_url = elem_a.get_attribute('href')
    urls.append(tartget_url)
    

if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)

# ファイルへ出力
with open(OUTPUT_FILE, mode='w') as f:
    for url in urls:
        url = url.replace('events/', 'events/results/') + "\n"
        f.write(url)

driver.quit()