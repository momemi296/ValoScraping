"""
match_url_getter.py
各イベントのmatchのurlを取得します。

event-urls.txtのURLを取得してそのURLページに接続し、matchのURLを取得します。
結果をmatch_urls_{実行時の日時}.txtに出力します。
"""
from selenium import webdriver
from selenium.webdriver import ChromeOptions as Options
from selenium.webdriver.common.by import By
from time import sleep
from datetime import datetime as dt
import os

OUTPUT_DIR = 'output_files'
INPUT_FILE = os.path.join(OUTPUT_DIR, 'event_urls_fixed.txt')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f'match_urls.txt')

op = Options()
op.add_argument('--ignore-certificate-errors')
op.add_argument('--ignore-ssl-errors')

event_urls = []

with open(INPUT_FILE, 'r') as f:
    for line in f:
        event_urls.append(line)

for i, url in enumerate(event_urls):
    
    print(f'{i+1}/{len(event_urls)}')

    print("Connect remote browser...")
    cService = webdriver.ChromeService(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=cService, options=op)

    print('remote browser connected...')
    
    driver.get(url)

    print('get: ', url)
    sleep(2)

    elements = driver.find_elements(By.CLASS_NAME, "event_match__Pi5AT")
    print(f'Number of matches = {len(elements)}')

    match_urls = []

    for i, element in enumerate(elements):
        href = element.find_element(By.TAG_NAME, "a").get_attribute('href')
        match_urls.append(href)
        print(f'({i+1}/{len(elements)}) ', end="")
        print(href)

    file_name = OUTPUT_FILE
    print(f'filename: {file_name}')
    with open(file_name, mode='a') as f:
        for url in match_urls:
            url = url + '\n'
            f.write(url)

    print("Getting match urls is finnished.")

    driver.quit()