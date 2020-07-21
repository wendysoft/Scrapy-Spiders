import pymysql

MYSQL_HOST = '172.16.32.135'
MYSQL_DBNAME = 'address'
MYSQL_USER = 'root'
MYSQL_PASSWD = 'ai4every1'

province_list= ['黑龙江省',
                '吉林省',
                '辽宁省',
                '河北省',
                '山西省',
                '江苏省',
                '浙江省',
                '安徽省',
                '福建省',
                '江西省',
                '山东省',
                '河南省',
                '湖北省',
                '湖南省',
                '广东省',
                '海南省',
                '四川省',
                '贵州省',
                '云南省',
                '陕西省',
                '甘肃省',
                '青海省',
                '台湾省']

zizhiqu_list = ['内蒙古自治区',
                '新疆维吾尔自治区',
                '广西壮族自治区',
                '宁夏回族自治区',
                '西藏自治区']

if __name__ == '__main__':
    connect = pymysql.connect(
        host=MYSQL_HOST,
        db=MYSQL_DBNAME,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWD,
        use_unicode=True
    )
    cursor = connect.cursor()
    # for i in zizhiqu_list:
    #     cursor.execute('select distinct province,city from postcode where province = %s',(i))
    #     city = cursor.fetchall()
    #     print('City:{},{}'.format(len(city),city))
    #     cursor.execute('select distinct province,city,district from postcode where province = %s',(i))
    #     district = cursor.fetchall()
    #     print('District:{},{}'.format(len(district), district))

    cursor.execute('select distinct(postcode) from postcode')
    result = cursor.fetchall()
    print(len(result))
    new = list()
    for i in result:
        new.append(i[0])
    cursor.close()
    connect.close()

    with open('../spiders/last_postcode.txt', encoding='utf8') as f:
        content = f.readlines()
        old = [i.strip('\n') for i in content]
    print(old)

    for i in old:
        if i not in new:
            print(i)






