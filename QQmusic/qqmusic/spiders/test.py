import scrapy
import json
import requests
from selenium import webdriver
import re
from scrapy.cmdline import execute
from scrapy import Request
from lxml import etree
from urllib.parse import urlencode
from qqmusic.settings import DEFAULT_REQUEST_HEADERS

playlist_headers = DEFAULT_REQUEST_HEADERS
playlist_headers['Referer'] = 'https://y.qq.com/portal/playlist.html'

def get_dist_info(page,categoryId):
    print(page)
    url = 'https://c.y.qq.com/splcloud/fcgi-bin/fcg_get_diss_by_tag.fcg?'
    print(url)
    params = {
        'picmid': '1',
        'rnd': '0.15993662911508766',
        'g_tk': '5381',
        'loginUin': '0',
        'hostUin': '0',
        'format': 'json',
        'inCharset': 'utf8',
        'outCharset': 'utf-8',
        'notice': '0',
        'platform': 'yqq.json',
        'needNewCode': '0',
        'categoryId': categoryId,
        'sortId': '5',
        'sin': int(page)*30-30,
        'ein': int(page)*30-1,
    }
    url += urlencode(params)
    r = requests.get(url, headers=playlist_headers)
    result = r.json()
    disslist = result['data']['list']
    print(json.dumps(r.json(), sort_keys=True, indent=2, ensure_ascii=False))
    print(disslist)

def get_song_info(disstid):
    params = {
        'type':'1',
        'json':'1',
        'utf8':'1',
        'onlysong':'0',
        'new_format':'1',
        'disstid':disstid,
        'g_tk':'5381',
        'loginUin':'0',
        'hostUin':'0',
        'format':'json',
        'inCharset':'utf-8',
        'notice':'0',
        'platform':'yqq.json',
        'needNewCode':'0'
    }
    url = 'https://c.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg?'
    url += urlencode(params)
    print(url)
    r = requests.get(url,headers = playlist_headers)
    print(r.text)
    print(json.dumps(r.json(), sort_keys=True, indent=2, ensure_ascii=False))

def get_vkey(mid):
    url = 'https://u.y.qq.com/cgi-bin/musicu.fcg?'
    params = {
        '-': 'getplaysongvkey7256617694143965',
        'g_tk': '5381',
        'loginUin': '0',
        'hostUin': '0',
        'format': 'json',
        'inCharset': 'utf8',
        'outCharset': 'utf-8',
        'notice': '0',
        'platform': 'yqq.json',
        'needNewCode': '0',
        'data': '{"req_0":{"module":"vkey.GetVkeyServer","method":"CgiGetVkey","param":{"guid":"5300386295","songmid":["%s"],"songtype":[0],"uin":"0","loginflag":1,"platform":"20"}},"comm":{"uin":0,"format":"json","ct":24,"cv":0}}' % mid
    }
    url += urlencode(params)
    r = requests.get(url,headers = playlist_headers)
    result = r.json()
    vkey = result['req_0']['data']['midurlinfo'][0]['vkey']
    print(vkey)
    return vkey

def down_song(path, media_mid, vkey):
    params = {
        'guid': '5300386295',
        'vkey': vkey,
        'uin': '0',
        'fromtag': '66'
    }
    url = 'http://222.73.132.154/amobile.music.tc.qq.com/C400{}.m4a?'.format(media_mid)
    url += urlencode(params)
    r = requests.get(url, headers=playlist_headers)
    print(url)
    if r.status_code in [200, 201]:
        with open(path, 'wb') as f:
            f.write(r.content)

def get_lyrics():
    params = {
        'nobase64': 1,
        'musicid': 213332679,
        '-': 'jsonp1',
        'g_tk': 5381,
        'loginUin': 0,
        'hostUin': 0,
        'format': 'json',
        'inCharset': 'utf8',
        'outCharset': 'utf-8',
        'notice': 0,
        'platform': 'yqq.json',
        'needNewCode': 0,
    }
    url = 'https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_yqq.fcg?'
    url += urlencode(params)
    r = requests.get(url, headers=playlist_headers)
    print(r.text)


if __name__ == '__main__':
    # get_lyrics()
    # get_dist_info(1,52)
    # get_song_info(7083719830)
    # mid = '001CsX4D4YLD1C'
    # name = '夏天的风'
    # media_mid = '000d3zCA0cSpWE'
    # path = 'C:/Users/W/Desktop/1.m4a'
    # vkey = '642011211021111BBCE38126B3F02D92B33E1408EB6FC9E00E427B1F53606506CE069E8544FC4BC994AAA149C3F591F0C2E9F3D5451FB4B1'
    # # get_vkey(mid)
    # down_song(path, media_mid, vkey)
    with open('C:/Users/W/Desktop/lyric.txt','r') as f:
        lyric = f.read()
        print(lyric)
    html_char = {}
    html_char['&#10;'] = ''
    html_char['&#58;'] = ':'
    html_char['&#32;'] = ' '
    html_char['&#45;'] = '-'
    html_char['&#46;'] = '.'
    html_char['&#40;'] = '('
    html_char['&#41;'] = ')'
    number_char = re.compile(r'&#\d+;',re.I)
    for char in number_char.findall(lyric):
        lyric = re.sub(char,html_char[char],lyric)
    print(lyric)