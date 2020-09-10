# -*- coding: utf-8 -*-
import re
import requests


class WikipediaFinder:
    def __init__(self, lang: str = 'ja'):
        # スクレイピング先のURL
        self.__url_to_scrape = f'https://{lang}.wikipedia.org/w/api.php'

    def getPageByName(self, page):
        # 一度に取得できる最大ページ数
        allow_page_count = 50
        payload = {
            'action':       'query',
            'format':       'json',
            'prop':         'description|info|categories',
            'indexpageids': 1,
            'titles':       None,
            'utf8':         1
        }
        result = {}

        # 引数チェック
        if type(page) is str:
            payload['titles'] = page
        elif type(page) is list:
            # ページ数が許容取得数より多い場合は許容内に収める
            if len(page) > allow_page_count:
                # 弾かれたページ一覧
                popped_page = []

                for i, target in enumerate(page[allow_page_count:]):
                    popped_page.append(target)
                    page.pop(i)

                print(f'一度に取得できる最大ページ数 ({allow_page_count}) を超えているため、次のページは除外されました：' + '、'.join(popped_page))

            payload['titles'] = '|'.join(page)
        else:
            print('引数「page」は文字列か文字列リストで指定してください')
            return

        response = requests.get(self.__url_to_scrape, payload)
        res_json = response.json().get('query', None)

        if res_json is None:
            print('ページを取得できませんでした')
            return

        page_ids = res_json['pageids']

        # 取得データを整形
        for i in page_ids:
            # 存在しないページは飛ばす
            if i == '-1':
                continue

            this_page = res_json['pages'][i]

            result[this_page['title']] = {
                'page_id':       i,
                'namespace':     this_page['ns'],
                'last_modified': this_page['touched'],
                'length':        this_page['length'],
                'desc':          this_page['description'],
                'categories':    [entry['title'] for entry in this_page['categories']]
            }

        return result
