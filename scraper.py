# -*- coding: utf-8 -*-
"""
-----------------------------------------------------------------------
-- Scrapeする情報 ----------------------------------------------------
-----------------------------------------------------------------------
    - Height (in) 身長
    - Weight (lb) 体重
    - Hand Size (inch) 手の大きさ
    - Arm length (inch) 腕の長さ
    - 40yd (seconds) 40ヤード走
    - Vertical (inch) その場跳び
    - Broad Jump (inch) 立ち幅跳び
    - Career receiving yards per catch １キャッチあたりのレシービングヤード数（大学時代全て）
    - Last year receiving yards per catch １キャッチあたりのレシービングヤード数（大学最後の年のみ）
    - Career Return yards per attempt １リターンあたりのヤード数（大学時代全て）
    - Last year return yards per attempt １リターンあたりのヤード数（大学最後の年のみ）
    - College 大学名
    - Round Drafted 指名巡 (ドラフトされなかった場合は0）
-----------------------------------------------------------------------
-----------------------------------------------------------------------

-----------------------------------------------------------------------
-- 全体の流れ -----------------------------------------------------------
-----------------------------------------------------------------------
    前提ファイル（crawlerによって生成されたもの)：
            　combine結果詳細ページ（選手の数）
    　        大学時代の戦績・ドラフト情報のページ（選手の数）
              選手名とドラフト年が含まれたcsvファイル（１枚）
              2019,2020のドラフトされたWRが載った一覧ページ（１枚）
    1. 選手名とドラフト年の読み込み
    2. 2019, 2020年のドラフト巡とドラフトされた選手名のリストをスクレーピング。あとで使うようにドラフトされた選手の名前が含まれる集合（set)を作成。
    3. 収集するデータごとにリストを作成
        4. combine結果詳細ページをscrapeしてlistに保存
        5. 大学時代の戦績・ドラフト情報のページをscrapeしてlistに保存
        6. 4,5を繰り返し
    7.各々のリストからdfを作成
    8. 軽くdfを綺麗にしてcsvに書き出し

    コードの生成物（枚数）：
    　収集項目のデータを持ったcsv
-----------------------------------------------------------------------
-----------------------------------------------------------------------
-----------------------------------------------------------------------


set化 => O(n) x1
list参照 => O(n) x (選手名分)
set参照 => O(1) x (選手名分)
list.index => O(n) x (setのなかに合った選手名分)

"""

# imports
import requests
from bs4 import BeautifulSoup as bs
from bs4 import Comment
import os
import pandas as pd

name_year_path = './crawl_exports/player_name_draft_year_colleges.csv'

# global variables
heights = list()
weights = list()
hand_sizes = list()
arm_lengths = list()
forty_times = list()
verticals = list()
broads = list()
last_year_rec = list()
career_rec = list()
last_year_return = list()
career_return = list()
draft_round = list()


def read_name_year_college():
    """
    return:
        draft_years: ドラフト年が含まれる配列
        plyaer_names: 選手名が含まれる配列
        colleges: 大学名が含まれる配列

    crawler.pyで書き出した選手名とドラフト年を含むcsvファイルを読み込んで、それぞれの列を配列として返す
    """

    name_year_df = pd.read_csv(name_year_path)

    return list(name_year_df.Draft_Year), list(name_year_df.Player_Name), list(name_year_df.College)


def scraper(year, name, recent_player_names, recent_draft_round):
    """
    for文を多様したくないため、二つのページから同時にスクレーピングを行う。
    返す値はなく、グローバルで定義されている配列にスクレーピングした値を保存する。
    """
    first_name = name.split()[0]
    last_name = name.split()[1]

    ####### combine stats #######
    combine_file_name = '{}_{}_{}.html'.format(first_name, last_name, year)
    combine_base_path = 'crawl_exports/combine_results/'
    combine_file_path = os.path.join(combine_base_path, combine_file_name)
    combine_content = open(combine_file_path, 'r').read()
    combine_stat_soup = bs(combine_content, 'html.parser')
    stats = combine_stat_soup.select_one(
        "table[class='tableperc']").select('tr')

    for idx, stat in enumerate(stats):
        children = stat.select('td')
        if idx == 1:
            height = children[1].get_text()
            num_height_list = [num for num in height if num != "\""]
            num_height = "".join(num_height_list)
            if num_height == '(N/A)':
                heights.append(None)
            else:
                heights.append(float(num_height))

        elif idx == 2:
            weight = children[1].get_text()
            num_weight = weight.split()[0]
            if num_weight == '(N/A)':
                weights.append(None)
            else:
                weights.append(float(num_weight))
        elif idx == 3:
            hand_size = children[1].get_text()
            num_hand_size_list = [num for num in hand_size if num != "\""]
            num_hand_size = ''.join(num_hand_size_list)
            if num_hand_size == '(N/A)':
                hand_sizes.append(None)
            else:
                hand_sizes.append(float(num_hand_size))

        elif idx == 4:
            arm_length = children[1].get_text()
            num_arm_length_list = [num for num in arm_length if num != "\""]
            num_arm_length = ''.join(num_arm_length_list)
            if num_arm_length == '(N/A)':
                arm_lengths.append(None)
            else:
                arm_lengths.append(float(num_arm_length))

        elif idx == 5:
            forty_time = children[1].get_text()
            num_forty_time = forty_time.split()[0]
            if num_forty_time == "(N/A)":
                forty_times.append(None)
            else:
                forty_times.append(float(num_forty_time))

        elif idx == 9:
            vertical = children[1].get_text()
            num_vertical_list = [num for num in vertical if num != "\""]
            num_vertical = ''.join(num_vertical_list)
            if num_vertical == '(N/A)':
                verticals.append(None)
            else:
                verticals.append(float(num_vertical))
        elif idx == 10:
            broad = children[1].get_text()
            num_broad_list = [num for num in broad if num != "\""]
            num_broad = ''.join(num_broad_list)
            if num_broad == "(N/A)":
                broads.append(None)
            else:
                broads.append(float(''.join(num_broad)))

     ####### college stats #######

    stats_file_name = '{}-{}-{}-stats.html'.format(
        first_name.lower(), last_name.lower(), year)
    stats_base_path = 'crawl_exports/college_stats/'
    stats_file_path = os.path.join(stats_base_path, stats_file_name)
    stats_content = open(stats_file_path, mode="r",
                         encoding="ascii", errors="ignore").read()
    stats_soup = bs(stats_content, "html.parser")

    # draft round
    if year in [2020, 2019]:
        if name in recent_player_names:
            draft_round.append(
                recent_draft_round[recent_player_names.index(name)])
        else:
            draft_round.append(0)

    else:
        meta = stats_soup.find(id='meta')
        str_meta = str(meta)
        if 'Draft' in str_meta:
            draft_round.append(int(str_meta[str_meta.index('Draft')+16]))
        else:
            draft_round.append(0)

    # receiving yards
    if stats_soup.find(id='receiving') is not None:
        last_year_rec.append(stats_soup.find(id='receiving').select_one(
            'tbody').select('tr')[-1].select('td')[7].get_text())
        career_rec.append(stats_soup.find(id='receiving').select_one(
            'tfoot').select('td')[7].get_text())
    else:
        last_year_rec.append(0)
        career_rec.append(0)

    # returning yards
    # returning yards はコメントに覆われてたので、少し手間を加える。
    comments = stats_soup.find_all(
        string=lambda text: isinstance(text, Comment))
    kick_ret_table = None
    for comment in comments:
        comment = bs(str(comment), 'html.parser')
        kick_ret_table = comment.find(id='kick_ret')
        if kick_ret_table:
            break

    if kick_ret_table:
        last_year_return.append(kick_ret_table.select_one(
            'tbody').select('tr')[-1].select('td')[7].get_text())
        career_return.append(kick_ret_table.select_one(
            'tfoot').select('td')[7].get_text())
    else:
        last_year_return.append(0)
        career_return.append(0)


def get_player_name_and_round():
    """
        return:
            player_names: 2020,2019年にドラフトされた選手を含む配列
            drafted_rounds: 2020,2019年にドラフトされた選手のドラフト巡を含む配列

        2019年以前の選手は、大学の戦績が載ったページにドラフト巡が載っているが、2019,2020年の選手は載っていなかったため、他のページから取得する。
    """

    draft_page = open('crawl_exports/draft_page.html', 'r').read()
    page_soup = bs(draft_page, 'html.parser')
    if page_soup.find(id='results') is not None:
        tbody = page_soup.find(id='results').select_one('tbody')
    else:
        tbody = None

    # creating list of player names that was drafted in 2020 or 2019
    player_names = list()
    drafted_rounds = list()
    if tbody is not None:
        for row in tbody.select('tr'):
            if row.get('class') is None:
                if row.select_one('td').get_text() in ['2020', '2019']:
                    tds = row.select('td')
                    player_names.append(tds[3].select_one('a').get_text().replace(
                        'Jr', '').replace('III', '').strip())
                    drafted_rounds.append(tds[1].get_text())

    return player_names, drafted_rounds


def main():
    recent_player_names, recent_draft_round = get_player_name_and_round()

    draft_years, player_names, colleges = read_name_year_college()
    for year, name in zip(draft_years, player_names):
        scraper(year, name, recent_player_names, recent_draft_round)

    data_dict = {'Height': heights, 'Weight': weights, 'HandSize': hand_sizes, 'ArmLength': arm_lengths, 'FortyTime': forty_times, 'Vertical': verticals, 'BroadJump': broads,
                 'LastYearRecAvg': last_year_rec, 'CareerRecAvg': career_rec, 'LastYearReturnAvg': last_year_return, 'CareerReturnAvg': career_return, 'DraftRound': draft_round, 'College': colleges}
    data_df = pd.DataFrame(data_dict)

    data_df.to_csv('output.csv', index=False)


main()
