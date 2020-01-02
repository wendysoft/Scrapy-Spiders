import scrapy
import requests
import logging
import re
import json
import pymysql
from jsonpath import jsonpath
from lxml import etree
from scrapy.cmdline import execute
from scrapy import Request
from neteasemusic import settings
from neteasemusic.functions.list import CategoryList
from neteasemusic.items import NeteasemusicItem
from neteasemusic.settings import DEFAULT_REQUEST_HEADERS


class playlistSpider(scrapy.Spider):
    name = 'netease'
    start_urls = ["https://music.163.com"]
    category_url = 'https://music.163.com/discover/playlist/?cat={}&limit=35&offset={}'
    CCategoryList = CategoryList()
    item = NeteasemusicItem()

    def start_requests(self):
        offset_list = [n * 35 for n in range(0, 2)]
        category_keywords_list = self.CCategoryList.get_mood_list()
        for keyword in category_keywords_list:
            for offset in offset_list:
                url = self.category_url.format(keyword, offset)
                yield Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        self.connect = pymysql.connect(
            host=settings.MYSQL_HOST,
            db=settings.MYSQL_DBNAME,
            user=settings.MYSQL_USER,
            passwd=settings.MYSQL_PASSWD,
            use_unicode=True)
        self.cursor = self.connect.cursor()

        r = requests.get(response.url, headers=DEFAULT_REQUEST_HEADERS)
        sel = etree.HTML(r.text)
        playlist_cat = sel.xpath('//*[@id="m-disc-pl-c"]/div/div[1]/h3/span/text()')[0]
        playlists = sel.xpath('//*[@class="u-cover u-cover-1"]')
        for playlist in playlists:
            playlist_dict = {}
            playlist_dict['playlist_cat'] = playlist_cat
            playlist_dict['playlist_name'] = playlist.xpath('a[1]/@title')[0]
            playlist_dict['playlist_id'] = playlist.xpath('a[1]/@href')[0].split('=')[-1]
            playlist_dict['playlist_url'] = self.start_urls[0] + playlist.xpath('a[1]/@href')[0]
            self.cursor.execute('select * from playlist where playlist_id = %s', (playlist_dict['playlist_id']))
            result = self.cursor.fetchall()
            if len(result) > 0:
                print('playlist id {} is already exist.'.format(playlist_dict['playlist_id']))
                continue
            else:
                yield Request(url=playlist_dict['playlist_url'], meta=playlist_dict, callback=self.parse_playlist)

    def parse_playlist(self, response):
        playlist_dict = response.meta
        r = requests.get(response.url, headers=DEFAULT_REQUEST_HEADERS)
        sel = etree.HTML(r.text)
        playlist_dict['playlist_author'] = sel.xpath('//div[@class="user f-cb"]/span/a/text()')[0]
        playlist_dict['playlist_author_id'] = sel.xpath('//div[@class="user f-cb"]/span/a/@href')[0].split('=')[-1]
        playlist_dict['playlist_pubtime'] = sel.xpath('//span[@class="time s-fc4"]/text()')[0].split()[0]
        playlist_dict['playlist_songnum'] = sel.xpath('//span[@id="playlist-track-count"]/text()')[0]
        playlist_dict['playlist_tag'] = ','.join(sel.xpath('//div[@class="tags f-cb"]/a/i/text()'))
        playlist_dict['playlist_desc'] = ''.join(sel.xpath('//p[@id="album-desc-more"]/text()'))
        playlist_dict['playlist_fav_count'] = sel.xpath('//*[@id="content-operation"]/a[3]/@data-count')[0]
        playlist_dict['playlist_share_count'] = sel.xpath('//*[@id="content-operation"]/a[4]/@data-count')[0]
        playlist_dict['playlist_comment_count'] = sel.xpath('//*[@id="cnt_comment_count"]/text()')[0]

        musics = sel.xpath('//ul[@class="f-hide"]/li/a/@href')
        for music in musics:
            music_id = music[9:]
            music_url = self.start_urls[0] + music
            music_dict = playlist_dict
            music_dict['music_id'] = music_id
            music_dict['music_url'] = music_url
            yield Request(music_url, meta=music_dict, callback=self.parse_music)

    def parse_music(self, response):
        music_dict = response.meta
        r = requests.get(response.url, headers=DEFAULT_REQUEST_HEADERS)
        sel = etree.HTML(r.text)
        self.item['music_name'] = sel.xpath('//div[@class="tit"]/em[@class="f-ff2"]/text()')[0]
        self.item['album_name'] = sel.xpath('//div[@class="cnt"]/p[2]/a/text()')[0]
        self.item['artist_name'] = ','.join(sel.xpath('//div[@class="cnt"]/p[1]/span/a/text()'))
        artist_ids = sel.xpath('//div[@class="cnt"]/p[1]/span/a/@href')
        artist_id = []
        for a in artist_ids:
            artist_id.append(a.split('=')[-1])
        self.item['artist_id'] = ','.join(artist_id)
        self.item['album_id'] = sel.xpath('//div[@class="cnt"]/p[2]/a/@href')[0].split('=')[-1]
        lrc_url = 'https://music.163.com/api/song/lyric?os=osx&' + 'id=' + str(
            music_dict['music_id']) + '&lv=1&kv=1&tv=-1'
        r = requests.get(lrc_url, headers=DEFAULT_REQUEST_HEADERS)
        json_obj = r.text
        j = json.loads(json_obj)
        try:
            lyric = j['lrc']['lyric']
            self.item['lyric'] = lyric
        except KeyError:
            self.item['lyric'] = ''

        column_list = ['playlist_id', 'playlist_name', 'playlist_cat', 'playlist_tag', 'playlist_author',
                       'playlist_author_id',
                       'playlist_pubtime', 'playlist_songnum', 'playlist_desc', 'playlist_fav_count',
                       'playlist_share_count',
                       'playlist_comment_count', 'music_id']
        for c in column_list:
            self.item[c] = music_dict[c]

        yield self.item


if __name__ == '__main__':
    execute('scrapy crawl netease'.split())
