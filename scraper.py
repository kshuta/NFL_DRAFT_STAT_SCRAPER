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
    1. 選手名とドラフト年の読み込み
    2. 収集するデータ項目をカラム名に設定し、pandasのDataframeを作成 (df)
        3. combine結果詳細ページをscrapeしてlistに保存
        4. 大学時代の戦績・ドラフト情報のページをscrapeして2と同じlistに保存
        5. 生成されたlistを 1で作成したdfに追加（append)。名前はdropする。
        7. 2を繰り返し
    8. 
    9. dfをcsvに書き出し

    コードの生成物（枚数）：
    　収集項目のデータを持ったcsv
-----------------------------------------------------------------------
-----------------------------------------------------------------------
-----------------------------------------------------------------------


"""

name_year_path = './crawl_exports/player_name_draft_year.csv'


def read_name_year():
    """
    return:
        draft_years: ドラフト年が含まれる配列
        plyaer_names: 選手名が含まれる配列
    crawler.pyで書き出した選手名とドラフト年を含むcsvファイルを読み込む
    """

    name_year_df = pd.read_csv(name_year_path)

    return list(name_year_df.Draft_Year), list(name_year_df.Player_Names)


def combine_stats_scraper(year, name):
    """

    """
    first_name = name.split()[0]
    last_name = name.split()[1]
    file_name = '{}_{}_{}.html'.format(first_name, last_name, year)
    base_path = 'crawl_exports/combine_results/'
    file_path = os.path.join(base_path, file_name)

    content = open(file_path, 'r').read()

    combine_stat_soup = bs(content, 'html.parser')
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


def main():
    heights = list()
    weights = list()
    hand_sizes = list()
    arm_lengths = list()
    forty_times = list()
    verticals = list()
    broads = list()
    draft_years, player_names = read_name_year()
    for year, name in zip(draft_years, player_names):
        combine_stats_scraper(year, name)
