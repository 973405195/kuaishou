import requests,re,json,time,os,pymysql,random
from concurrent.futures import ThreadPoolExecutor
import concurrent

db = pymysql.connect(host="192.168.1.80", port=3306, user="remo80", password="juzhun2023", database="zt")  # 测试

def extract_video_id(share_url, cookies, t_id):
    print(share_url, cookies[random.randint(0, len(cookies) - 1)], t_id)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "cookie": cookies[random.randint(0, len(cookies) - 1)]
    }
    try:
        resp = requests.get(share_url, headers=headers, allow_redirects=True)
        resure = requests.get(resp.url, headers=headers).text
        match = re.search(r'"photoUrl":"(.*?)"', resure)
        if match:
            encoded_url = match.group(1)
            decoded_url = encoded_url.encode().decode('unicode_escape')
            print(f"✅ 提取视频链接成功: {decoded_url}")
            gengxin_sql = f"UPDATE zt_material_third_task SET task_flag = 3, material_url = '{decoded_url}' WHERE id = {t_id}"
            cursor.execute(gengxin_sql)
            db.commit()
            return decoded_url  # ✅ 返回结果
        else:
            print("❌ 未找到 photoUrl 字段")
            gengxin_sql = f"UPDATE zt_material_third_task SET task_flag = 2,reason = '未找到 photoUrl 字段' WHERE id = {t_id}"
            cursor.execute(gengxin_sql)
            db.commit()
            return None
    except Exception as e:
        print(f"⚠️ 错误: {e}")
        gengxin_sql = f"UPDATE zt_material_third_task SET task_flag = 2,reason = '错误:{str(e)}' WHERE id = {t_id}"
        cursor.execute(gengxin_sql)
        db.commit()
        return None






if __name__ == '__main__':
    cursor = db.cursor()
    task_sql = "SELECT id,share_url FROM `zt_material_third_task` WHERE task_type=2 and task_flag=0"
    cursor.execute(task_sql)
    task_list = cursor.fetchall()
    task_url_list = []
    for i in task_list:
        task_url_list.append((i[1],i[0]))
    print(task_url_list)
    ids = []
    cookies = []
    # cookies
    cks = 'SELECT cookie FROM zt_dy_cookies WHERE status=1 and cookies_type=2'
    cursor.execute(cks)
    cookie_s = cursor.fetchall()
    for cook in cookie_s:
        cookies.append(cook[0])

    with ThreadPoolExecutor(max_workers=5) as executor:
        # 提交请求任务到线程池
        future_to_url = {executor.submit(extract_video_id, video_url, cookies, t_id): (video_url, t_id) for
                         (video_url, t_id) in task_url_list}
        # 收集结果
        for future in concurrent.futures.as_completed(future_to_url):
            thread_ = future_to_url[future]
            try:
                status_code = future.result()
                shipin_url = status_code[0]
                print(shipin_url)
            except Exception as exc:
                print(exc)
        concurrent.futures.wait(future_to_url)


    cursor.close()
    db.close()
    requests.get('http://172.17.20.2:5000/transcode',timeout=1200)
