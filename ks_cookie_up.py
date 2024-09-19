from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import json
from selenium.webdriver.chrome.service import Service
import http.cookies
import pymysql,requests

def cookies_string_to_dict(cookie_string):
    cookies = http.cookies.SimpleCookie()
    cookies.load(cookie_string)
    cookie_dict = {}
    for key, morsel in cookies.items():
        cookie_dict[key] = morsel.value
    # print(cookie_dict)
    return cookie_dict
num = 0



response = requests.get('https://zt.juzhun.com/pyapi/kuaishou/').json()
cookies = response['cookie']

for c in cookies:
    print(c[0])
    service = Service(r'C:\Users\李亚航\AppData\Local\Programs\Python\Python37-32\chromedriver.exe')
    driver = webdriver.Chrome(service=service)
    # print('打开浏览器')
    # 打开抖音登录页面
    driver.get('https://www.kuaishou.com/')
    # 通过cookies登录
    cookies_ = cookies_string_to_dict(c[1])

    for cookie in cookies_:
        # print(cookie,cookies_[cookie])
        driver.add_cookie(
            {
                'domain': '.kuaishou.com',
                'name': cookie,
                'value': cookies_[cookie],
                'path': '/',
                'expires':None
            }
        )
    sleep(5)
    # 刷新页面以便cookies生效
    driver.refresh()
    # 等待页面加载完成

    sleep(5)
    try:
        # 假设登录后用户名会显示在这个元素中
        username_element = driver.find_element(By.CLASS_NAME, 'user-name')
        if username_element:
            print('登录状态:', username_element.text)
            cookies_list = driver.get_cookies()
            print(cookies_list)
            # 将cookies转换为字符串
            cookie_str = ''
            for cookie in cookies_list:
                cookie_str += f"{cookie['name']}={cookie['value']}; "
            # 打印字符串格式的cookies
            # messagebox.showinfo("提示", cookie_str)
            url = 'https://zt.juzhun.com/admin/cookies/saveCookies'
            data = {
                "name": c[0],
                "cookie": cookie_str,
                "cookiesType": 2
            }
            requests.post(url, json=data)
            print(f'{c[0]}用户已登录')
            # 此时页面已经加载完毕，可以进行后续操作
            # 例如：打印当前页面的标题
            # print(driver.title)
            # 关闭浏览器
            sleep(10)
            driver.quit()
        else:
            print('未登录')
    except:
        print('未登录')



