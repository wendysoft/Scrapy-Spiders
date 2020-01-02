import scrapy
import requests
import logging
import re
import time
import pymysql
from jsonpath import jsonpath
from scrapy.cmdline import execute
from scrapy import Request
from qqmusic import settings
from qqmusic.functions.dictionary import CategoryDict,HtmlDict
from qqmusic.functions.params import Params
from qqmusic.functions.function import Function
from qqmusic.settings import DEFAULT_REQUEST_HEADERS
from qqmusic.items import QqmusicItem,QqcommentItem

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class playlistSpider(scrapy.Spider):
    name = 'qqmusic'
    start_urls = ['https://y.qq.com']
    playlist_url = 'https://c.y.qq.com/splcloud/fcgi-bin/fcg_get_diss_by_tag.fcg?'
    songinfo_url = 'https://c.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg?'
    download_url = 'http://222.73.132.154/amobile.music.tc.qq.com/C400{}.m4a?'
    lyric_url = 'https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_yqq.fcg?'
    CCategorydict = CategoryDict()
    CHtmldict = HtmlDict()
    Cparams = Params()
    CFunction = Function()
    item = QqmusicItem()

    def start_requests(self):
        category_id_list = list(self.CCategorydict.get_all_dict().keys())
        for id in category_id_list:
            url = 'https://y.qq.com/portal/playlist.html#t3=1&t2=5&t1={}&'.format(id)
            print(url)
            yield Request(url=url,meta={'category_id':id},callback=self.parse_playlist,dont_filter = True)

    def parse_playlist(self,response):
        self.connect = pymysql.connect(
            host=settings.MYSQL_HOST,
            db=settings.MYSQL_DBNAME,
            user=settings.MYSQL_USER,
            passwd=settings.MYSQL_PASSWD,
            use_unicode=True)
        self.cursor = self.connect.cursor()

        category_id = response.meta['category_id']
        self.item['playlist_cat'] = self.CCategorydict.number_to_word(number=int(category_id))
        for page in range(0,5):
            params_p = self.Cparams.get_playlist_params(page=5, categoryId=category_id)
            url_p = self.CFunction.get_url_with_params(self.playlist_url,params_p)
            r_p = requests.get(url_p,headers = DEFAULT_REQUEST_HEADERS)
            result_p = r_p.json()
            playlist_list = jsonpath(result_p, '$.data.list')[0]
            for playlist in playlist_list:
                try:
                    self.item['playlist_pubtime'] = jsonpath(playlist,'$.commit_time')[0]
                    self.item['playlist_author'] = jsonpath(playlist,'$.creator.name')[0]
                    self.item['playlist_author_qq'] = jsonpath(playlist,'$.creator.qq')[0]
                    self.item['playlist_id'] = jsonpath(playlist,'$.dissid')[0]
                    self.item['playlist_name'] = jsonpath(playlist,'$.dissname')[0]
                    self.item['playlist_listen_count'] = jsonpath(playlist,'$.listennum')[0]
                    params_s = self.Cparams.get_info_params(disstid=self.item['playlist_id'])
                    url_s = self.CFunction.get_url_with_params(self.songinfo_url, params_s)
                    r_s = requests.get(url_s, headers=DEFAULT_REQUEST_HEADERS)
                    result_s = r_s.json()
                    song_list = jsonpath(result_s,'$.cdlist[0].songlist')[0]
                    self.item['playlist_desc'] = jsonpath(result_s,'$.cdlist[0].desc')[0]
                    self.item['playlist_songids'] = jsonpath(result_s,'$.cdlist[0].songids')[0]
                    self.item['playlist_songnum'] = jsonpath(result_s,'$.cdlist[0].total_song_num')[0]
                    self.item['playlist_tag'] = ','.join(jsonpath(result_s,'$.cdlist[0].tags..name'))
                    self.item['playlist_tagids'] = ','.join([str(i) for i in jsonpath(result_s, '$.cdlist[0].tags..id')])
                    self.cursor.execute('select * from playlist where playlist_id = %s', (self.item['playlist_id']))
                    result = self.cursor.fetchall()
                    if result is not None:
                        print('playlist id {} is already exist.'.format(self.item['playlist_id']))
                        logging.error('playlist id {} is already exist.'.format(self.item['playlist_id']))
                        self.cursor.execute(
                            '''insert ignore into playlist (playlist_id, playlist_name, playlist_cat, playlist_tag, playlist_tagids,
                             playlist_author, playlist_author_qq, playlist_pubtime, playlist_songids, playlist_songnum, playlist_desc,
                             playlist_listen_count) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ''',
                            (self.item['playlist_id'], self.item['playlist_name'], self.item['playlist_cat'], self.item['playlist_tag'],
                             self.item['playlist_tagids'],
                             self.item['playlist_author'], self.item['playlist_author_qq'], self.item['playlist_pubtime'],
                             self.item['playlist_songids'],
                             self.item['playlist_songnum'], self.item['playlist_desc'], self.item['playlist_listen_count']))
                        continue
                    else:
                        for song in song_list:
                            self.item['album_id'] = jsonpath(song,'$.album.id')[0]
                            self.item['album_mid'] = jsonpath(song,'$.album.mid')[0]
                            self.item['album_name'] = jsonpath(song,'$.album.name')[0]
                            self.item['album_subtitle'] = jsonpath(song,'$.album.subtitle')[0]
                            self.item['music_media_mid'] = jsonpath(song,'$.file.media_mid')[0]
                            self.item['music_id'] = jsonpath(song, '$.id')[0]
                            self.item['music_mid'] = jsonpath(song,'$.mid')[0]
                            self.item['music_mv_mid'] = jsonpath(song,'$.mv.vid')[0]
                            self.item['music_name'] = jsonpath(song,'$.name')[0]
                            artist = jsonpath(song, '$.singer')[0]
                            self.item['artist_id'] = jsonpath(song, '$.singer[*].id')[0]
                            self.item['artist_mid'] = jsonpath(song, '$.singer[*].mid')[0]
                            self.item['artist_name'] = jsonpath(song, '$.singer[*].name')[0]

                            if len(artist) >1:
                                artist_id = [str(i) for i in jsonpath(song, '$.singer[*].id')]
                                self.item['artist_id'] = ','.join(artist_id)
                                artist_mid = [str(i) for i in jsonpath(song, '$.singer[*].mid')]
                                self.item['artist_mid'] = ','.join(artist_mid)
                                self.item['artist_name'] = ','.join(jsonpath(song, '$.singer[*].name'))

                            self.item['music_songtype'] = jsonpath(song,'$.songtype')[0]
                            self.item['music_genre'] = jsonpath(song, '$.genre')[0]
                            self.item['music_language'] = jsonpath(song, '$.language')[0]
                            self.item['music_pubtime'] = jsonpath(song,'$.time_public')[0]
                            params_l = self.Cparams.get_lyric_params(music_id=self.item['music_id'])
                            url_l = self.CFunction.get_url_with_params(self.lyric_url,params_l)
                            r_l = requests.get(url_l,headers = DEFAULT_REQUEST_HEADERS)
                            result_l = r_l.json()
                            lyric = jsonpath(result_l,'$.lyric')[0]
                            html_char_pattern = re.compile(r'&#\d+;',re.I)
                            html_char_dict = self.CHtmldict.get_all_dict()
                            for c in html_char_pattern.findall(lyric):
                                try:
                                    html_to_char = html_char_dict[c]
                                except KeyError as e:
                                    html_to_char = ''
                                    print('KeyError: {}'.format(e))
                                    logging.error('KeyError: {}'.format(e))
                                    pass
                                lyric = re.sub(c, html_to_char, lyric)
                            self.item['lyric'] = ''.join(lyric)
                            yield self.item
                except TypeError as e:
                    print('TypeError: {}'.format(e))
                    logging.error('TypeError: {}'.format(e))
                continue

class commentSpider(scrapy.Spider):
    name = 'qqcomment'
    Cparams = Params()
    CFunction = Function()
    comment_url = 'https://c.y.qq.com/base/fcgi-bin/fcg_global_comment_h5.fcg?'
    start_urls = ['https://y.qq.com']
    item = QqcommentItem()

    def start_requests(self):
        # music_ids = ['1530858']
        self.connect = pymysql.connect(
            host=settings.MYSQL_HOST,
            db=settings.MYSQL_DBNAME,
            user=settings.MYSQL_USER,
            passwd=settings.MYSQL_PASSWD,
            use_unicode=True)
        self.cursor = self.connect.cursor()
        self.cursor.execute('select distinct music_id from music limit 20000 offset 130000')
        music_ids = self.cursor.fetchall()
        for id in music_ids:
            url = 'https://y.qq.com/n/yqq/song/{}.html'.format(id[0])
            yield Request(url=url,callback=self.parse,meta={'music_id':id[0]})

    def parse(self, response):
        music_id = response.meta['music_id']
        self.item['music_id'] = music_id
        params = self.Cparams.get_comment_params(music_id=music_id,page=0,last_comment_id='')
        url = self.CFunction.get_url_with_params(self.comment_url,params)
        r = requests.get(url,params=params, headers = DEFAULT_REQUEST_HEADERS)
        result = r.json()
        hot_comment_list = jsonpath(result,'$.hot_comment.commentlist')[0]
        if len(hot_comment_list) > 0 :
            for comment in hot_comment_list:
                self.item['user_avatar_link'] = jsonpath(comment,'$.avatarurl')[0]
                self.item['comment_id'] = jsonpath(comment,'$.commentid')[0]
                self.item['is_hot'] = jsonpath(comment,'$.is_hot')[0]
                self.item['is_hot_cmt'] = jsonpath(comment,'$.is_hot_cmt')[0]
                self.item['is_medal'] = jsonpath(comment,'$.is_medal')[0]
                self.item['is_stick'] = jsonpath(comment,'$.is_stick')[0]
                self.item['is_praise'] = jsonpath(comment,'$.ispraise')[0]
                self.item['user_uin'] = jsonpath(comment,'$.uin')[0]
                self.item['user_nickname'] = jsonpath(comment, '$.nick')[0]
                self.item['content'] = ''.join(jsonpath(comment, '$.rootcommentcontent'))
                timestamp = jsonpath(comment, '$.time')[0]
                self.item['pub_time'] = time.strftime('%Y-%m-%d', time.localtime(int(timestamp)))
                self.item['liked'] = jsonpath(comment, '$.praisenum')[0]
                yield self.item

if __name__ == '__main__':
    execute('scrapy crawl qqcomment'.split())





