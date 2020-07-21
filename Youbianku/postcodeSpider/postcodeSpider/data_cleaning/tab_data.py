import pymysql
from postcodeSpider.settings import *

MYSQL_HOST = '172.16.32.135'
MYSQL_DBNAME = 'address'
MYSQL_USER = 'root'
MYSQL_PASSWD = 'ai4every1'

def select():
    connect = pymysql.connect(
        host=MYSQL_HOST,
        db=MYSQL_DBNAME,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWD,
        use_unicode=True
    )
    cursor = connect.cursor()
    cursor.execute('select postcode from postcode where length(district)=0')
    result = cursor.fetchall()
    multi_district_list = []
    for i in result:
        multi_district_list.append(i[0]+'\n')
    cursor.close()
    connect.close()

    with open('../spiders/multi_district.txt', 'w', encoding='utf8') as f:
        f.writelines(multi_district_list)

if __name__ == '__main__':
    connect = pymysql.connect(
        host=MYSQL_HOST,
        db=MYSQL_DBNAME,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWD,
        use_unicode=True
    )
    cursor = connect.cursor()
    cursor.execute('delete from postcode where district="1"')
    connect.commit()
    cursor.close()
    connect.close()



