import pymysql
from postcodeSpider.settings import *

MYSQL_HOST = '172.16.32.135'
MYSQL_DBNAME = 'address'
MYSQL_USER = 'root'
MYSQL_PASSWD = 'ai4every1'

if __name__ == '__main__':
    connect = pymysql.connect(
        host=MYSQL_HOST,
        db=MYSQL_DBNAME,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWD,
        use_unicode=True
    )
    cursor = connect.cursor()
    cursor.execute('select distinct address,province from postcode where district="1"')
    l = cursor.fetchall()
    for i in l:
        province = i[1]
        if province in ['北京市','上海市','天津市','重庆市']:
            city = i[0].split('市')[0] + '市'
            district = i[0].replace(city,'')
        elif province in ['海南省']:
            city_district = i[0].replace(province,'')
            city = city_district.split('县')[0] + '县'
            district = city
        elif i[0] == '湖北省神农架林区':
            city = '神农架林区'
            district = city
        else:
            city_district = i[0].replace(province,'')
            if '地区' in city_district:
                city = city_district.split('地区')[0] + '地区'
                district = city_district.replace(city,'')
            elif '盟' in city_district:
                city = city_district.split('盟')[0] + '盟'
                district = city_district.replace(city,'')
            elif '自治州' in city_district:
                city = city_district.split('自治州')[0] + '自治州'
                district = city_district.replace(city, '')
            elif '市' in city_district:
                city = city_district.split('市')[0] + '市'
                district = city_district.replace(city, '')
            else:
                continue
        print(province,city,district)
        cursor.execute('update postcode set city = %s, district = %s where address = %s',(city,district,i[0]))
        connect.commit()

    cursor.close()
    connect.close()
