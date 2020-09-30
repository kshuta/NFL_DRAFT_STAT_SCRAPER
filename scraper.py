
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
    -- 以下追加項目 --
    - 20yds (seconds) 20ヤード走
    - 10yds (seconds) 10ヤード走
    - Bench (reps) 100kgのベンチプレスを何回あげれるか。
    - Shuttle (seconds) 短距離のシャトル走
    - 3 cones (seconds) 3つのコーンを使ったアジリティドリル
    - 60yds Shuttle (seconds) 60ヤードのシャトル走
    - Career receiving yards レシービングヤード数（大学時代全て）
    - Last Year receiving yards レシービングヤード数（大学最後の年のみ）
-----------------------------------------------------------------------
-----------------------------------------------------------------------


"""

# imports
import requests
from bs4 import BeautifulSoup as bs
from bs4 import Comment
import os
import pandas as pd
from tqdm import tqdm

name_year_path = './crawl_exports/player_name_draft_year_colleges.csv'

# global variables
heights = list()
weights = list()
hand_sizes = list()
arm_lengths = list()
forty_times = list()
twenty_times = list()
ten_times = list()
benches = list()
verticals = list()
broads = list()
shuttles = list()
three_cones = list()
sixty_yard_shuttles = list()
last_year_rec = list()
career_rec = list()
last_year_return = list()
career_return = list()
draft_round = list()
total_career_rec = list()
total_last_year_rec = list()


def read_name_year_college():
    """
    return:
        draft_year_list: ドラフト年が含まれる配列
        plyaer_names: 選手名が含まれる配列
        colleges: 大学名が含まれる配列

    crawler.pyで書き出した選手名とドラフト年を含むcsvファイルを読み込んで、それぞれの列を配列として返す
    """

    name_year_df = pd.read_csv(name_year_path)

    return list(name_year_df.Draft_Year), list(name_year_df.Player_Name), list(name_year_df.College)


def scraper(draft_year, player_name, recent_player_names, recent_draft_round):
    """
    for文を多用したくないため、二つのページから同時にスクレーピングを行う。
    返す値はなく、グローバルで定義されている配列にスクレーピングした値を保存する。
    """
    first_name = player_name.split()[0]
    last_name = player_name.split()[1]

    ####### combine stats #######
    combine_file_name = '{}_{}_{}.html'.format(
        first_name, last_name, draft_year)
    combine_base_path = 'crawl_exports/combine_results/'
    combine_file_path = os.path.join(combine_base_path, combine_file_name)
    combine_content = open(combine_file_path, 'r').read()
    combine_stat_soup = bs(combine_content, 'html.parser')
    stats = combine_stat_soup.select_one(
        "table[class='tableperc']").select('tr')

    for idx, stat in enumerate(stats):
        """
        idx==1: 選手の身長
        idx==2: 選手の体重
        idx==3: 選手の手の大きさ
        idx==4: 選手の腕の長さ
        idx==5: 選手の40yd走の記録
        idx==6: 選手の20yd走の記録
        idx==7: 選手の10yd走の記録
        idx==8: 選手の100kgのベンチプレスのレップ数
        idx==9: 選手の垂直跳びの記録
        idx==10: 選手の立ち幅跳びの記録
        idx==11: 選手のシャトル走の記録
        idx==12: 選手の3 cone drillの記録
        idx==13: 選手の60yd シャトル走の記録

        長さを表す記録にはインチを表す'"'と言う表記が入っているが、出力する時に不要なので配列に追加する前に消去する。
        その他記録は、数値と単位の間にスペースが入っているため、split()してから最初のentryを選択する。
        情報が記録されていないものに関しては、'(N/A)'というテキストが入っているため、その場合は配列に'None'を追加する

        """
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
        elif idx == 6:
            twenty_time = children[1].get_text()
            num_twenty_time = twenty_time.split()[0]
            if num_twenty_time == "(N/A)":
                twenty_times.append(None)
            else:
                twenty_times.append(float(num_twenty_time))
        elif idx == 7:
            ten_time = children[1].get_text()
            num_ten_time = ten_time.split()[0]
            if num_ten_time == "(N/A)":
                ten_times.append(None)
            else:
                ten_times.append(float(num_ten_time))
        elif idx == 8:
            bench = children[1].get_text()
            num_bench = bench.split()[0]
            if num_bench == "(N/A)":
                benches.append(None)
            else:
                benches.append(int(num_bench))
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
        elif idx == 11:
            shuttle = children[1].get_text()
            num_shuttle = shuttle.split()[0]
            if num_shuttle == "(N/A)":
                shuttles.append(None)
            else:
                shuttles.append(float(num_shuttle))
        elif idx == 12:
            three_cone = children[1].get_text()
            num_cone = three_cone.split()[0]
            if num_cone == "(N/A)":
                three_cones.append(None)
            else:
                three_cones.append(float(num_cone))
        elif idx == 13:
            sixty_shuttle = children[1].get_text()
            num_sixty_shuttle = sixty_shuttle.split()[0]
            if num_sixty_shuttle == "(N/A)":
                sixty_yard_shuttles.append(None)
            else:
                sixty_yard_shuttles.append(float(num_sixty_shuttle))

         ####### college stats #######

    stats_file_name = '{}-{}-{}-stats.html'.format(
        first_name.lower(), last_name.lower(), draft_year)
    stats_base_path = 'crawl_exports/college_stats/'
    stats_file_path = os.path.join(stats_base_path, stats_file_name)
    stats_content = open(stats_file_path, mode="r",
                         encoding="ascii", errors="ignore").read()
    stats_soup = bs(stats_content, "html.parser")

    # draft round
    """
    2020,2019にドラフトされた選手は
    """
    if draft_year in [2020, 2019]:
        if player_name in recent_player_names:
            draft_round.append(
                recent_draft_round[recent_player_names.index(player_name)])
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
        total_last_year_rec.append(stats_soup.find(id='receiving').select_one(
            'tbody').select('tr')[-1].select('td')[6].get_text())
        total_career_rec.append(stats_soup.find(id='receiving').select_one(
            'tfoot').select('td')[6].get_text())

    else:
        last_year_rec.append(0)
        career_rec.append(0)
        total_last_year_rec.append(0)
        total_career_rec.append(0)

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
            player_name_list: 2020,2019年にドラフトされた選手を含む配列
            drafted_rounds: 2020,2019年にドラフトされた選手のドラフト巡を含む配列

        2019年以前の選手は、大学の戦績が載ったページにドラフト巡が載っているが、2019,2020年の選手は載っていない。
        そのため、別途クロールしてきた"draft_page.html"からドラフトラウンドを取得する。
    """

    draft_page = open('crawl_exports/draft_page.html', 'r').read()
    page_soup = bs(draft_page, 'html.parser')

    # ドラフト年、ドラフト巡が記載されたテーブルを取り出す。
    tbody = page_soup.find(id='results').select_one('tbody')

    # 選手名、ドラフト巡を保存しておくための配列を作成
    player_name_list = list()
    drafted_rounds = list()

    if tbody is not None:
        for row in tbody.select('tr'):
            if row.get('class') is None:  # 取得した行のclassに何か指定されていると、それはデータを含まない行なので飛ばす。
                # 一番最初の'td'にドラフト年が入っているので、それが2020か2019の場合は次に進む。
                if row.select_one('td').get_text() in ['2020', '2019']:
                    tds = row.select('td')
                    # 2つ目のtdにドラフト巡、4つ目のtdに名前が入っている。
                    player_name_list.append(tds[3].select_one('a').get_text().replace(
                        'Jr', '').replace('III', '').strip())  # 比較する選手の名前が入った配列にヒア、名前に'Jr.'や 'III'などと行った表記はないためここで省く。
                    drafted_rounds.append(tds[1].get_text())

    return player_name_list, drafted_rounds


def main():
    recent_player_names, recent_draft_round = get_player_name_and_round()

    draft_year_list, player_name_list, colleges = read_name_year_college()

    # プログレスバーの設定
    with tqdm(total=len(player_name_list)) as pbar:
        for idx, (draft_year, player_name) in enumerate(zip(draft_year_list, player_name_list)):
            scraper(draft_year, player_name,
                    recent_player_names, recent_draft_round)
            pbar.update(1)

    data_dict = {'Height': heights, 'Weight': weights, 'HandSize': hand_sizes, 'ArmLength': arm_lengths, 'FortyTime': forty_times, 'TwentyTime': twenty_times, 'TenTime': ten_times, 'Bench': benches, 'Vertical': verticals, 'BroadJump': broads, 'Shuttle': shuttles, 'ThreeCone': three_cones, 'SixtyShuttle': sixty_yard_shuttles,
                 'LastYearRecAvg': last_year_rec, 'CareerRecAvg': career_rec, 'LastYearReturnAvg': last_year_return, 'CareerReturnAvg': career_return, 'DraftRound': draft_round, 'College': colleges, 'DraftYear': draft_year_list, 'CareerRec': total_career_rec, 'LastYearRec': total_last_year_rec}
    data_df = pd.DataFrame(data_dict)

    data_df.to_csv('output.csv', index=False)


main()
