import requests
import re
import json
import time
import datetime
import pymysql
import settings
from lxml import etree
from jsonpath import jsonpath

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cache-Control': 'max-age=0',
    'Cookie': 'xhsTrackerId=2a1815ab-521e-471f-c725-c74a80a0fdb6; smidV2=20191022111825a3e3ac885608d45351e570474723f053004f8fd0b15449a90; timestamp1=719450530; hasaki=JTVCJTIyTW96aWxsYSUyRjUuMCUyMChXaW5kb3dzJTIwTlQlMjAxMC4wJTNCJTIwV2luNjQlM0IlMjB4NjQpJTIwQXBwbGVXZWJLaXQlMkY1MzcuMzYlMjAoS0hUTUwlMkMlMjBsaWtlJTIwR2Vja28pJTIwQ2hyb21lJTJGNzkuMC4zOTQ1Ljc5JTIwU2FmYXJpJTJGNTM3LjM2JTIyJTJDJTIyemgtQ04lMjIlMkMyNCUyQy00ODAlMkN0cnVlJTJDdHJ1ZSUyQ3RydWUlMkMlMjJ1bmRlZmluZWQlMjIlMkMlMjJmdW5jdGlvbiUyMiUyQ251bGwlMkMlMjJXaW4zMiUyMiUyQzglMkM4JTJDbnVsbCUyQyUyMkNocm9tZSUyMFBERiUyMFBsdWdpbiUzQSUzQVBvcnRhYmxlJTIwRG9jdW1lbnQlMjBGb3JtYXQlM0ElM0FhcHBsaWNhdGlvbiUyRngtZ29vZ2xlLWNocm9tZS1wZGZ+cGRmJTNCQ2hyb21lJTIwUERGJTIwVmlld2VyJTNBJTNBJTNBJTNBYXBwbGljYXRpb24lMkZwZGZ+cGRmJTNCTmF0aXZlJTIwQ2xpZW50JTNBJTNBJTNBJTNBYXBwbGljYXRpb24lMkZ4LW5hY2x+JTJDYXBwbGljYXRpb24lMkZ4LXBuYWNsfiUyMiUyQzM0NDE5NzA0NzclNUQ=; timestamp2=652fac245831222794e6b7951e0a5210; extra_exp_ids=; xhs_spses.5dde=*; xhs_spid.5dde=d263b57731edaf18.1566903324.14.1576567421.1576565380.bd422c9e-182b-4e55-bcab-a9b25ea1bc81',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Site': 'none',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
    'Host': 'www.xiaohongshu.com',
    'Connection': 'keep-alive'
    # 'Refer':'https://www.xiaohongshu.com/web-login/captcha?redirectPath=http%3A%2F%2Fwww.xiaohongshu.com%2Fdiscovery%2Fitem%2F{}'.format(id),
}

def connect_mysql():
    connect = pymysql.connect(
        host=settings.MYSQL_HOST,
        db=settings.MYSQL_DBNAME,
        user=settings.MYSQL_USER,
        passwd=settings.MYSQL_PASSWD,
        use_unicode=True)
    return connect

def get_end_day(day):
    return day - (datetime.timedelta(days=5))

if __name__ == '__main__':
    end_day =str(get_end_day(datetime.date.today()))
    connect = connect_mysql()
    cursor = connect.cursor()
    cursor.execute(
        'select id from xhs where pub_time is Null and insert_time > %s',(end_day))
    cursor.scroll(0,mode='absolute')
    results =cursor.fetchall()
    rule = re.compile('(http:\/\/sns-img-qn.xhscdn.com\/[-a-zA-Z0-9\/?]{0,100}\/webp)')
    for item in results:
        id = item[0]
        url = 'https://www.xiaohongshu.com/discovery/item/{}'.format(id)
        r = requests.get(url,headers = headers)
        sel = etree.HTML(r.text)
        data = ''.join(sel.xpath('/html/head/script/text()'))
        try:
            data = json.loads(data)
            print(json.dumps(data, sort_keys=True, indent=2))
            title = ''.join(jsonpath(data,'$.headline'))
            description = ''.join(jsonpath(data,'$.description'))
            pub_time = jsonpath(data,'$.datePublished')[0].split('T')[0]
            cursor.execute('update xhs set title = %s, description = %s, pub_time = %s where id = %s', (title, description, pub_time, id))
            connect.commit()
            print(id)
        except Exception as e:
            print(id,e)

    cursor.close()
    connect.close()