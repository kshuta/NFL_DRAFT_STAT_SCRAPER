"""
-----------------------------------------------------------------------
-- Crawlするwebsite ----------------------------------------------------
-----------------------------------------------------------------------

    Combineの結果一覧ページ：
        "https://nflcombineresults.com/nflcombinedata.php?year=all&pos=WR&college="
    Combineの結果詳細ページ:
        -> 上記のページからscrapingする
    大学時代の戦績・ドラフト情報：
        "https://www.sports-reference.com/cfb/players/{選手の姓.lower}-{選手の名.lower}-1.html
    2020,2019のドラフト情報：
        "https://www.pro-football-reference.com/play-index/draft-finder.cgi?request=1&year_min=1987&year_max=2020&pick_type=overall&pos%5B%5D=wr&conference=any&show=all&order_by=default"

-----------------------------------------------------------------------
-----------------------------------------------------------------------


"""

# Imports
import requests
from bs4 import BeautifulSoup as bs
import os
import time
import pandas as pd
from tqdm import tqdm

# url_list
combine_index_url = "https://nflcombineresults.com/nflcombinedata.php?year=2020&pos=WR&college="
draft_table_url = "https://www.pro-football-reference.com/play-index/draft-finder.cgi?request=1&year_min=1987&year_max=2020&pick_type=overall&pos%5B%5D=wr&conference=any&show=all&order_by=default"


# directory paths
output_directory_path_for_combine = './crawl_exports/combine_results'
output_directory_path_for_stats = './crawl_exports/college_stats'
output_directory_path = './crawl_exports'


def draft_page_crawler():
    """
        2020,2019年にドラフトされた選手は、大学時代の戦績が乗ったページにドラフトされた順位が載っていないため、別途ここでクロールしたページを使う。
    """

    draft_page = requests.get(draft_table_url)
    file_name = "draft_page.html"

    if not os.path.exists(output_directory_path):
        os.mkdir(output_directory_path)
    with open(os.path.join(output_directory_path, file_name), 'w') as f:
        f.write(draft_page.text.encode('ascii', 'ignore').decode('utf-8'))


def get_show_urls_and_draft_year(index_url):
    """
        parameters:
            index_url: 詳細ページのURLを含んだ一覧ページのURL
        returns:
            <list>url_list, <list>player_names, <list>draft_year, <list>colleges

        詳細画面のURLの配列、選手名の配列、ドラフト年の配列が返される
        scraperで使うために、選手名、ドラフト年、大学名が入ったcsvファイルが出力される。
        デバッグ目的で引数として一覧ページのURLを渡すようにしている。
    """

    # responseとsoupの準備
    combine_index_response = requests.get(index_url)
    combine_index_soup = bs(combine_index_response.text, 'html.parser')

    # 詳細ページのURLを配列い保存する
    # urlが含まれている <tr>　を取得、クラス名は　tablefont
    tablefont_elms = combine_index_soup.find_all('tr', {'class': 'tablefont'})
    # urlの摘出
    combine_show_urls = [a_tag.get(
        'href') for element in tablefont_elms for a_tag in element.find_all('a')]

    # ドラフト年の摘出
    draft_years = [element.select('td')[0].get_text()
                   for element in tablefont_elms]
    # 名前の摘出
    player_name_list = [a_tag.get_text().replace('.', '')
                        for element in tablefont_elms for a_tag in element.find_all('a')]

    colleges = [element.select(
        'td')[2].get_text() for element in tablefont_elms]

    # Scraperで使うために選手名とドラフト年が入ったデータフレームをcsvファイルにエクスポート
    name_year_dict = {'Player_Name': player_name_list,
                      'Draft_Year': draft_years, 'College': colleges}
    name_year_df = pd.DataFrame(name_year_dict)
    if not os.path.exists(output_directory_path):
        os.mkdir(output_directory_path)
    file_name = os.path.join(
        output_directory_path, 'player_name_draft_year_colleges.csv')
    name_year_df.to_csv(file_name, index=False)

    return combine_show_urls, player_name_list, draft_years


def crawl_show_pages(url_list, player_name_list, draft_years):
    """
        parameters:
            url_list: crawlしたいページのURLの配列
            player_name_list: ファイル名作成用の選手名一覧

        与えられたURLSのページをcrawlingする。
        crawlしたものは"{first_name}_{last_name}_{ドラフト年}"というファイル名で出力される。

    """

    # ユーザーへ有益な出力をするためにenumerateしてます。
    with tqdm(total=len(url_list)) as pbar:
        for url, name, draft_year in zip(url_list, player_name_list, draft_years):
            splitted_name = name.split()
            first_name = splitted_name[0]
            last_name = splitted_name[1]

            # 出力用のファイル名の作成・保存先フォルダの作成
            file_name = "{}_{}_{}.html".format(
                first_name, last_name, draft_year)
            os.makedirs(output_directory_path_for_combine, exist_ok=True)

            # scrapeをし、ファイルに出力
            combine_show_response = requests.get(url)
            with open(os.path.join(output_directory_path_for_combine, file_name), mode='w', encoding='utf-8') as f:
                f.write(combine_show_response.text)

                # サーバーに負荷をかけすぎないために処理の一時停止・コードが正常に動いていることをユーザーに知らせるアウトプット
                pbar.update(1)
                time.sleep(1)


def crawl_college_stats_pages(name, draft_year):
    """
        引数として渡される名前とドラフト年を用いて、大学時代の戦績をcrawlする。
        出力ファイル名は"{first_name}_{last_name}_{draft_year}.html"
        parameters:
            name: 選手名
            draft_year: ドラフト年
    """

    # 選手名の下処理
    splitted_name = name.split()
    first_name = splitted_name[0].lower()
    last_name = splitted_name[1].lower()

    # 大学時代の戦績・ドラフト情報が乗ったページのベースURL
    base_url = "https://www.sports-reference.com/cfb/players/"

    # 同姓同名のチェック
    same_name_counter = 1
    stats_not_found_counter = 0
    # urlのフォーマット、"{first_name}-{last_name}-{same_name_counter}"は、同姓同名の選手を最後のsame_name_counterで識別する。
    while True:
        time.sleep(1)
        url = base_url + \
            "{}-{}-{}.html".format(first_name, last_name, same_name_counter)
        print(url)
        page = requests.get(url)
        temp_soup = bs(page.text, 'html.parser')
        if temp_soup.select_one('tbody') is not None:
            page_year = temp_soup.select_one('tbody').select(
                'tr')[-1].select_one('th').get_text()
            page_year = ''.join([num for num in page_year if num.isdecimal()])
        else:
            page_year = 0

        # getしたものに"404 error"という文言が入っていれば、ページが存在しなかったとのことなので、"stats not found"と記載されたhtmlを出力
        if "404 error" in page.text:
            file_name = "{}-{}-{}-stats.html".format(
                first_name, last_name, draft_year)
            os.makedirs(output_directory_path_for_stats, exist_ok=True)
            with open(os.path.join(output_directory_path_for_stats, file_name), mode='w') as f:
                f.write("Stats not found")
            stats_not_found_counter = 1
            break

        # getしたものにドラフト年-1の年（求める人であれば戦績のテーブルに必ず入っている）が入っているかどうかを確認。
        # ドラフト年-1の年がテキストの中に入ってなければ、same_name_counterを更新してループの最初に戻る。
        elif str(int(draft_year)-1) != page_year:
            same_name_counter = same_name_counter + 1
            continue

        # 上記のif文を全てクリアすれば求める人の戦績が載っているpageであることがわかったので、ファイルに出力
        else:
            file_name = "{}-{}-{}-stats.html".format(
                first_name, last_name, draft_year)
            os.makedirs(output_directory_path_for_stats, exist_ok=True)
            with open(os.path.join(output_directory_path_for_stats, file_name), mode='w', encoding='utf-8') as f:
                f.write(page.text)
            break
    return stats_not_found_counter


def main():
    draft_page_crawler()

    print('Crawling combine results: ')
    test_urls, player_name_list, draft_years = get_show_urls_and_draft_year(
        combine_index_url)

    crawl_show_pages(test_urls, player_name_list, draft_years)
    stats_not_found_counter = list()
    print("Crawling stats:")
    with tqdm(total=len(player_name_list)) as pbar:
        for name, draft_year in zip(player_name_list, draft_years):
            stats_not_found_counter.append(
                crawl_college_stats_pages(name, draft_year))
            pbar.update(1)

    print("Number of stats not found: ".format(sum(stats_not_found_counter)))
    print("done")


main()
