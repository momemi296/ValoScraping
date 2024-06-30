"""
event_url_chooser.py
イベントのURLの中から特定のイベントのURLを厳選する
event_urls_fixed.txtに結果を出力します。
"""

import os

OUTPUT_DIR = 'output_files'
INPUT_FILE = os.path.join(OUTPUT_DIR, 'event_urls.txt')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'event_urls_fixed.txt')

event_urls = []

with open(INPUT_FILE, 'r') as f:
    for line in f:
        """
        以下で条件を指定するとこで、特定のイベントのURLのみを取得することができます。
        以下の例では、vct-2023とvct-2024の試合で、urlにchallengers、game-changers、off-season
        を含まないurlを取得できます。
        """
        
        if 'vct-2023' in line or 'vct-2024' in line:
            
            if 'challengers' in line:
                continue
            
            if 'game-changers' in line:
                continue
                
            if 'off-season' in line:
                continue
            
            event_urls.append(line)

with open(OUTPUT_FILE, 'w') as f:
    for url in event_urls:
        f.write(url)