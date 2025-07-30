import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)

import mns_common.api.proxies.liu_guan_proxy_api as liu_guan_proxy_api
import pandas as pd
import mns_common.utils.data_frame_util as data_frame_util
from mns_common.db.MongodbUtil import MongodbUtil
import mns_common.constant.db_name_constant as db_name_constant
import datetime
import requests
import time
from loguru import logger
from functools import lru_cache

mongodb_util = MongodbUtil('27017')


def query_liu_guan_proxy_ip():
    ip_proxy_pool = mongodb_util.find_all_data(db_name_constant.IP_PROXY_POOL)
    return ip_proxy_pool


def remove_proxy_ip():
    mongodb_util.remove_data({}, db_name_constant.IP_PROXY_POOL)


def check_valid(ip_proxy_pool):
    effect_time = list(ip_proxy_pool['effect_time'])[0]

    now_date = datetime.datetime.now()

    str_now_date = now_date.strftime('%Y-%m-%d %H:%M:%S')

    if effect_time > str_now_date:
        return True
    else:
        remove_proxy_ip()
        return False


@lru_cache(maxsize=None)
def get_account_cache():
    query = {"type": "liu_guan_proxy", }
    return mongodb_util.find_query_data(db_name_constant.STOCK_ACCOUNT_INFO, query)


def generate_proxy_ip_api(minutes):
    stock_account_info = get_account_cache()
    order_id = list(stock_account_info['password'])[0]
    secret = list(stock_account_info['account'])[0]
    # 获取10分钟动态ip
    ip = liu_guan_proxy_api.get_proxy_api(order_id, secret, str(60 * minutes))
    return ip


def generate_proxy_ip(minutes):
    ip_proxy_pool = mongodb_util.find_all_data(db_name_constant.IP_PROXY_POOL)
    if data_frame_util.is_not_empty(ip_proxy_pool):
        return list(ip_proxy_pool['ip'])[0]
    else:
        remove_proxy_ip()
        now_date = datetime.datetime.now()
        # 加上分钟
        time_to_add = datetime.timedelta(minutes=minutes)
        new_date = now_date + time_to_add
        str_now_date = new_date.strftime('%Y-%m-%d %H:%M:%S')

        # 获取10分钟动态ip
        while True:
            ip = generate_proxy_ip_api(minutes)
            if check_proxy(ip, timeout=2):
                break
            else:
                time.sleep(0.5)
        result_dict = {"_id": ip,
                       'effect_time': str_now_date,
                       'ip': ip}
        result_df = pd.DataFrame(result_dict, index=[1])

        mongodb_util.insert_mongo(result_df, db_name_constant.IP_PROXY_POOL)

        return ip


def get_proxy_ip(minutes):
    ip_proxy_pool = query_liu_guan_proxy_ip()
    if data_frame_util.is_empty(ip_proxy_pool):
        return generate_proxy_ip(minutes)
    else:
        if check_valid(ip_proxy_pool):
            return list(ip_proxy_pool['ip'])[0]
        else:
            return generate_proxy_ip(minutes)


def check_baidu_proxy(proxy_ip, timeout=2):
    """
    检测代理IP是否能访问百度
    :param proxy_ip: 代理IP地址
    :param proxy_port: 代理端口
    :param timeout: 超时时间(秒)
    :return: (是否可用, 响应时间, 检测结果信息)
    """
    # 构造代理地址

    # 设置代理参数
    proxies = {
        "http": proxy_ip,
        "https": proxy_ip
    }

    # 模拟浏览器请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive"
    }

    try:
        # 记录开始时间
        start_time = time.time()

        # 发送请求到百度
        response = requests.get(
            url="https://www.baidu.com",
            proxies=proxies,
            headers=headers,
            timeout=timeout,
            allow_redirects=True  # 允许重定向
        )

        # 计算响应时间
        response_time = round((time.time() - start_time) * 1000)  # 毫秒
        # 检查响应状态和内容
        if response.status_code == 200:
            # 验证是否返回百度页面
            if "百度一下" in response.text and "baidu.com" in response.text:
                logger.info("代理ip可用:{},响应时间:{}", proxy_ip, response_time)
                return True
            else:
                logger.error("代理ip不可用:{},响应时间:{}", proxy_ip, response_time)
                return False
        else:
            logger.error("代理ip不可用:{},响应时间:{},HTTP状态码异常:{}", proxy_ip, response_time, response.status_code)
            return False
    except requests.exceptions.ConnectTimeout:
        logger.error("代理ip不可用:{},连接超时", proxy_ip, response_time)
        return False
    except requests.exceptions.ProxyError:
        logger.error("代理ip不可用:{},代理拒绝连接", proxy_ip, response_time)
        return False
    except requests.exceptions.SSLError:
        logger.error("代理ip不可用:{},SSL证书错误", proxy_ip, response_time)
        return False
    except requests.exceptions.RequestException as e:
        logger.error("代理ip不可用:{},网络错误:{}", proxy_ip, str(e))
        return False


def check_proxy(proxy_ip, timeout=2):
    proxies = {
        "http": proxy_ip,
        "https": proxy_ip
    }
    try:
        # 测试请求（httpbin.org 返回请求的IP）
        response = requests.get(
            "http://httpbin.org/ip",
            proxies=proxies,
            timeout=timeout  # 超时时间
        )
        if response.status_code == 200:
            return True
        else:
            logger.error("代理ip不可用:{}", proxy_ip)
            return False
    except Exception as e:
        logger.error("代理ip不可用:{},{}", proxy_ip, e)
        return False


if __name__ == "__main__":
    target_ip = "112.28.228.67:35528"  # Google DNS
    if check_proxy(target_ip, 2):
        print(f"{target_ip} 可以访问")
    else:
        print(f"{target_ip} 无法访问")
