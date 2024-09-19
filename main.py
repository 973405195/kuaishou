import pymysql,requests,re
from datetime import datetime
from time import sleep
from fake_useragent import UserAgent
import random

uas = UserAgent()

def main_(au_id,id,cookies):

    url = f'https://www.kuaishou.com/profile/{au_id}'
    # headers1 = {
    #     "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    # }
    # res = requests.get(url, headers=headers1)
    # ck = ''
    # for cookie in res.cookies:
    #     ck += cookie.name + '=' + cookie.value + ';'

    headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "max-age=0",
    "connection": "keep-alive",
    "cookie":cookies[random.randint(0,len(cookies)-1)],
    "host": "www.kuaishou.com",
    "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent":uas.random
    }
    num_count = 0
    while True:

        try:
            response = requests.get(url, headers=headers).text
            print(au_id)
            works = re.findall('"photo_public":"(.*?)"',response)[0]
            fans = re.findall('{"fan":"(.*?)"', response)[0]
            desc = re.findall('"user_text":"(.*?)","user_profile_bg_url"',response)[0]
            icon_url = re.findall('<img src="(.*?)" clas',response)[0]
            # print(works,fans,desc,icon_url)
            # # print(icon_url)
            if fans[-1:] == '万':
                fans = int(float(fans[:-1])*10000)
            if works[-1:] == '万':
                works = int(float(works[:-1]) * 10000)
            new_now = datetime.now()
            now_date = new_now.strftime('%Y-%m-%d %H:%M:%S')

            update_sql = f"UPDATE zt_ks_author SET  icon_url = '{icon_url}',video_count = {works}, fans_count = {fans},author_desc = '{desc}',create_time = '{now_date}',update_time = '{now_date}' WHERE id = {id}"
            cursor.execute(update_sql)
            db.commit()
            print(works, fans, desc, icon_url,works)
            sleep(random.randint(1,5))
            return
        except Exception as e :
            headers["cookie"] = cookies[random.randint(0,len(cookies)-1)]
            headers["user-agent"] = uas.random
            print(e)
            sleep(random.randint(1,3))
            if num_count>5:
                return



# db = pymysql.connect(host="172.17.0.142", port=3306, user="jzzt", password="jzzt#2024", database="zt")  # 服务


db = pymysql.connect(host="192.168.1.80", port=3306, user="remo80", password="juzhun2023", database="zt")

cursor = db.cursor()

select_sql = "SELECT * FROM `zt_ks_author` WHERE status_flag=1 and icon_url IS NULL "
cursor.execute(select_sql)
author_list = cursor.fetchall()
author_id = []


cookies = []
cks = 'SELECT cookie FROM zt_dy_cookies WHERE status=1 and cookies_type=2'
cursor.execute(cks)
cookie_s = cursor.fetchall()
for cook in cookie_s:
    cookies.append(cook[0])
for author in author_list:
    ids = author[0]
    author_ids = author[2].split('/')
    # author_id.append(author_ids[len(author_ids)-1])
    main_(author_ids[len(author_ids)-1],ids,cookies)
cursor.close()
db.close()
# main_('3xkr6qi5xkjaypq')

