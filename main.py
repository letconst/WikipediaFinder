# -*- coding: utf-8 -*-
import re
import requests
import time


class WikipediaFinder:
    # 一度に取得できる最大ページ数
    __allow_page_count = 50
    # スクレイピングの間隔（秒）
    __scrape_interval = 1
    # 最後にリクエストを行った時間
    __last_scraped = 0

    def __init__(self, lang: str = 'ja'):
        # スクレイピング先のURL
        self.__url_to_scrape = f'https://{lang}.wikipedia.org/w/api.php'

    def get_page_by_name(self, page):
        """
        ページ名からページを取得する
        :param page: 取得するページの名前。複数取得したい場合は配列で指定
        :return: 取得したページの情報dict
        """
        payload = {
            'action':       'query',
            'format':       'json',
            'prop':         'description|info|categories',
            'indexpageids': 1,
            'titles':       None,
            'utf8':         1
        }

        # 引数チェック
        if type(page) is str:
            payload['titles'] = page
        elif type(page) is list:
            # ページ数が許容取得数より多い場合は許容内に収める
            if len(page) > self.__allow_page_count:
                # 弾かれたページ一覧
                popped_page = []

                for i, target in enumerate(page[self.__allow_page_count:]):
                    popped_page.append(target)
                    page.pop(i)

                print(f'一度に取得できる最大ページ数 ({self.__allow_page_count}) を超えているため、次のページは除外されました：' + '、'.join(popped_page))

            payload['titles'] = '|'.join(page)
        else:
            print('引数「page」は文字列か文字列リストで指定してください')
            return

        self.__await_interval()

        response = requests.get(self.__url_to_scrape, payload)
        res_json = response.json().get('query')

        if res_json is None:
            print('ページを取得できませんでした')
            return

        return self.__parse_receive_json(res_json)

    def get_random_page(self, pages_limit: int):
        """
        ページをランダムに取得する
        :param pages_limit: 取得するページ数
        :return: 取得したページの情報dict
        """
        if 0 >= pages_limit or pages_limit > 5000:
            print('引数「pages_limit」は1以上5000以下の整数で指定してください')
            return

        payload = {
            'action':       'query',
            'format':       'json',
            'prop':         'description|info|categories',
            'indexpageids': 1,
            'generator':    'random',
            'utf8':         1,
            'grnnamespace': '0',
            'grnlimit':     str(pages_limit)
        }

        self.__await_interval()

        response = requests.get(self.__url_to_scrape, payload)
        res_json = response.json().get('query')

        if res_json is None:
            print('ページを取得できませんでした')
            return

        return self.__parse_receive_json(res_json)

    def get_pages_in_category(self, category: str, pages_limit: int = 10):
        if 0 >= pages_limit or pages_limit > 5000:
            print('引数「pages_limit」は1以上5000以下の整数で指定してください')
            return

        payload = {
            'action':       'query',
            'format':       'json',
            'list':         'categorymembers',
            'indexpageids': 1,
            'utf8':         1,
            'cmtitle':      f'Category:{category}',
            'cmprop':       'ids|title',
            'cmnamespace':  '0',
            'cmlimit':      str(pages_limit)
        }

        self.__await_interval()

        response = requests.get(self.__url_to_scrape, payload)
        res_json = response.json().get('query')

        if res_json is None:
            print('ページを取得できませんでした')
            return

        return res_json['categorymembers']

    @staticmethod
    def __parse_receive_json(json: dict):
        """
        Wikipediaから取得したjsonを解析する
        :param json: Wikipediaから取得したjson
        :return: 解析し、整形したページ情報のdict
        """
        page_ids = json.get('pageids')
        result = {}

        if page_ids is None:
            return

        for id in page_ids:
            # 存在しないページは飛ばす
            if id == '-1':
                continue

            this_page = json['pages'][id]

            result[this_page['title']] = {
                'page_id':       id,
                'namespace':     this_page['ns'],
                'last_modified': this_page['touched'],
                'length':        this_page['length'],
                'desc':          this_page['description'] if 'description' in this_page else '',
                'categories':    [entry['title'] for entry in
                                  this_page['categories']] if 'categories' in this_page else []
            }

        return result
