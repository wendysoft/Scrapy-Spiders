from appium import webdriver
import time
##创建一个字典,用于存储设备和应用信息
desired_caps={
#连接的设备信息
   'udid': '127.0.0.1:62001', # 模拟器id，通过adb devices获取
          "platformName": "Android",
         "platformVersion": "7.1.2",
        "deviceName": "SM-G977N",
        "appPackage": "com.instagram.android",
        "appActivity": "com.instagram.mainactivity.MainActivity",
        "noReset": "True" }
#与appium session之间建立联系，括号内为appium服务地址
driver = webdriver.Remote('http://localhost:4723/wd/hub',desired_caps)
driver.find_element_by_xpath('//android.widget.FrameLayout[@content-desc="Search and Explore"]').click()
time.sleep(1)
driver.find_element_by_id('com.instagram.android:id/action_bar_search_edit_text').click()
time.sleep(1)
driver.find_elements_by_id('com.instagram.android:id/tab_button_name_text')[1].click()
time.sleep(1)
driver.save_screenshot('endpos1.png')
driver.find_element_by_id('com.instagram.android:id/action_bar_search_edit_text').send_keys('_resanu_')
time.sleep(5)
driver.save_screenshot('endpos2.png')
driver.find_elements_by_id("com.instagram.android:id/row_search_user_info_container")[0].click()
time.sleep(5)
print('get likes count')
ob = driver.find_element_by_id('com.instagram.android:id/row_profile_header_textview_followers_count')
print(ob)
followers_count = ob.get_attribute('text')
print(followers_count)