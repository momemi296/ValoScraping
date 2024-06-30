"""
match_result_getter.py
matchのURLから試合結果を取得し、jsonl形式で出力します。

INPUT_FILEにmatchのURLが記述されたファイル名を代入してください。
match_results{プログラムを実行した日時}.jsonlに試合結果を出力し、
match_results{プログラムを実行した日時}_log.txtにログファイルを出力します。
"""


from selenium import webdriver
from selenium.webdriver import ChromeOptions as Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
from datetime import datetime as dt
import ndjson
import os

start_datetime_str = dt.now().strftime('%Y%m%d_%H%M')

OUTPUT_DIR = 'output_files'
INPUT_FILE = os.path.join(OUTPUT_DIR, 'match_urls.txt')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f'match_results_{start_datetime_str}.jsonl')
OUTPUT_LOG_FILE = os.path.join(OUTPUT_DIR, f'match_results_{start_datetime_str}_log.txt')

def get_player_info(driver, player_stats_list, is_attacker):
    match_player_stats_list = driver.find_elements(By.CLASS_NAME, 'match_playersStats__N01e1')
    for match_player_stats in match_player_stats_list:
        players = match_player_stats.find_elements(By.CLASS_NAME, 'match_tableRow__jAg0n')
        
        for player in players:
            match_player_details = player.find_element(By.CLASS_NAME, 'match_playerDetails__DbNW7') \
                .find_element(By.TAG_NAME, 'a')
            player_name = match_player_details.text
            country = match_player_details.find_element(By.TAG_NAME, 'img').get_attribute('title')
            
            match_agents = player.find_element(By.CLASS_NAME, 'match_agents__k5KRY') \
                .find_element(By.XPATH, 'span/img')
            agent_name = match_agents.get_attribute('alt')
            
            rating = player.find_elements(By.TAG_NAME, 'div')[2].text
            acs = player.find_elements(By.TAG_NAME, 'div')[3].text
            kda = player.find_element(By.CLASS_NAME, 'match_kda__wyeC7') \
                .find_element(By.TAG_NAME, 'span') \
                .find_elements(By.TAG_NAME, 'span')
            if len(kda) < 5:
                return False
                
            kills =  kda[0].text
            deaths =  kda[2].text
            assists =  kda[4].text
            
            k_minus_d = int(kills) - int(deaths)
            if int(deaths) == 0:
                k_per_d = int(kills)
            else:
                k_per_d = int(kills)/int(deaths)
            k_per_d = round(k_per_d, 2)
            kast = player.find_elements(By.TAG_NAME, 'div')[7].text
            adr = player.find_elements(By.TAG_NAME, 'div')[8].text
            hsr = player.find_elements(By.TAG_NAME, 'div')[9].text
            fbsr = player.find_elements(By.TAG_NAME, 'div')[10].text
            fb = player.find_elements(By.TAG_NAME, 'div')[11].text
            fd = player.find_elements(By.TAG_NAME, 'div')[12].text
            
            '''
            print(f'{player_name}, {country}, atk:{is_attacker}, {agent_name}, {rating}, {acs}, {kill}/{death}/{assist}, '
                  + f'{k_minus_d}, {k_per_d}, {kast}, {adr}, {hsr}, {fbsr}, {fb}, {fd}'
                  )
            '''
            
            player_stats_list.append({
                'player_name' : player_name,
                'country' : country,
                'is_attacker' : is_attacker,
                'agent_name' : agent_name,
                'rating' : rating,
                'acs' : acs,
                'kills' : kills,
                'deaths' : deaths,
                'assists' : assists,
                'k_minus_d' : k_minus_d,
                'k_per_d' : k_per_d,
                'kast' : kast,
                'adr' : adr,
                'hsr' : hsr,
                'fbsr' : fbsr,
                'fb' : fb,
                'fd' : fd
            })
    return True


op = Options()
op.add_argument('--ignore-certificate-errors')
op.add_argument('--ignore-ssl-errors')

with open(INPUT_FILE, 'r') as f:
    lines = f.read()
    urls = lines.split("\n")

for url_index, url in enumerate(urls):
    
    print(f'({url_index + 1}/{len(urls)})')

    print("Connect remote browser...")
    cService = webdriver.ChromeService(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=cService, options=op)

    print('remote browser connected...')
    print(f'url: {url}')
    driver.get(url=url)

    xpath_base = '//*[@id="__next"]/div[1]/main/div[1]/div[4]/div[2]/'
    atk_button_xpath_base = '//*[@id="__next"]/div[1]/main/div[1]/div[4]/div[5]/div[1]/div[2]/'

    i = 0

    while True:
        
        map_name = ''
        finish_status = 'normal'
        
        try:
            # マップの選択
            if len(driver.find_elements(By.XPATH, xpath_base + f'div[{i+1}]/div[3]/span')) <= 0:
                i += 1
                if i > 10:
                    break
                continue
                
            # マップがプレーされたか判定
            is_played = len(driver.find_element(By.XPATH, xpath_base + f'div[{i+1}]') \
                .find_elements(By.CLASS_NAME, 'match_score__m3Tq3')) > 0
            if not is_played:
                break
            sleep(1)
            mapname_elem = driver.find_element(By.XPATH, xpath_base + f'div[{i+1}]/div[3]/span')
            map_button = driver.find_element(By.XPATH, xpath_base + f'div[{i+1}]')
            driver.execute_script("arguments[0].click();", map_button)
            sleep(1)
            
            # //*[@id="__next"]/div[1]/main/div[1]/div[4]/div[2]/div[3]
            
            # 大会名の取得
            event_name = driver.find_element(By.CLASS_NAME, 'match_eventInfo__a6bN4').text
            match_details = driver.find_element(By.CLASS_NAME, 'match_matchDetails__T0yPR')
            # 試合名の取得
            match_name = match_details.find_elements(By.TAG_NAME, 'span')[0].text
            # 試合日時の取得
            match_date_time_str = match_details.find_elements(By.TAG_NAME, 'span')[1].text
            match_date_time = dt.strptime(match_date_time_str, '- %B %d, %Y - %I:%M%p')
            # パッチの取得
            patch = match_details.find_elements(By.TAG_NAME, 'span')[2].text.replace("Patch ", "")
            
            print(f'event_name : {event_name}')
            print(f'match_name : {match_name}')
            print(f'date_time : {match_date_time}')
            print(f'patch : {patch}')
            
            # マップ名の取得
            map_name = mapname_elem.text
            print(map_name)
            
            # チーム名の取得
            match_teams = driver.find_element(By.CLASS_NAME, 'match_teams__9d0xj')
            team_names = match_teams.find_elements(By.CLASS_NAME, "match_teamName__77urb")
            team_a_name = team_names[0].text
            team_b_name = team_names[1].text
            print(f'{team_a_name} vs {team_b_name}')
            
            # 攻撃側、守備側の取得
            first_round_results = driver.find_element(By.CLASS_NAME, 'match_roundDetails__EP1bY') \
                                .find_elements(By.TAG_NAME, 'span')
            
            reason_src = ""
            if (len(first_round_results) <= 2):
                print("ERROR: the number of first_round_results is less than 2.")
            elif len(first_round_results[1].find_elements(By.TAG_NAME, 'span')) > 0:
                # /_next/image?url=%2Fimages%2Fattacking-eliminate.png&w=32&q=75
                reason_src = first_round_results[1].find_elements(By.TAG_NAME, 'span')[0] \
                                .find_elements(By.TAG_NAME, 'img')[1] \
                                .get_attribute('src')
                reason_src = reason_src.replace('https://www.thespike.gg/_next/image?url=%2Fimages%2F', '').replace('.png&w=32&q=75', '')
                team_a_side = reason_src.split("-")[0]
                if team_a_side == 'attacking':
                    attacking_team_label = 'A'
                    deffending_team_label = 'B'
                else:
                    attacking_team_label = 'B'
                    deffending_team_label = 'A'
                
            elif len(first_round_results[2].find_elements(By.TAG_NAME, 'span')) > 0:
                reason_src = first_round_results[2].find_elements(By.TAG_NAME, 'span')[0] \
                                .find_elements(By.TAG_NAME, 'img')[1] \
                                .get_attribute('src')
                reason_src = reason_src.replace('https://www.thespike.gg/_next/image?url=%2Fimages%2F', '').replace('.png&w=32&q=75', '')
                team_b_side = reason_src.split("-")[0]
                if team_b_side == 'attacking':
                    attacking_team_label = 'B'
                    deffending_team_label = 'A'
                else:
                    attacking_team_label = 'A'
                    deffending_team_label = 'B'
            else:
                pass
            
            # ラウンド毎の勝敗の取得
            rounds = []
            match_rounds = driver.find_elements(By.CLASS_NAME, 'match_rounds__0neb8')
            for match_round in match_rounds:
                match_round_details = match_round.find_elements(By.CLASS_NAME, 'match_roundDetails__EP1bY')
                
                for match_round_detail in match_round_details:
                    round_results = match_round_detail.find_elements(By.TAG_NAME, 'span')
                    
                    if (len(round_results) == 0):
                        continue
                    if len(round_results[1].find_elements(By.TAG_NAME, 'span')) > 0:
                        winning_team_name = team_a_name
                        winning_team_label = 'A'
                        reason = round_results[1].find_elements(By.TAG_NAME, 'span')[0] \
                                .find_elements(By.TAG_NAME, 'img')[1] \
                                .get_attribute('alt')
                    elif len(round_results[2].find_elements(By.TAG_NAME, 'span')) > 0:
                        winning_team_name = team_b_name
                        winning_team_label = 'B'
                        reason = round_results[2].find_elements(By.TAG_NAME, 'span')[0] \
                                .find_elements(By.TAG_NAME, 'img')[1] \
                                .get_attribute('alt')
                    else:
                        break
                    
                    rounds.append({
                        'number' : round_results[0].text,
                        'winning_team_label' : winning_team_label,
                        'reason' : reason,
                    })
                    
            for match_round in rounds:
                print(f"{match_round['number']} : {match_round['winning_team_label']} - {match_round['reason']}")
            
            is_overtime = len(rounds) > 24
            
            first_half_rounds = rounds[:12]
            second_half_rounds = rounds[12:]
            
            first_half_a_score = sum([1 for r in first_half_rounds if r['winning_team_label'] == 'A'])
            first_half_b_score = 12 - first_half_a_score
            total_a_score = sum([1 for r in rounds if r['winning_team_label'] == 'A'])
            total_b_score = sum([1 for r in rounds if r['winning_team_label'] == 'B'])
            
            print(f'first_half_a_score : {first_half_a_score}')
            print(f'first_half_b_score : {first_half_b_score}')
            print(f'total_a_score : {total_a_score}')
            print(f'total_b_score : {total_b_score}')
            
            # プレイヤー戦績の取得
            player_stats_list = []
            atkdev_button = driver.find_element(By.CLASS_NAME, 'match_teamSide__NjM7C') \
                                .find_elements(By.TAG_NAME, 'button')
            atk_button = atkdev_button[1]
            def_button = atkdev_button[2]
            driver.execute_script("arguments[0].click();", atk_button)
            print("Getting attacker stats")
            sleep(1)
            
            is_success = get_player_info(driver, player_stats_list, True)
            if (not is_success):
                i += 1
                if i > 10:
                    break
                continue
            
            driver.execute_script("arguments[0].click();", def_button)
            print("Getting deffender stats")
            sleep(1)
            
            is_success = get_player_info(driver, player_stats_list, False)
            if (not is_success):
                i += 1
                if i > 10:
                    break
                continue
            
            first_half_stats = []
            second_half_stats = []
            team_a_index = [0, 1, 2, 3, 4, 10, 11, 12, 13, 14]
            if attacking_team_label == 'A':
                for j, stats in enumerate(player_stats_list):
                    if (stats['is_attacker'] and j in team_a_index) \
                        or (not stats['is_attacker'] and not j in team_a_index):
                        first_half_stats.append(stats)
                    else:
                        second_half_stats.append(stats)
            else:
                for j, stats in enumerate(player_stats_list):
                    if (not stats['is_attacker'] and j in team_a_index) \
                        or (stats['is_attacker'] and not j in team_a_index):
                        first_half_stats.append(stats)
                    else:
                        second_half_stats.append(stats)
            
            print("first_half")
            for stats in first_half_stats:
                print(f"{stats['player_name']}, {stats['country']}, atk:{stats['is_attacker']}, {stats['agent_name']}, {stats['rating']}, {stats['acs']}, {stats['kills']}/{stats['deaths']}/{stats['assists']}, "
                + f"{stats['k_minus_d']}, {stats['k_per_d']}, {stats['kast']}, {stats['adr']}, {stats['hsr']}, {stats['fbsr']}, {stats['fb']}, {stats['fd']}"
                )
            print("second_half")
            for stats in second_half_stats:
                print(f"{stats['player_name']}, {stats['country']}, atk:{stats['is_attacker']}, {stats['agent_name']}, {stats['rating']}, {stats['acs']}, {stats['kills']}/{stats['deaths']}/{stats['assists']}, "
                + f"{stats['k_minus_d']}, {stats['k_per_d']}, {stats['kast']}, {stats['adr']}, {stats['hsr']}, {stats['fbsr']}, {stats['fb']}, {stats['fd']}"
                )
            
            # json形式で保存する前のディクショナリ
            map_stats_dict = {
                "event_name" : event_name,
                "match_name" : match_name,
                "match_date_time" : str(match_date_time),
                "patch" : patch,
                "team_a_name" : team_a_name,
                "team_b_name" : team_b_name,
                "map_name" : map_name,
                "first_half_attaker_side" : attacking_team_label,
                "first_half_a_score" : first_half_a_score,
                "first_half_b_score" : first_half_b_score,
                "total_a_score" : total_a_score,
                "total_b_score" : total_b_score,
                "rounds_data" : rounds,
                "player_first_half_stats" : first_half_stats,
                "player_second_half_stats" : second_half_stats
            }
            
            with open(OUTPUT_FILE, 'a') as f:
                writer = ndjson.writer(f)
                writer.writerow(map_stats_dict)
                    
        except Exception as e:
            finish_status = 'error:' + str(e)
            print(finish_status)
            
        # ログを残す
        with open(OUTPUT_LOG_FILE, 'a') as f:
            f.write(f'({url_index + 1}/{len(urls)})-[{i + 1}], {map_name}, {finish_status}, {url}\n')
        
        i += 1
        if i > 10:
            break
        
    driver.quit()