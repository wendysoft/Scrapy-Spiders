from appium import webdriver
import time
import random


def slide_app(keywords):
    # 初始化配置，设置Desired Capabilities参数
    desired_caps = {
        'platformName': 'Android',
        'platformVersion': '5.1.1',
        'deviceName': 'OPPO R11',
        'appPackage': 'com.xingin.xhs',
        'appActivity': '.index.IndexNewActivity',
        'noReset': 'True',
        'unicodeKeyboard': 'True'
    }

    # 指定Appium Server
    server = 'http://localhost:4723/wd/hub'

    # 新建一个driver
    driver = webdriver.Remote(server, desired_caps)
    # # 获取模拟器/手机的分辨率(px)

    # print(width, height)

    search = driver.find_element_by_id('com.xingin.xhs:id/a8f').click()
    time.sleep(10)
    text = driver.find_element_by_id('com.xingin.xhs:id/b5q')
    time.sleep(10)
    text.send_keys(keywords)
    button = driver.find_element_by_id('com.xingin.xhs:id/b5t').click()
    time.sleep(10)
    latest_post = driver.find_element_by_id('com.xingin.xhs:id/b5h').click()
    time.sleep(10)

    width = driver.get_window_size()['width']
    height = driver.get_window_size()['height']
    slide = 0

    while slide < 100:
        print('Keywords: {}, Slide: {}/100'.format(keywords,slide))
        posts = driver.find_elements_by_id('com.xingin.xhs:id/b61')
        driver.swipe(width * 0.5, height * 0.75, width * 0.5, height * 0.25)
        slide = slide + 1
        time.sleep(random.uniform(2, 5))

    # ****************Connection aborted.*****************************************
    # width = driver.get_window_size()['width']
    # height = driver.get_window_size()['height']
    # slide =0
    # num = 0
    #
    # while slide < 10:
    #     posts = driver.find_elements_by_id('com.xingin.xhs:id/b61')
    #     print(len(posts))
    #     try:
    #         for i in range(len(posts)):
    #             print('i:{}',format(i))
    #             posts[i].click()
    #             time.sleep(random.uniform(5,10))
    #             # driver.swipe(width * 0.5, height * 0.75, width * 0.5, height * 0.25)
    #             # pub_time = driver.find_element_by_id('com.xingin.xhs:id/bfy').text
    #             # print(pub_time)
    #             back = driver.find_element_by_id('com.xingin.xhs:id/i8').click()
    #             time.sleep(random.uniform(2,5))
    #         driver.swipe(width * 0.5, height * 0.75, width * 0.5, height * 0.25)
    #     except Exception as e:
    #         driver.swipe(width*0.5,height*0.75,width*0.5,height*0.25)
    #     # driver.swipe(width * 0.5, height * 0.75, width * 0.5, height * 0.25)
    #     slide = slide + 1
    #     num = num + 4
    #     time.sleep(random.uniform(5,10))
    # **********************************************************************************

    driver.save_screenshot('endpos.png')


def run():
    # '一甜相机','水柚相机'太少
    keywords_list = ['b612', '轻颜', 'zepeto', 'faceu']
    for keywords in keywords_list:
        print('Start Spider...')
        print('Keywords: {}'.format(keywords))
        slide_app(keywords)
        time.sleep(60)


if __name__ == '__main__':
    run()
