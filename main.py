# -*- coding: utf-8 -*-
import re
import requests


class WikipediaFinder:
    # 一度に取得できる最大ページ数
    __allow_page_count = 50

    def __init__(self, lang: str = 'ja'):
        # スクレイピング先のURL
        self.__url_to_scrape = f'https://{lang}.wikipedia.org/w/api.php'

    def get_page_by_name(self, page):
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

        response = requests.get(self.__url_to_scrape, payload)
        res_json = response.json().get('query')

        if res_json is None:
            print('ページを取得できませんでした')
            return

        return self.__parse_receive_json(res_json)

    def get_random_page(self, page_count: int):
        if page_count <= 0:
            print('引数「page_count」は自然数で指定してください')
            return

        payload = {
            'action':       'query',
            'format':       'json',
            'prop':         'description|info|categories',
            'indexpageids': 1,
            'generator':    'random',
            'utf8':         1,
            'grnnamespace': '0',
            'grnlimit':     str(page_count)
        }

        response = requests.get(self.__url_to_scrape, payload)
        res_json = response.json().get('query')

        if res_json is None:
            print('ページを取得できませんでした')
            return

        return self.__parse_receive_json(res_json)

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
