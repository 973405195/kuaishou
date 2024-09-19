import json

import requests, pymysql
from fake_useragent import UserAgent
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import concurrent
from setuptools.wheel import Wheel
import threading
from time import sleep
import logging, random

uas = UserAgent()
mutex = threading.Lock()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 设置日志级别
file_handler = logging.FileHandler('example.log')  # 创建一个文件处理器，用于将日志写入文件
file_handler.setLevel(logging.DEBUG)  # 设置文件的日志级别
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')  # 创建一个formatter并设置日志格式
file_handler.setFormatter(formatter)  # 将formatter设置到handler上
logger.addHandler(file_handler)  # 将处理器添加到记录器中
logger.info('任务启动')

def spider_(author_id, cookies):
    url = 'https://www.kuaishou.com/graphql'


    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh-CN,zh;q=0.9",
        "connection": "keep-alive",
        "content-length": "1784",
        "content-type": "application/json",
        "cookie": cookies[random.randint(0,4)],
        "host": "www.kuaishou.com",
        "origin": "https://www.kuaishou.com",
        "referer": "https://www.kuaishou.com/profile/3xuj7uqrg43yw3w",
        "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": uas.random
    }
    data = {
        "operationName": "visionProfilePhotoList",
        "variables": {
            "userId": author_id,
            "pcursor": "",
            "page": "profile"
        },
        "query": "fragment photoContent on PhotoEntity {\n  __typename\n  id\n  duration\n  caption\n  originCaption\n  likeCount\n  viewCount\n  commentCount\n  realLikeCount\n  coverUrl\n  photoUrl\n  photoH265Url\n  manifest\n  manifestH265\n  videoResource\n  coverUrls {\n    url\n    __typename\n  }\n  timestamp\n  expTag\n  animatedCoverUrl\n  distance\n  videoRatio\n  liked\n  stereoType\n  profileUserTopPhoto\n  musicBlocked\n  riskTagContent\n  riskTagUrl\n}\n\nfragment recoPhotoFragment on recoPhotoEntity {\n  __typename\n  id\n  duration\n  caption\n  originCaption\n  likeCount\n  viewCount\n  commentCount\n  realLikeCount\n  coverUrl\n  photoUrl\n  photoH265Url\n  manifest\n  manifestH265\n  videoResource\n  coverUrls {\n    url\n    __typename\n  }\n  timestamp\n  expTag\n  animatedCoverUrl\n  distance\n  videoRatio\n  liked\n  stereoType\n  profileUserTopPhoto\n  musicBlocked\n  riskTagContent\n  riskTagUrl\n}\n\nfragment feedContent on Feed {\n  type\n  author {\n    id\n    name\n    headerUrl\n    following\n    headerUrls {\n      url\n      __typename\n    }\n    __typename\n  }\n  photo {\n    ...photoContent\n    ...recoPhotoFragment\n    __typename\n  }\n  canAddComment\n  llsid\n  status\n  currentPcursor\n  tags {\n    type\n    name\n    __typename\n  }\n  __typename\n}\n\nquery visionProfilePhotoList($pcursor: String, $userId: String, $page: String, $webPageArea: String) {\n  visionProfilePhotoList(pcursor: $pcursor, userId: $userId, page: $page, webPageArea: $webPageArea) {\n    result\n    llsid\n    webPageArea\n    feeds {\n      ...feedContent\n      __typename\n    }\n    hostName\n    pcursor\n    __typename\n  }\n}\n"
    }

    while True:
        response = requests.post(url, json=data, headers=headers).json()
        pcursor = response["data"]["visionProfilePhotoList"]["pcursor"]  # 翻页
        data["variables"]["pcursor"] = str(pcursor)
        data_list = response["data"]["visionProfilePhotoList"]["feeds"]

        # print(data_list)
        # input()

        if len(data_list) != 0:
            for photo in data_list:
                caption = photo["photo"]["caption"]
                likeCount = photo["photo"]["realLikeCount"]
                photoUrl = photo["photo"]["photoUrl"]
                video_id = photo["photo"]["id"]
                durations = photo["photo"]["duration"]

                duration = float(int(durations) / 1000)  # 获取影片时常
                minute = float(duration) // 60
                second = float(duration) % 60
                dura = f'{str(int(minute))}:{str(int(second))}'

                date_time = photo["photo"]["timestamp"]  # 影片发布时间
                dt_object = datetime.fromtimestamp(date_time / 1000)  # 13位时间戳进行转换
                formatted_date = dt_object.strftime('%Y-%m-%d %H:%M:%S')

                threshold = 3 * 24 * 60 * 60  # 设置三天前得时间
                now = datetime.now().timestamp()  # 获取当前时间
                # 打印当前日期和时间到分钟
                new_now = datetime.now()
                now_date = new_now.strftime('%Y-%m-%d %H:%M:%S')

                name = photo["author"]["name"]  # 达人名字
                # author_id = photo["author"]["name"]  # id
                tags = photo["tags"]  # 标签
                manifest = photo["photo"]["manifest"]["adaptationSet"][0]["representation"][0]["qualityType"]  # 分辨率大小

                new_tag = ''
                if tags != None:
                    for tag in tags:
                        t = tag["name"]
                        # print(t)
                        new_tag += '#' + t
                logger.info(photo["photo"]["profileUserTopPhoto"])
                if now - (date_time / 1000) > threshold:  # 进行三天时间判断

                    if photo["photo"]["profileUserTopPhoto"] == 'true':  # 判断视频是否为置顶
                        print('置顶视频跳过')
                    else:
                        print('超过三天退出')
                        return '超过三天退出'
                else:
                    mutex.acquire()
                    sql = f"SELECT * FROM `zt_ks` WHERE video_id='{video_id}'"

                    cursor.execute(sql)
                    video_id_list = cursor.fetchall()
                    preview_url = f"https://www.kuaishou.com/short-video/{video_id}?authorId={author_id}&streamSource=profile&area=profilexxnull"
                    print(author_id)
                    if len(video_id_list) == 0:
                        insert_sql = (
                            f"INSERT INTO zt_ks (author_id,author_name, playlet_title, playlet_url, issue_time, "
                            f"create_time,update_time,digg_count, three_digg_count, video_id, playlet_tag, "
                            f"playlet_duration, playlet_size,preview_url) VALUES ('{author_id}','{name}','{caption}','{photoUrl}',"
                            f"'{dt_object}','{now_date}','{now_date}',{likeCount},{0},'{video_id}','{new_tag}',"
                            f"'{dura}','{manifest}','{preview_url}')")
                        print(insert_sql)
                        cursor.execute(insert_sql)
                        db.commit()
                        logger.info(f"达人名字：{name} decs：{caption} 视频ID：{video_id}")

                    else:

                        three_likeCount = int(likeCount) - video_id_list[0][8]
                        update_sql = f"UPDATE zt_ks SET  update_time = '{now_date}',digg_count = {likeCount}, three_digg_count = {three_likeCount}, preview_url='{preview_url}' WHERE video_id = '{video_id}'"
                        cursor.execute(update_sql)
                        db.commit()
                        logger.info('存在需要更新')
                        # print('存在需要更新')
                    mutex.release()
                    sleep(random.randint(1, 3))


        else:
            print('空的数据')
            return '空'


# db = pymysql.connect(host="172.17.0.142", port=3306, user="jzzt", password="jzzt#2024", database="zt")  # 服务

db = pymysql.connect(host="192.168.1.80", port=3306, user="remo80", password="juzhun2023", database="zt")
cursor = db.cursor()

select_sql = "SELECT author_url FROM `zt_ks_author` WHERE author_url!='' and status_flag=1"
cursor.execute(select_sql)
author_list = cursor.fetchall()
author_id = []
for author in author_list:
    author_ids = author[0].split('/')
    author_id.append(author_ids[len(author_ids) - 1])
cookies = []
cks = 'SELECT cookie FROM zt_dy_cookies WHERE status=1 and cookies_type=2'
cursor.execute(cks)
cookie_s = cursor.fetchall()
for cook in cookie_s:
    cookies.append(cook[0])

# with ThreadPoolExecutor(max_workers=3) as executor:
#     # 提交请求任务到线程池
#     future_to_url = {executor.submit(spider_, au_id, cookies): au_id for au_id in author_id}
#     # 收集结果
#     for future in concurrent.futures.as_completed(future_to_url):
#         thread_ = future_to_url[future]
#
#         # try:
#         #     status_code = future.result()
#         #
#         # except Exception as exc:
#         #     print(exc)
#     concurrent.futures.wait(future_to_url)
#
# logger.info('任务结束')
# cursor.close()
# db.close()

spider_('3x5bhpnp9kacggk',cookies)